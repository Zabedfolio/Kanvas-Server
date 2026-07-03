from django.contrib import admin
from .models import Task, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'created_at')
    search_fields = ('name',)
    ordering      = ('name',)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display   = ('id', 'title', 'user', 'status', 'priority', 'due_date', 'created_at')
    list_filter    = ('status', 'priority', 'due_date')
    search_fields  = ('title', 'description', 'user__email')
    ordering       = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
    list_per_page  = 25
