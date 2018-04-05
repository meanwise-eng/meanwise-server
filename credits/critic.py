import uuid
import hashlib
from meanwise_backend.eventsourced import (EventRepository, Command, EventSourced, Event,)


class Criticized(Event):
    pass


class Credits(EventSourced):

    @staticmethod
    def create(id):
        return Credits(id, [])

    def __init__(self, *args, **kwargs):
        self.critics = []
        self.overall_endorsements = 0
        self.skill_endorsements = {}
        self.critic_hashes = []
        super().__init__(*args, **kwargs)

    def add_critic(self, criticizer, post_id, rating, skill):
        critic_hash = self._get_hash(criticizer, post_id)
        if critic_hash in self.critic_hashes:
            raise Exception("User already criticized this post")

        skill_endorsements = 0
        if skill in self.skill_endorsements:
            skill_endorsements = self.skill_endorsements[skill]

        criticized = Criticized(self.id, {
            'criticizer': criticizer, 'post_id': post_id, 'rating': rating, 'skill':skill,
            'overall_endorsements': self.overall_endorsements,
            'skill_endorsements': skill_endorsements})
        return self._new([criticized])

    def _apply_Criticized(self, event: Criticized):
        self.overall_endorsements += event.data['rating']
        skill = event.data['skill']
        if skill not in self.skill_endorsements:
            self.skill_endorsements[skill] = 0
        self.skill_endorsements[skill] += event.data['rating']
        self.critics.append(event)
        self.critic_hashes.append(self._get_hash(event.data['criticizer'], event.data['post_id']))

    def _get_hash(self, criticizer, post_uuid):
        m = hashlib.sha256()
        m.update((str(criticizer) + str(post_uuid)).encode('utf-8'))
        return m.digest()


class CreditsRepository(EventRepository):

    stream_prefix = 'mw_credits_credits-'
    ar_class = Credits


@Command.create(repo=CreditsRepository)
def create_critic(criticizer, criticized, post_id, rating, skill, repo):
    try:
        credits = repo.get(criticized)
    except Exception:
        credits = Credits.create(criticized)
    credits = credits.add_critic(criticizer=criticizer, post_id=post_id, rating=rating, skill=skill)

    repo.save(credits)
