from django.apps import AppConfig


class InfluencersConfig(AppConfig):
    name = 'influencers'

    def ready(self):
        import influencers.signals
