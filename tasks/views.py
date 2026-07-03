from rest_framework import viewsets, permissions
from .models import Task, Tag
from .serializers import TaskSerializer, TagSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]

    # Tags are global in this setup but we can restrict creation/deletion if needed.
    # We will allow anyone authenticated to view/create.


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Enforce that users can only see their own tasks
        queryset = Task.objects.filter(user=self.request.user)
        
        # Filter by date query param if present
        date_param = self.request.query_params.get('date', None)
        if date_param:
            queryset = queryset.filter(due_date=date_param)
            
        return queryset

    def perform_create(self, serializer):
        # Inject the authenticated user
        serializer.save(user=self.request.user)
