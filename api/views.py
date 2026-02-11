from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import get_user_model
from django.utils import timezone
from academy.models import Course, Group
from homeworks.models import Homework, Submission
from .serializers import (
    UserListSerializer, UserDetailSerializer, UserCreateSerializer, UserUpdateSerializer,
    CourseListSerializer, CourseDetailSerializer, CourseCreateUpdateSerializer,
    GroupListSerializer, GroupDetailSerializer, GroupCreateUpdateSerializer,
    HomeworkListSerializer, HomeworkDetailSerializer, HomeworkCreateUpdateSerializer,
    SubmissionListSerializer, SubmissionDetailSerializer, SubmissionCreateUpdateSerializer,
    SubmissionGradeSerializer
)
from .permissions import IsAdmin, IsTeacher, IsAdminOrReadOnly

User = get_user_model()


# ==================== USER VIEWSET ====================
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users
    - List: GET /api/v1/users/
    - Create: POST /api/v1/users/
    - Detail: GET /api/v1/users/{id}/
    - Update: PUT/PATCH /api/v1/users/{id}/
    - Delete: DELETE /api/v1/users/{id}/
    """
    queryset = User.objects.all()
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdmin]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserListSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = UserDetailSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_status(self, request, pk=None):
        """Toggle user active status"""
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        return Response({'status': 'user status updated', 'is_active': user.is_active})
    
    @action(detail=False, methods=['get'])
    def by_role(self, request):
        """Filter users by role"""
        role = request.query_params.get('role', None)
        if role:
            queryset = self.queryset.filter(role=role)
        else:
            queryset = self.queryset
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ==================== COURSE VIEWSET ====================
class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing courses
    - List: GET /api/v1/courses/
    - Create: POST /api/v1/courses/
    - Detail: GET /api/v1/courses/{id}/
    - Update: PUT/PATCH /api/v1/courses/{id}/
    - Delete: DELETE /api/v1/courses/{id}/
    """
    queryset = Course.objects.all()
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateUpdateSerializer
        return CourseListSerializer


# ==================== GROUP VIEWSET ====================
class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing groups
    - List: GET /api/v1/groups/
    - Create: POST /api/v1/groups/
    - Detail: GET /api/v1/groups/{id}/
    - Update: PUT/PATCH /api/v1/groups/{id}/
    - Delete: DELETE /api/v1/groups/{id}/
    """
    queryset = Group.objects.all()
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GroupDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return GroupCreateUpdateSerializer
        return GroupListSerializer
    
    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """Add student to group"""
        group = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = User.objects.get(id=student_id, role='STUDENT')
            group.students.add(student)
            return Response({'status': 'student added'})
        except User.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_student(self, request, pk=None):
        """Remove student from group"""
        group = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = User.objects.get(id=student_id)
            group.students.remove(student)
            return Response({'status': 'student removed'})
        except User.DoesNotExist:
            return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)


# ==================== HOMEWORK VIEWSET ====================
class HomeworkViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing homeworks
    - List: GET /api/v1/homeworks/
    - Create: POST /api/v1/homeworks/
    - Detail: GET /api/v1/homeworks/{id}/
    - Update: PUT/PATCH /api/v1/homeworks/{id}/
    - Delete: DELETE /api/v1/homeworks/{id}/
    """
    queryset = Homework.objects.all()
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HomeworkDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return HomeworkCreateUpdateSerializer
        return HomeworkListSerializer
    
    def get_queryset(self):
        """Filter homeworks by user role"""
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'STUDENT':
                # Students see only homeworks from their groups
                return Homework.objects.filter(group__students=user)
            elif user.role == 'TEACHER':
                # Teachers see only their group homeworks
                return Homework.objects.filter(group__teacher=user)
        return self.queryset.all()
    
    @action(detail=True, methods=['post'])
    def extend_deadline(self, request, pk=None):
        """Extend homework deadline"""
        homework = self.get_object()
        new_deadline = request.data.get('deadline')
        if new_deadline:
            homework.deadline = new_deadline
            homework.save()
            return Response({'status': 'deadline extended', 'deadline': homework.deadline})
        return Response({'error': 'deadline required'}, status=status.HTTP_400_BAD_REQUEST)


# ==================== SUBMISSION VIEWSET ====================
class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing submissions
    - List: GET /api/v1/submissions/
    - Create: POST /api/v1/submissions/
    - Detail: GET /api/v1/submissions/{id}/
    - Update: PUT/PATCH /api/v1/submissions/{id}/
    - Delete: DELETE /api/v1/submissions/{id}/
    """
    queryset = Submission.objects.all()
    authentication_classes = [JWTAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubmissionDetailSerializer
        elif self.action == 'grade':
            return SubmissionGradeSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SubmissionCreateUpdateSerializer
        return SubmissionListSerializer
    
    def get_queryset(self):
        """Filter submissions based on user role"""
        user = self.request.user
        if user.role == 'STUDENT':
            return Submission.objects.filter(student=user)
        elif user.role == 'TEACHER':
            return Submission.objects.filter(homework__group__teacher=user)
        return self.queryset.all()
    
    def perform_create(self, serializer):
        """Set student to current user"""
        serializer.save(student=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsTeacher])
    def grade(self, request, pk=None):
        """Grade submission (teacher only)"""
        submission = self.get_object()
        serializer = SubmissionGradeSerializer(submission, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(graded_at=timezone.now())
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_submissions(self, request):
        """Get current user's submissions"""
        submissions = Submission.objects.filter(student=request.user)
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending submissions (ungraded)"""
        submissions = self.get_queryset().filter(status='PENDING')
        serializer = self.get_serializer(submissions, many=True)
        return Response(serializer.data)
