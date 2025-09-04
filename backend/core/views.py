from datetime import date, datetime, timedelta
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from django.utils import timezone
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Room, Attendance, Complaint, Payment, Feedback, RoomAllocation, 
    Notice, MaintenanceRequest
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, RoomSerializer,
    AttendanceSerializer, ComplaintSerializer, PaymentSerializer,
    FeedbackSerializer, RoomAllocationSerializer, NoticeSerializer,
    MaintenanceRequestSerializer, DashboardStatsSerializer
)
from .permissions import IsAdmin, IsStudent, IsWarden


User = get_user_model()


class UserRegistrationView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.role == "student":
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="students")
    def students(self, request):
        students = User.objects.filter(role="student")
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room_type', 'status', 'floor']
    search_fields = ['number', 'description']
    ordering_fields = ['number', 'monthly_rent', 'created_at']
    ordering = ['number']

    @action(detail=False, methods=["get"], url_path="available")
    def available_rooms(self, request):
        available_rooms = Room.objects.filter(status='available')
        serializer = self.get_serializer(available_rooms, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="stats")
    def room_stats(self, request):
        total_rooms = Room.objects.count()
        available_rooms = Room.objects.filter(status='available').count()
        occupied_rooms = Room.objects.filter(status='occupied').count()
        maintenance_rooms = Room.objects.filter(status='maintenance').count()
        
        return Response({
            'total_rooms': total_rooms,
            'available_rooms': available_rooms,
            'occupied_rooms': occupied_rooms,
            'maintenance_rooms': maintenance_rooms,
            'occupancy_rate': round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 2)
        })


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().select_related("user")
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date', 'present']
    ordering_fields = ['date', 'marked_at']
    ordering = ['-date']

    def get_queryset(self):
        if self.request.user.role == "student":
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsStudent])
    def mark(self, request):
        today = date.today()
        attendance, created = Attendance.objects.get_or_create(
            user=request.user, date=today, defaults={"present": True}
        )
        serializer = self.get_serializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="stats")
    def attendance_stats(self, request):
        user = request.user if request.user.role == "student" else None
        queryset = self.get_queryset()
        
        if user:
            total_days = queryset.count()
            present_days = queryset.filter(present=True).count()
            attendance_rate = round((present_days / total_days * 100) if total_days > 0 else 0, 2)
            
            return Response({
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': total_days - present_days,
                'attendance_rate': attendance_rate
            })
        
        # Admin/warden view
        total_attendance = queryset.count()
        present_attendance = queryset.filter(present=True).count()
        
        return Response({
            'total_attendance': total_attendance,
            'present_attendance': present_attendance,
            'absent_attendance': total_attendance - present_attendance,
            'overall_attendance_rate': round((present_attendance / total_attendance * 100) if total_attendance > 0 else 0, 2)
        })


class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all().select_related("user", "room")
    serializer_class = ComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'room']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.role == "student":
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsWarden])
    def update_status(self, request, pk=None):
        complaint = self.get_object()
        new_status = request.data.get('status')
        if new_status in ['open', 'in_progress', 'resolved']:
            complaint.status = new_status
            complaint.save()
            serializer = self.get_serializer(complaint)
            return Response(serializer.data)
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().select_related("user")
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_type']
    ordering_fields = ['created_at', 'amount', 'due_date']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.role == "student":
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    @action(detail=False, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsStudent])
    def create_order(self, request):
        amount = request.data.get("amount")
        payment_type = request.data.get("payment_type", "rent")
        description = request.data.get("description", "")
        
        payment = Payment.objects.create(
            user=request.user, 
            amount=amount,
            payment_type=payment_type,
            description=description
        )
        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="pending")
    def pending_payments(self, request):
        pending = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="stats")
    def payment_stats(self, request):
        queryset = self.get_queryset()
        total_amount = queryset.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0
        pending_amount = queryset.filter(status='pending').aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            'total_collected': total_amount,
            'pending_amount': pending_amount,
            'total_transactions': queryset.count(),
            'successful_transactions': queryset.filter(status='success').count(),
            'pending_transactions': queryset.filter(status='pending').count()
        })


class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all().select_related("user")
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.role == "student":
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="stats")
    def feedback_stats(self, request):
        queryset = self.get_queryset()
        total_feedback = queryset.count()
        avg_rating = queryset.aggregate(avg_rating=models.Avg('rating'))['avg_rating'] or 0
        
        rating_distribution = {}
        for i in range(1, 6):
            rating_distribution[f'{i}_star'] = queryset.filter(rating=i).count()
        
        return Response({
            'total_feedback': total_feedback,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': rating_distribution
        })


class RoomAllocationViewSet(viewsets.ModelViewSet):
    queryset = RoomAllocation.objects.all().select_related("user", "room")
    serializer_class = RoomAllocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'room']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']

    @action(detail=False, methods=["get"], url_path="active")
    def active_allocations(self, request):
        active = self.queryset.filter(status='active')
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.all().select_related("created_by")
    serializer_class = NoticeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'target_audience', 'is_active']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        user_role = self.request.user.role
        return self.queryset.filter(
            Q(target_audience=user_role) | Q(target_audience='all'),
            is_active=True
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRequest.objects.all().select_related("user", "room", "assigned_to")
    serializer_class = MaintenanceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'room']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.role == "student":
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["patch"], permission_classes=[permissions.IsAuthenticated, IsWarden])
    def assign(self, request, pk=None):
        maintenance = self.get_object()
        assigned_to_id = request.data.get('assigned_to')
        if assigned_to_id:
            try:
                assigned_user = User.objects.get(id=assigned_to_id)
                maintenance.assigned_to = assigned_user
                maintenance.status = 'in_progress'
                maintenance.save()
                serializer = self.get_serializer(maintenance)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'assigned_to is required'}, status=status.HTTP_400_BAD_REQUEST)


class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from django.db import models
        
        # Basic stats
        total_students = User.objects.filter(role='student').count()
        total_rooms = Room.objects.count()
        occupied_rooms = RoomAllocation.objects.filter(status='active').values('room').distinct().count()
        available_rooms = total_rooms - occupied_rooms
        
        # Payment stats
        pending_payments = Payment.objects.filter(status='pending').count()
        monthly_revenue = Payment.objects.filter(
            status='success',
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Complaint and maintenance stats
        pending_complaints = Complaint.objects.filter(status='open').count()
        pending_maintenance = MaintenanceRequest.objects.filter(status='pending').count()
        
        stats = {
            'total_students': total_students,
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'available_rooms': available_rooms,
            'pending_payments': pending_payments,
            'pending_complaints': pending_complaints,
            'pending_maintenance': pending_maintenance,
            'monthly_revenue': monthly_revenue
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)


