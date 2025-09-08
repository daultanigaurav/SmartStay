from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    Room, Attendance, Complaint, ComplaintComment, Payment, Feedback, RoomAllocation, 
    Notice, NoticeRead, MaintenanceRequest, AuditLog, EmailNotification, 
    Document, Visitor, Event
)


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm', 
            'first_name', 'last_name', 'phone_number', 'date_of_birth', 
            'address', 'emergency_contact', 'role'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    current_room = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    pending_visitors = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'date_of_birth', 'address', 
            'emergency_contact', 'profile_picture', 'is_active', 
            'email_verified', 'phone_verified', 'last_login_ip',
            'created_at', 'current_room', 'documents_count', 'pending_visitors'
        ]
        read_only_fields = ['id', 'created_at', 'last_login_ip']

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_current_room(self, obj):
        allocation = obj.allocations.filter(status='active').first()
        if allocation:
            return {
                'room_number': allocation.room.number,
                'room_type': allocation.room.room_type,
                'start_date': allocation.start_date
            }
        return None

    def get_documents_count(self, obj):
        return obj.documents.count()

    def get_pending_visitors(self, obj):
        return obj.visitors.filter(status='pending').count()


class RoomSerializer(serializers.ModelSerializer):
    current_occupancy = serializers.ReadOnlyField()
    is_available = serializers.ReadOnlyField()
    occupants = serializers.SerializerMethodField()
    
    class Meta:
        model = Room
        fields = [
            'id', 'number', 'capacity', 'floor', 'room_type', 'status',
            'monthly_rent', 'amenities', 'description', 'image',
            'current_occupancy', 'is_available', 'occupants',
            'created_at', 'updated_at'
        ]

    def get_occupants(self, obj):
        active_allocations = obj.allocations.filter(status='active')
        return [
            {
                'id': allocation.user.id,
                'name': f"{allocation.user.first_name} {allocation.user.last_name}".strip(),
                'start_date': allocation.start_date
            }
            for allocation in active_allocations
        ]


class AttendanceSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ['id', 'user', 'user_name', 'date', 'present', 'marked_at']
        read_only_fields = ['marked_at', 'user']


class ComplaintSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    room_number = serializers.CharField(source='room.number', read_only=True)
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Complaint
        fields = [
            'id', 'user', 'user_name', 'room', 'room_number', 'title', 
            'description', 'status', 'created_at', 'updated_at', 'comments'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_comments(self, obj):
        return ComplaintCommentSerializer(obj.comments.all().order_by('-created_at'), many=True).data


class ComplaintCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = ComplaintComment
        fields = ['id', 'user', 'user_name', 'message', 'created_at']
        read_only_fields = ['user', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_name', 'amount', 'currency', 'payment_type',
            'status', 'due_date', 'paid_date', 'description', 'created_at'
        ]
        read_only_fields = [
            'status', 'provider_order_id', 'provider_payment_id', 
            'provider_signature', 'paid_date'
        ]


class FeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'user', 'user_name', 'rating', 'comments', 'category', 
            'is_anonymous', 'created_at'
        ]
        read_only_fields = ['user', 'created_at']


class RoomAllocationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    room_number = serializers.CharField(source='room.number', read_only=True)
    room_type = serializers.CharField(source='room.room_type', read_only=True)
    
    class Meta:
        model = RoomAllocation
        fields = [
            'id', 'user', 'user_name', 'room', 'room_number', 'room_type',
            'start_date', 'end_date', 'status', 'monthly_rent', 
            'security_deposit', 'created_at', 'updated_at'
        ]


class NoticeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content', 'priority', 'target_audience',
            'is_active', 'created_by', 'created_by_name', 'created_at', 'updated_at', 'is_read'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_is_read(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return NoticeRead.objects.filter(notice=obj, user=request.user).exists()


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    room_number = serializers.CharField(source='room.number', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'user', 'user_name', 'room', 'room_number', 'title',
            'description', 'priority', 'status', 'assigned_to', 'assigned_to_name',
            'estimated_cost', 'actual_cost', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'action', 'model_name', 'object_id',
            'description', 'ip_address', 'user_agent', 'created_at'
        ]
        read_only_fields = ['created_at']


class EmailNotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = EmailNotification
        fields = [
            'id', 'user', 'user_name', 'subject', 'message', 'status',
            'sent_at', 'created_at'
        ]
        read_only_fields = ['status', 'sent_at', 'created_at']


class DocumentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    verified_by_name = serializers.CharField(source='verified_by.get_full_name', read_only=True)
    
    class Meta:
        model = Document
        fields = [
            'id', 'user', 'user_name', 'document_type', 'title', 'file',
            'description', 'is_verified', 'verified_by', 'verified_by_name',
            'verified_at', 'created_at'
        ]
        read_only_fields = ['is_verified', 'verified_by', 'verified_at', 'created_at']


class VisitorSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = Visitor
        fields = [
            'id', 'student', 'student_name', 'visitor_name', 'visitor_phone',
            'visitor_id_proof', 'purpose', 'visit_date', 'visit_time',
            'expected_duration', 'status', 'approved_by', 'approved_by_name',
            'approved_at', 'actual_entry_time', 'actual_exit_time', 'created_at'
        ]
        read_only_fields = ['approved_by', 'approved_at', 'actual_entry_time', 'actual_exit_time', 'created_at']


class EventSerializer(serializers.ModelSerializer):
    organizer_name = serializers.CharField(source='organizer.get_full_name', read_only=True)
    attendees_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'start_date', 'end_date',
            'location', 'organizer', 'organizer_name', 'attendees', 'attendees_count',
            'is_public', 'created_at', 'updated_at'
        ]
        read_only_fields = ['organizer', 'created_at', 'updated_at']

    def get_attendees_count(self, obj):
        return obj.attendees.count()


class DashboardStatsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_rooms = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    available_rooms = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    pending_complaints = serializers.IntegerField()
    pending_maintenance = serializers.IntegerField()
    pending_visitors = serializers.IntegerField()
    monthly_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)


