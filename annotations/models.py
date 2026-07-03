from django.db import models
from django.conf import settings

class AnnotationImage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='annotation_images'
    )
    image = models.ImageField(upload_to='annotation_images/', null=True, blank=True)
    image_url = models.URLField(max_length=1000, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    @property
    def url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url
        return None

    def __str__(self):
        return f"Image {self.id} uploaded by {self.user.email}"


class Polygon(models.Model):
    image = models.ForeignKey(
        AnnotationImage,
        on_delete=models.CASCADE,
        related_name='polygons'
    )
    points = models.JSONField(help_text="List of coordinate objects, e.g., [{'x': 10, 'y': 20}, ...]")
    label = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Polygon {self.id} on Image {self.image.id}"
