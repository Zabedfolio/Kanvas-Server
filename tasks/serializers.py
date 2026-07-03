from rest_framework import serializers
from .models import Task, Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    tag_names = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = [
            'id', 'user', 'title', 'description', 'priority', 
            'status', 'due_date', 'tags', 'tag_names', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'tags', 'created_at', 'updated_at']

    def create(self, validated_data):
        tag_names = validated_data.pop('tag_names', [])
        # user will be injected by ViewSet perform_create
        task = Task.objects.create(**validated_data)
        
        for name in tag_names:
            name_cleaned = name.strip()
            if name_cleaned:
                tag, _ = Tag.objects.get_or_create(name=name_cleaned)
                task.tags.add(tag)
                
        return task

    def update(self, instance, validated_data):
        tag_names = validated_data.pop('tag_names', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tag_names is not None:
            instance.tags.clear()
            for name in tag_names:
                name_cleaned = name.strip()
                if name_cleaned:
                    tag, _ = Tag.objects.get_or_create(name=name_cleaned)
                    instance.tags.add(tag)

        return instance
