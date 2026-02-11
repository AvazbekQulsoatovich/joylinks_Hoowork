from rest_framework import serializers
from django.contrib.auth import get_user_model
from academy.models import Course, Group
from homeworks.models import Homework, Submission

User = get_user_model()


# ==================== USER SERIALIZERS ====================
class UserListSerializer(serializers.ModelSerializer):
    """Minimal user data for lists"""
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'role', 'is_active')
        read_only_fields = ('id',)


class UserDetailSerializer(serializers.ModelSerializer):
    """Full user details"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 
                  'phone', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
        read_only_fields = ('id', 'date_joined', 'is_staff', 'is_superuser')


class UserCreateSerializer(serializers.ModelSerializer):
    """User creation with password"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 
                  'first_name', 'last_name', 'role', 'phone')
    
    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({'password': "Passwords don't match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """User update (without password)"""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'role', 'is_active')


# ==================== COURSE SERIALIZERS ====================
class CourseListSerializer(serializers.ModelSerializer):
    """Course list view"""
    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'created_at')
        read_only_fields = ('id', 'created_at')


class CourseDetailSerializer(serializers.ModelSerializer):
    """Full course details with groups"""
    groups_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ('id', 'name', 'description', 'groups_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_groups_count(self, obj):
        return obj.groups.count()


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update course"""
    class Meta:
        model = Course
        fields = ('name', 'description')


# ==================== GROUP SERIALIZERS ====================
class GroupListSerializer(serializers.ModelSerializer):
    """Group list view"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Group
        fields = ('id', 'name', 'course', 'course_name', 'teacher', 'students_count', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def get_students_count(self, obj):
        return obj.students.count()


class GroupDetailSerializer(serializers.ModelSerializer):
    """Full group details with students and teacher"""
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    students = UserListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Group
        fields = ('id', 'name', 'course', 'course_name', 'teacher', 'teacher_name',
                  'students', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class GroupCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update group"""
    class Meta:
        model = Group
        fields = ('name', 'course', 'teacher')


# ==================== HOMEWORK SERIALIZERS ====================
class HomeworkListSerializer(serializers.ModelSerializer):
    """Homework list view"""
    group_name = serializers.CharField(source='group.name', read_only=True)
    submissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Homework
        fields = ('id', 'title', 'group', 'group_name', 'deadline', 'submissions_count', 'created_at')
        read_only_fields = ('id', 'created_at')
    
    def get_submissions_count(self, obj):
        return obj.submissions.count()


class HomeworkDetailSerializer(serializers.ModelSerializer):
    """Full homework details"""
    group_name = serializers.CharField(source='group.name', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Homework
        fields = ('id', 'title', 'description', 'group', 'group_name', 'deadline',
                  'code_language', 'file', 'file_url', 'options', 'sequence', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class HomeworkCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update homework"""
    class Meta:
        model = Homework
        fields = ('title', 'description', 'group', 'deadline', 'code_language', 'file', 'options', 'sequence')


# ==================== SUBMISSION SERIALIZERS ====================
class SubmissionListSerializer(serializers.ModelSerializer):
    """Submission list view"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    homework_title = serializers.CharField(source='homework.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = ('id', 'homework', 'homework_title', 'student', 'student_name',
                  'grade', 'status', 'submitted_at')
        read_only_fields = ('id', 'submitted_at')


class SubmissionDetailSerializer(serializers.ModelSerializer):
    """Full submission details"""
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    homework_title = serializers.CharField(source='homework.title', read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = ('id', 'homework', 'homework_title', 'student', 'student_name',
                  'text_answer', 'code_answer', 'file', 'file_url', 'grade',
                  'feedback', 'status', 'submitted_at', 'graded_at')
        read_only_fields = ('id', 'submitted_at', 'graded_at')
    
    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class SubmissionCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update submission"""
    class Meta:
        model = Submission
        fields = ('homework', 'text_answer', 'code_answer', 'file')


class SubmissionGradeSerializer(serializers.ModelSerializer):
    """Grade submission"""
    class Meta:
        model = Submission
        fields = ('grade', 'feedback', 'status')
