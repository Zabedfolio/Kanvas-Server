from rest_framework import serializers
from .models import AnnotationImage, Polygon

class PolygonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Polygon
        fields = ['id', 'image', 'points', 'label', 'created_at']
        read_only_fields = ['id', 'image', 'created_at']


class AnnotationImageSerializer(serializers.ModelSerializer):
    url = serializers.ReadOnlyField()

    class Meta:
        model = AnnotationImage
        fields = ['id', 'user', 'image', 'image_url', 'url', 'uploaded_at']
        read_only_fields = ['id', 'user', 'image_url', 'url', 'uploaded_at']
