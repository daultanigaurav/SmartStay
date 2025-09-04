from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserRegistrationView, UserViewSet, RoomViewSet, AttendanceViewSet,
    ComplaintViewSet, PaymentViewSet, FeedbackViewSet, RoomAllocationViewSet,
    NoticeViewSet, MaintenanceRequestViewSet, DashboardStatsView
)
# from .views_enhanced import (
#     AdvancedUserViewSet, AdvancedRoomViewSet, DocumentViewSet, VisitorViewSet,
#     EventViewSet, AuditLogViewSet, AdvancedDashboardStatsView, DataExportView, SearchView
# )

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

# Enhanced API endpoints (temporarily disabled)
# router.register(r"advanced/users", AdvancedUserViewSet, basename="advanced-user")
# router.register(r"advanced/rooms", AdvancedRoomViewSet, basename="advanced-room")
# router.register(r"documents", DocumentViewSet)
# router.register(r"visitors", VisitorViewSet)
# router.register(r"events", EventViewSet)
# router.register(r"audit-logs", AuditLogViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
    path("dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    # path("dashboard/advanced-stats/", AdvancedDashboardStatsView.as_view(), name="advanced-dashboard-stats"),
    # path("export/", DataExportView.as_view(), name="data-export"),
    # path("search/", SearchView.as_view(), name="search"),
]


