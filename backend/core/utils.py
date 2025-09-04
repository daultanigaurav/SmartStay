from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import AuditLog, EmailNotification
import logging

logger = logging.getLogger(__name__)


def log_audit_action(user, action, model_name, object_id=None, description="", request=None):
    """
    Log user actions for audit trail
    """
    try:
        ip_address = None
        user_agent = ""
        
        if request:
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception as e:
        logger.error(f"Failed to log audit action: {e}")


def get_client_ip(request):
    """
    Get client IP address from request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def send_notification_email(user, subject, message, template=None):
    """
    Send email notification to user
    """
    try:
        # Create notification record
        notification = EmailNotification.objects.create(
            user=user,
            subject=subject,
            message=message
        )
        
        # Send email if email settings are configured
        if hasattr(settings, 'EMAIL_HOST') and settings.EMAIL_HOST:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            notification.status = 'sent'
            notification.sent_at = timezone.now()
        else:
            notification.status = 'pending'
        
        notification.save()
        return True
        
    except Exception as e:
        logger.error(f"Failed to send notification email: {e}")
        if 'notification' in locals():
            notification.status = 'failed'
            notification.save()
        return False


def send_bulk_notification(users, subject, message):
    """
    Send bulk email notifications
    """
    success_count = 0
    for user in users:
        if send_notification_email(user, subject, message):
            success_count += 1
    
    return success_count


def generate_report_data(start_date, end_date, report_type):
    """
    Generate data for various reports
    """
    from .models import User, Room, Payment, Complaint, Attendance
    
    data = {}
    
    if report_type == 'financial':
        payments = Payment.objects.filter(
            created_at__date__range=[start_date, end_date]
        )
        
        data = {
            'total_revenue': payments.filter(status='success').aggregate(
                total=models.Sum('amount')
            )['total'] or 0,
            'pending_amount': payments.filter(status='pending').aggregate(
                total=models.Sum('amount')
            )['total'] or 0,
            'payment_breakdown': payments.values('payment_type').annotate(
                count=models.Count('id'),
                total=models.Sum('amount')
            )
        }
    
    elif report_type == 'occupancy':
        rooms = Room.objects.all()
        allocations = RoomAllocation.objects.filter(
            start_date__lte=end_date
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=start_date)
        )
        
        data = {
            'total_rooms': rooms.count(),
            'occupied_rooms': allocations.values('room').distinct().count(),
            'occupancy_rate': 0,  # Calculate percentage
            'room_type_breakdown': rooms.values('room_type').annotate(
                count=models.Count('id')
            )
        }
    
    elif report_type == 'attendance':
        attendance = Attendance.objects.filter(
            date__range=[start_date, end_date]
        )
        
        data = {
            'total_attendance': attendance.count(),
            'present_count': attendance.filter(present=True).count(),
            'absent_count': attendance.filter(present=False).count(),
            'attendance_rate': 0,  # Calculate percentage
            'daily_breakdown': attendance.values('date').annotate(
                present=models.Count('id', filter=models.Q(present=True)),
                absent=models.Count('id', filter=models.Q(present=False))
            )
        }
    
    return data


def validate_room_availability(room, start_date, end_date=None):
    """
    Validate if a room is available for the given date range
    """
    from .models import RoomAllocation
    
    if end_date is None:
        end_date = start_date
    
    conflicting_allocations = RoomAllocation.objects.filter(
        room=room,
        status='active',
        start_date__lte=end_date,
        models.Q(end_date__isnull=True) | models.Q(end_date__gte=start_date)
    )
    
    return conflicting_allocations.count() == 0


def calculate_rent_amount(room, start_date, end_date):
    """
    Calculate rent amount for a room allocation
    """
    from datetime import timedelta
    
    if end_date is None:
        # Monthly rent
        return room.monthly_rent
    
    # Calculate days
    days = (end_date - start_date).days + 1
    daily_rate = room.monthly_rent / 30  # Assuming 30 days per month
    
    return daily_rate * days


def get_user_statistics(user):
    """
    Get comprehensive statistics for a user
    """
    from .models import Payment, Complaint, Attendance, Feedback
    
    stats = {
        'payments': {
            'total': Payment.objects.filter(user=user).count(),
            'pending': Payment.objects.filter(user=user, status='pending').count(),
            'successful': Payment.objects.filter(user=user, status='success').count(),
            'total_amount': Payment.objects.filter(user=user, status='success').aggregate(
                total=models.Sum('amount')
            )['total'] or 0
        },
        'complaints': {
            'total': Complaint.objects.filter(user=user).count(),
            'open': Complaint.objects.filter(user=user, status='open').count(),
            'resolved': Complaint.objects.filter(user=user, status='resolved').count()
        },
        'attendance': {
            'total_days': Attendance.objects.filter(user=user).count(),
            'present_days': Attendance.objects.filter(user=user, present=True).count(),
            'attendance_rate': 0  # Calculate percentage
        },
        'feedback': {
            'total': Feedback.objects.filter(user=user).count(),
            'average_rating': Feedback.objects.filter(user=user).aggregate(
                avg=models.Avg('rating')
            )['avg'] or 0
        }
    }
    
    # Calculate attendance rate
    if stats['attendance']['total_days'] > 0:
        stats['attendance']['attendance_rate'] = round(
            (stats['attendance']['present_days'] / stats['attendance']['total_days']) * 100, 2
        )
    
    return stats


def backup_database():
    """
    Create a backup of the database
    """
    import os
    import subprocess
    from django.conf import settings
    
    try:
        # This is a simplified backup function
        # In production, you'd want to use proper database backup tools
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'backup_{timestamp}.json')
        
        # Export data to JSON (simplified approach)
        from django.core.management import call_command
        with open(backup_file, 'w') as f:
            call_command('dumpdata', stdout=f)
        
        return backup_file
        
    except Exception as e:
        logger.error(f"Failed to create database backup: {e}")
        return None


def cleanup_old_data():
    """
    Clean up old data to maintain database performance
    """
    from .models import AuditLog, EmailNotification
    
    try:
        # Delete audit logs older than 1 year
        cutoff_date = timezone.now() - timezone.timedelta(days=365)
        old_audit_logs = AuditLog.objects.filter(created_at__lt=cutoff_date)
        deleted_audit_logs = old_audit_logs.count()
        old_audit_logs.delete()
        
        # Delete sent email notifications older than 6 months
        cutoff_date = timezone.now() - timezone.timedelta(days=180)
        old_notifications = EmailNotification.objects.filter(
            status='sent',
            sent_at__lt=cutoff_date
        )
        deleted_notifications = old_notifications.count()
        old_notifications.delete()
        
        return {
            'deleted_audit_logs': deleted_audit_logs,
            'deleted_notifications': deleted_notifications
        }
        
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")
        return None
