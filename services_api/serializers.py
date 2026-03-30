import uuid

from rest_framework import serializers, viewsets

from accounts.models import ProgrammerUser
from categories.models import Type, Technology
from comments.models import Comment
from programmers.models import Programmer
from services.models import Service

import requests
from django.core.files.base import ContentFile



class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at']

class ProgrammerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammerUser
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)
    image_url = serializers.URLField(write_only=True, required=False)

    comments = CommentSerializer(many=True, read_only=True)

    programmer_info = ProgrammerSerializer(source='programmer', read_only=True)
    programmer = serializers.PrimaryKeyRelatedField(queryset=ProgrammerUser.objects.all(), write_only=True)

    type_info = TypeSerializer(source='type', read_only=True)
    type = serializers.PrimaryKeyRelatedField(queryset=Type.objects.all(), write_only=True)

    technologies_info = TechnologySerializer(source='technologies', read_only=True, many=True)
    technologies = serializers.PrimaryKeyRelatedField(queryset=Technology.objects.all(), write_only=True, many=True)



    class Meta:
        model = Service
        fields = ['name', 'programmer', 'programmer_info', 'description',
                  'image', 'image_url', 'type', 'type_info', 'technologies',
                  'technologies_info', 'min_price', 'max_price', 'comments']

    def _get_image_file(self, url):


        response = requests.get(url)
        response.raise_for_status()


        file_name = f"{uuid.uuid4()}.jpg"
        return ContentFile(response.content, name=file_name)

    def create(self, validated_data):
        url = validated_data.pop("image_url", None)

        if url:
            validated_data["image_url"] = self._get_image_file(url)

        return super().create(validated_data)

    def update(self, instance, validated_data):
        url = validated_data.pop("image_url", None)


        if url:
            validated_data["image"] = self._get_image_file(url)

        return super().update(instance, validated_data)
