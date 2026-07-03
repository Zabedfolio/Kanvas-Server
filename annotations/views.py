import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import AnnotationImage, Polygon
from .serializers import AnnotationImageSerializer, PolygonSerializer

def upload_to_imgbb(image_file):
    """
    Uploads an image file to ImgBB and returns the public URL.
    Returns None if IMGBB_API_KEY is not configured or if the upload fails.
    """
    if not getattr(settings, 'IMGBB_API_KEY', None):
        return None
    try:
        image_file.seek(0)  # Rewind file pointer
        url = "https://api.imgbb.com/1/upload"
        files = {
            'image': (image_file.name, image_file, image_file.content_type)
        }
        payload = {
            'key': settings.IMGBB_API_KEY
        }
        response = requests.post(url, data=payload, files=files, timeout=30)
        if response.status_code == 200:
            res_json = response.json()
            return res_json.get('data', {}).get('url')
        else:
            print(f"ImgBB upload failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Exception during ImgBB upload: {e}")
    return None


class AnnotationImageViewSet(viewsets.ModelViewSet):
    serializer_class = AnnotationImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Scope to logged-in user
        return AnnotationImage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        image_file = self.request.FILES.get('image')
        image_url = None
        
        if image_file:
            # Try uploading to ImgBB
            image_url = upload_to_imgbb(image_file)
            
        if image_url:
            # Successfully uploaded to ImgBB.
            # We save the image URL and can optionally skip saving the local file
            # to save disk space, or save both. Let's save only the URL to represent
            # remote cloud storage, but we can also write the file to media for reference.
            # To avoid saving locally if ImgBB succeeds, we instantiate the serializer 
            # with image_url and no local image.
            serializer.save(user=self.request.user, image_url=image_url, image=None)
        else:
            # Fallback to local storage (image_file is saved by default Django upload handler)
            serializer.save(user=self.request.user)

    @action(detail=True, methods=['get', 'post'], url_path='polygons')
    def polygons(self, request, pk=None):
        """
        GET  /api/images/:id/polygons/ - List all polygons for this image
        POST /api/images/:id/polygons/ - Create a polygon for this image
        """
        image = get_object_or_404(AnnotationImage, pk=pk, user=request.user)

        if request.method == 'GET':
            polygons = image.polygons.all()
            serializer = PolygonSerializer(polygons, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = PolygonSerializer(data=request.data)
            if serializer.is_valid():
                # Save polygon linked to the current image
                serializer.save(image=image)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PolygonViewSet(viewsets.GenericViewSet, mixins.DestroyModelMixin):
    """
    DELETE /api/polygons/:id/ - Delete a polygon by ID.
    Enforces security by only allowing users to delete polygons on their own images.
    """
    queryset = Polygon.objects.all()
    serializer_class = PolygonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Strict ownership check
        return Polygon.objects.filter(image__user=self.request.user)
