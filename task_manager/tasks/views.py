from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .models import Task
from .serializers import TaskSerializer, UserSerializer
from .authentication import generate_token

class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = generate_token(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token = generate_token(user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token
        })

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']

    def get_queryset(self):
        user = self.request.user
        queryset = Task.objects.filter(user=user)
        
        completed = self.request.query_params.get('completed')
        if completed is not None:
            completed_bool = completed.lower() == 'true'
            queryset = queryset.filter(completed=completed_bool)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)
