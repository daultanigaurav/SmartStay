from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import (
    Room, Attendance, Complaint, Payment, Feedback, RoomAllocation, 
    Notice, MaintenanceRequest
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
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'date_of_birth', 'address', 
            'emergency_contact', 'profile_picture', 'is_active', 
            'created_at', 'current_room'
        ]
        read_only_fields = ['id', 'created_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_current_room(self, obj):
        allocation = obj.allocations.filter(status='active').first()
        if allocation:
            return {
                'room_number': allocation.room.number,
                'room_type': allocation.room.room_type,
                'start_date': allocation.start_date
            }
        return None


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
    
    class Meta:
        model = Complaint
        fields = [
            'id', 'user', 'user_name', 'room', 'room_number', 'title', 
            'description', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']


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
        fields = ['id', 'user', 'user_name', 'rating', 'comments', 'created_at']
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
    
    class Meta:
        model = Notice
        fields = [
            'id', 'title', 'content', 'priority', 'target_audience',
            'is_active', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']


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


class DashboardStatsSerializer(serializers.Serializer):
    total_students = serializers.IntegerField()
    total_rooms = serializers.IntegerField()
    occupied_rooms = serializers.IntegerField()
    available_rooms = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    pending_complaints = serializers.IntegerField()
    pending_maintenance = serializers.IntegerField()
    monthly_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)


