from rest_framework.routers import DefaultRouter

from .views import AttendanceRecordViewSet, StudentProfileViewSet

router = DefaultRouter()
router.register('students', StudentProfileViewSet, basename='student')
router.register('attendance', AttendanceRecordViewSet, basename='attendance')

urlpatterns = router.urls
