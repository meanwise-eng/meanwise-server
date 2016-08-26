from django.db.models import Q

from account_profile.models import Profile, Relation
from account_profile.constants import RelationType


def get_profile_hits_recommendations(profile):
    profiles = Profile.objects.exclude(Q(relation__relation_type=RelationType.FOLLOW) & Q(relation__source=profile) | Q(id=profile.id)).order_by('hit_count__hits')[:10]
    return profiles


def get_similar_profiles(profile, logged_in_profile):
    profiles = Profile.objects.exclude(id=profile.id).filter(skills__in=profile.skills.all())
    if logged_in_profile:
        profiles = profiles.exclude(Q(relation__relation_type=RelationType.FOLLOW) & Q(relation__source=logged_in_profile) | Q(id=logged_in_profile.id))
    return profiles.distinct()[:10]
