from django.contrib import admin
from .models import AnnotationImage, Polygon


class PolygonInline(admin.TabularInline):
    """Show polygons directly inside the image detail view."""
    model       = Polygon
    extra       = 0
    readonly_fields = ('id', 'label', 'points', 'created_at')
    can_delete  = True


@admin.register(AnnotationImage)
class AnnotationImageAdmin(admin.ModelAdmin):
    list_display   = ('id', 'user', 'image_url', 'uploaded_at', 'polygon_count')
    search_fields  = ('user__email', 'image_url')
    ordering       = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)
    list_per_page  = 25
    inlines        = [PolygonInline]

    @admin.display(description='Annotations')
    def polygon_count(self, obj):
        return obj.polygons.count()


@admin.register(Polygon)
class PolygonAdmin(admin.ModelAdmin):
    list_display   = ('id', 'image', 'label', 'point_count', 'created_at')
    list_filter    = ('label',)
    search_fields  = ('label', 'image__id')
    ordering       = ('-created_at',)
    readonly_fields = ('created_at',)
    list_per_page  = 25

    @admin.display(description='# Points')
    def point_count(self, obj):
        return len(obj.points) if obj.points else 0
