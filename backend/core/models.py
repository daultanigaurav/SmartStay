from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator
import uuid


class User(AbstractUser):
    class Roles(models.TextChoices):
        STUDENT = "student", "Student"
        ADMIN = "admin", "Admin"
        WARDEN = "warden", "Warden"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.STUDENT)
    phone_number = models.CharField(max_length=20, blank=True, validators=[MinLengthValidator(10)])
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name or self.username


class Room(models.Model):
    class RoomType(models.TextChoices):
        SINGLE = "single", "Single"
        DOUBLE = "double", "Double"
        TRIPLE = "triple", "Triple"
        QUAD = "quad", "Quad"

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        OCCUPIED = "occupied", "Occupied"
        MAINTENANCE = "maintenance", "Under Maintenance"

    number = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField(default=1)
    floor = models.PositiveIntegerField(default=1)
    room_type = models.CharField(max_length=20, choices=RoomType.choices, default=RoomType.SINGLE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amenities = models.TextField(blank=True, help_text="Comma-separated list of amenities")
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='rooms/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self) -> str:
        return f"Room {self.number} ({self.room_type.title()})"
    
    @property
    def current_occupancy(self):
        return self.allocations.filter(end_date__isnull=True).count()
    
    @property
    def is_available(self):
        return self.current_occupancy < self.capacity


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField()
    present = models.BooleanField(default=True)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "date")


class Complaint(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complaints")
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ComplaintComment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complaint_comments")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    class PaymentType(models.TextChoices):
        RENT = "rent", "Monthly Rent"
        SECURITY = "security", "Security Deposit"
        MAINTENANCE = "maintenance", "Maintenance Fee"
        PENALTY = "penalty", "Penalty"
        OTHER = "other", "Other"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")
    payment_type = models.CharField(max_length=20, choices=PaymentType.choices, default=PaymentType.RENT)
    provider = models.CharField(max_length=20, default="razorpay")
    provider_order_id = models.CharField(max_length=100, blank=True)
    provider_payment_id = models.CharField(max_length=100, blank=True)
    provider_signature = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField(null=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedbacks")
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comments = models.TextField(blank=True)
    category = models.CharField(max_length=50, default="general", choices=[
        ("general", "General"),
        ("facilities", "Facilities"),
        ("staff", "Staff"),
        ("food", "Food"),
        ("security", "Security"),
        ("maintenance", "Maintenance")
    ])
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class RoomAllocation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        TERMINATED = "terminated", "Terminated"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="allocations")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="allocations")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        unique_together = ("user", "room", "start_date")


class Notice(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    target_audience = models.CharField(max_length=20, choices=User.Roles.choices, default=User.Roles.STUDENT)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_notices")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class NoticeRead(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name="reads")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notice_reads")
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("notice", "user")


class MaintenanceRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="maintenance_requests")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="maintenance_requests")
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_maintenance")
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"
        DELETE = "delete", "Delete"
        LOGIN = "login", "Login"
        LOGOUT = "logout", "Logout"
        PAYMENT = "payment", "Payment"
        ALLOCATION = "allocation", "Room Allocation"

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EmailNotification(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Document(models.Model):
    class DocumentType(models.TextChoices):
        ID_PROOF = "id_proof", "ID Proof"
        ADDRESS_PROOF = "address_proof", "Address Proof"
        FEE_RECEIPT = "fee_receipt", "Fee Receipt"
        AGREEMENT = "agreement", "Room Agreement"
        OTHER = "other", "Other"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=20, choices=DocumentType.choices)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="verified_documents")
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Visitor(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        COMPLETED = "completed", "Completed"

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visitors")
    visitor_name = models.CharField(max_length=100)
    visitor_phone = models.CharField(max_length=20)
    visitor_id_proof = models.CharField(max_length=50)
    purpose = models.TextField()
    visit_date = models.DateField()
    visit_time = models.TimeField()
    expected_duration = models.PositiveIntegerField(help_text="Duration in hours")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_visitors")
    approved_at = models.DateTimeField(null=True, blank=True)
    actual_entry_time = models.DateTimeField(null=True, blank=True)
    actual_exit_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Event(models.Model):
    class EventType(models.TextChoices):
        MEETING = "meeting", "Meeting"
        CELEBRATION = "celebration", "Celebration"
        MAINTENANCE = "maintenance", "Maintenance"
        INSPECTION = "inspection", "Inspection"
        OTHER = "other", "Other"

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EventType.choices)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    attendees = models.ManyToManyField(User, related_name="attended_events", blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


