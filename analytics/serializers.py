from rest_framework import serializers

from .models import SeenPost, SeenPostBatch


class SeenPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeenPost
        exclude = ('url', )


class SeenPostBatchSerializer(serializers.ModelSerializer):
    posts = SeenPostSerializer(many=True)

    class Meta:
        model = SeenPostBatch
        fields = ('url', 'datetime', 'posts')

    def create(self, validated_data):
        posts_data = validated_data.pop('posts')

        post_batch = SeenPostBatch.objects.get_or_create(url=validated_data["url"],datetime=validated_data["datetime"])[0]

        for post_data in posts_data:
            SeenPost.objects.create(url=post_batch, **post_data)

        return post_batch
