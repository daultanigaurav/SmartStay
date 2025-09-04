from django.contrib import admin
from .models import User, Room, Attendance, Complaint, Payment, Feedback, RoomAllocation


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role")
    search_fields = ("username", "email")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("number", "capacity", "floor")
    search_fields = ("number",)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "present", "marked_at")
    list_filter = ("present",)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "status", "created_at")
    list_filter = ("status",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "status", "provider", "created_at")
    list_filter = ("status", "provider")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("user", "rating", "created_at")


@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display = ("user", "room", "start_date", "end_date")


