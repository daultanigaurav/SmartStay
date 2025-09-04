from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, UserViewSet, RoomViewSet, AttendanceViewSet,
    ComplaintViewSet, PaymentViewSet, FeedbackViewSet, RoomAllocationViewSet,
    NoticeViewSet, MaintenanceRequestViewSet, DashboardStatsView
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"rooms", RoomViewSet)
router.register(r"attendance", AttendanceViewSet)
router.register(r"complaints", ComplaintViewSet)
router.register(r"payments", PaymentViewSet)
router.register(r"feedback", FeedbackViewSet)
router.register(r"allocations", RoomAllocationViewSet)
router.register(r"notices", NoticeViewSet)
router.register(r"maintenance", MaintenanceRequestViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
]


