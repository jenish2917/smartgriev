from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import ComplaintCategory, Department
from .serializers import ComplaintCategorySerializer, DepartmentSerializer

class CategoryListView(generics.ListAPIView):
    """
    List all active complaint categories
    """
    queryset = ComplaintCategory.objects.filter(is_active=True)
    serializer_class = ComplaintCategorySerializer
    permission_classes = [permissions.AllowAny]  # Public access
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'categories': serializer.data,
            'count': queryset.count()
        })

class DepartmentListView(generics.ListAPIView):
    """
    List all departments
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.AllowAny]  # Public access
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'departments': serializer.data,
            'count': queryset.count()
        })
