from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnnotationImageViewSet, PolygonViewSet

router = DefaultRouter()
router.register(r'images', AnnotationImageViewSet, basename='image')
router.register(r'polygons', PolygonViewSet, basename='polygon')

urlpatterns = [
    path('', include(router.urls)),
]
