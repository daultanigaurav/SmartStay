from datetime import date, datetime, timedelta
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from .models import (
    Room, Attendance, Complaint, Payment, Feedback, RoomAllocation, 
    Notice, MaintenanceRequest, AuditLog, EmailNotification, 
    Document, Visitor, Event
)
from .serializers import (
    UserSerializer, UserRegistrationSerializer, RoomSerializer,
    AttendanceSerializer, ComplaintSerializer, PaymentSerializer,
    FeedbackSerializer, RoomAllocationSerializer, NoticeSerializer,
    MaintenanceRequestSerializer, AuditLogSerializer, EmailNotificationSerializer,
    DocumentSerializer, VisitorSerializer, EventSerializer, DashboardStatsSerializer
)
from .permissions import IsAdmin, IsStudent, IsWarden
from .utils import log_audit_action, send_notification_email


User = get_user_model()


class AdvancedUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'email_verified', 'phone_verified']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['created_at', 'username', 'last_login']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.role == "student":
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()

    def perform_create(self, serializer):
        user = serializer.save()
        log_audit_action(
            user=self.request.user,
            action='create',
            model_name='User',
            object_id=str(user.id),
            description=f'Created user: {user.username}',
            request=self.request
        )

    def perform_update(self, serializer):
        user = serializer.save()
        log_audit_action(
            user=self.request.user,
            action='update',
            model_name='User',
            object_id=str(user.id),
            description=f'Updated user: {user.username}',
            request=self.request
        )

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="students")
    def students(self, request):
        students = User.objects.filter(role="student")
        serializer = self.get_serializer(students, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def verify_email(self, request, pk=None):
        user = self.get_object()
        user.email_verified = True
        user.save()
        
        # Send verification email
        send_notification_email(
            user=user,
            subject="Email Verified",
            message="Your email has been successfully verified."
        )
        
        return Response({'message': 'Email verified successfully'})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def verify_phone(self, request, pk=None):
        user = self.get_object()
        user.phone_verified = True
        user.save()
        
        return Response({'message': 'Phone verified successfully'})

    @action(detail=False, methods=["get"], url_path="statistics")
    def user_statistics(self, request):
        total_users = User.objects.count()
        students = User.objects.filter(role='student').count()
        admins = User.objects.filter(role='admin').count()
        wardens = User.objects.filter(role='warden').count()
        active_users = User.objects.filter(is_active=True).count()
        verified_emails = User.objects.filter(email_verified=True).count()
        
        return Response({
            'total_users': total_users,
            'students': students,
            'admins': admins,
            'wardens': wardens,
            'active_users': active_users,
            'verified_emails': verified_emails,
            'verification_rate': round((verified_emails / total_users * 100) if total_users > 0 else 0, 2)
        })


class AdvancedRoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['room_type', 'status', 'floor']
    search_fields = ['number', 'description', 'amenities']
    ordering_fields = ['number', 'monthly_rent', 'created_at', 'floor']
    ordering = ['floor', 'number']

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
        
        # Room type distribution
        room_types = Room.objects.values('room_type').annotate(count=Count('id'))
        
        # Floor distribution
        floor_distribution = Room.objects.values('floor').annotate(count=Count('id'))
        
        return Response({
            'total_rooms': total_rooms,
            'available_rooms': available_rooms,
            'occupied_rooms': occupied_rooms,
            'maintenance_rooms': maintenance_rooms,
            'occupancy_rate': round((occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0, 2),
            'room_types': list(room_types),
            'floor_distribution': list(floor_distribution)
        })

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsWarden])
    def change_status(self, request, pk=None):
        room = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in ['available', 'occupied', 'maintenance']:
            old_status = room.status
            room.status = new_status
            room.save()
            
            log_audit_action(
                user=request.user,
                action='update',
                model_name='Room',
                object_id=str(room.id),
                description=f'Changed room {room.number} status from {old_status} to {new_status}',
                request=request
            )
            
            return Response({'message': f'Room status changed to {new_status}'})
        
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'is_verified']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'document_type']
    ordering = ['-created_at']

    def get_queryset(self):
        if self.request.user.role == "student":
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        document = serializer.save(user=self.request.user)
        log_audit_action(
            user=self.request.user,
            action='create',
            model_name='Document',
            object_id=str(document.id),
            description=f'Uploaded document: {document.title}',
            request=self.request
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsWarden])
    def verify(self, request, pk=None):
        document = self.get_object()
        document.is_verified = True
        document.verified_by = request.user
        document.verified_at = timezone.now()
        document.save()
        
        # Send notification to user
        send_notification_email(
            user=document.user,
            subject="Document Verified",
            message=f"Your document '{document.title}' has been verified."
        )
        
        return Response({'message': 'Document verified successfully'})


class VisitorViewSet(viewsets.ModelViewSet):
    queryset = Visitor.objects.all()
    serializer_class = VisitorSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'visit_date']
    search_fields = ['visitor_name', 'purpose']
    ordering_fields = ['visit_date', 'created_at']
    ordering = ['-visit_date']

    def get_queryset(self):
        if self.request.user.role == "student":
            return self.queryset.filter(student=self.request.user)
        return self.queryset

    def perform_create(self, serializer):
        visitor = serializer.save(student=self.request.user)
        log_audit_action(
            user=self.request.user,
            action='create',
            model_name='Visitor',
            object_id=str(visitor.id),
            description=f'Created visitor request for {visitor.visitor_name}',
            request=self.request
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsWarden])
    def approve(self, request, pk=None):
        visitor = self.get_object()
        visitor.status = 'approved'
        visitor.approved_by = request.user
        visitor.approved_at = timezone.now()
        visitor.save()
        
        # Send notification to student
        send_notification_email(
            user=visitor.student,
            subject="Visitor Request Approved",
            message=f"Your visitor request for {visitor.visitor_name} has been approved."
        )
        
        return Response({'message': 'Visitor request approved'})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsWarden])
    def reject(self, request, pk=None):
        visitor = self.get_object()
        visitor.status = 'rejected'
        visitor.approved_by = request.user
        visitor.approved_at = timezone.now()
        visitor.save()
        
        # Send notification to student
        send_notification_email(
            user=visitor.student,
            subject="Visitor Request Rejected",
            message=f"Your visitor request for {visitor.visitor_name} has been rejected."
        )
        
        return Response({'message': 'Visitor request rejected'})


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['event_type', 'is_public']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['start_date']

    def perform_create(self, serializer):
        event = serializer.save(organizer=self.request.user)
        log_audit_action(
            user=self.request.user,
            action='create',
            model_name='Event',
            object_id=str(event.id),
            description=f'Created event: {event.title}',
            request=self.request
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        event = self.get_object()
        if event.attendees.filter(id=request.user.id).exists():
            return Response({'message': 'Already joined this event'})
        
        event.attendees.add(request.user)
        return Response({'message': 'Successfully joined the event'})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def leave(self, request, pk=None):
        event = self.get_object()
        if not event.attendees.filter(id=request.user.id).exists():
            return Response({'message': 'Not joined this event'})
        
        event.attendees.remove(request.user)
        return Response({'message': 'Successfully left the event'})


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'model_name']
    search_fields = ['description', 'user__username']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class AdvancedDashboardStatsView(APIView):
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
        pending_visitors = Visitor.objects.filter(status='pending').count()
        
        # Feedback stats
        avg_rating = Feedback.objects.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0
        
        # Recent activities
        recent_activities = []
        
        # Recent payments
        recent_payments = Payment.objects.filter(status='success').order_by('-created_at')[:5]
        for payment in recent_payments:
            recent_activities.append({
                'type': 'payment',
                'description': f'{payment.user.get_full_name()} paid ₹{payment.amount}',
                'timestamp': payment.created_at,
                'user': payment.user.get_full_name()
            })
        
        # Recent complaints
        recent_complaints = Complaint.objects.order_by('-created_at')[:5]
        for complaint in recent_complaints:
            recent_activities.append({
                'type': 'complaint',
                'description': f'New complaint: {complaint.title}',
                'timestamp': complaint.created_at,
                'user': complaint.user.get_full_name()
            })
        
        # Recent visitors
        recent_visitors = Visitor.objects.filter(status='approved').order_by('-created_at')[:5]
        for visitor in recent_visitors:
            recent_activities.append({
                'type': 'visitor',
                'description': f'Visitor approved: {visitor.visitor_name}',
                'timestamp': visitor.approved_at or visitor.created_at,
                'user': visitor.student.get_full_name()
            })
        
        # Sort by timestamp
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_activities = recent_activities[:10]
        
        stats = {
            'total_students': total_students,
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'available_rooms': available_rooms,
            'pending_payments': pending_payments,
            'pending_complaints': pending_complaints,
            'pending_maintenance': pending_maintenance,
            'pending_visitors': pending_visitors,
            'monthly_revenue': monthly_revenue,
            'average_rating': round(avg_rating, 2),
            'recent_activities': recent_activities
        }
        
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)


class DataExportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        import csv
        from django.http import HttpResponse
        from django.db.models import Q
        
        export_type = request.GET.get('type', 'students')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{export_type}_export.csv"'
        
        writer = csv.writer(response)
        
        if export_type == 'students':
            writer.writerow(['ID', 'Username', 'Name', 'Email', 'Phone', 'Role', 'Created At'])
            students = User.objects.filter(role='student')
            for student in students:
                writer.writerow([
                    student.id, student.username, student.get_full_name(),
                    student.email, student.phone_number, student.role, student.created_at
                ])
        
        elif export_type == 'rooms':
            writer.writerow(['ID', 'Number', 'Type', 'Status', 'Floor', 'Rent', 'Created At'])
            rooms = Room.objects.all()
            for room in rooms:
                writer.writerow([
                    room.id, room.number, room.room_type, room.status,
                    room.floor, room.monthly_rent, room.created_at
                ])
        
        elif export_type == 'payments':
            writer.writerow(['ID', 'User', 'Amount', 'Type', 'Status', 'Date'])
            payments = Payment.objects.all()
            for payment in payments:
                writer.writerow([
                    payment.id, payment.user.get_full_name(), payment.amount,
                    payment.payment_type, payment.status, payment.created_at
                ])
        
        return response


class SearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.GET.get('q', '')
        if not query:
            return Response({'results': []})
        
        results = {
            'users': [],
            'rooms': [],
            'complaints': [],
            'notices': []
        }
        
        # Search users
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )[:5]
        
        for user in users:
            results['users'].append({
                'id': user.id,
                'name': user.get_full_name(),
                'username': user.username,
                'role': user.role,
                'type': 'user'
            })
        
        # Search rooms
        rooms = Room.objects.filter(
            Q(number__icontains=query) |
            Q(description__icontains=query)
        )[:5]
        
        for room in rooms:
            results['rooms'].append({
                'id': room.id,
                'number': room.number,
                'type': room.room_type,
                'status': room.status,
                'type': 'room'
            })
        
        # Search complaints
        complaints = Complaint.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )[:5]
        
        for complaint in complaints:
            results['complaints'].append({
                'id': complaint.id,
                'title': complaint.title,
                'status': complaint.status,
                'user': complaint.user.get_full_name(),
                'type': 'complaint'
            })
        
        # Search notices
        notices = Notice.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )[:5]
        
        for notice in notices:
            results['notices'].append({
                'id': notice.id,
                'title': notice.title,
                'priority': notice.priority,
                'type': 'notice'
            })
        
        return Response(results)


