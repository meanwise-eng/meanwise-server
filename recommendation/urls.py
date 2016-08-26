from django.conf.urls import url

from .views import profile_hit_recommendations, similar_profiles

urlpatterns = [
    url(r'^profiles/recommendations/$', profile_hit_recommendations,
        name='recomendation_profiles'),
    url(r'^profiles/similar/$', similar_profiles,
        name='recomendation_similar_profiles'),
]
