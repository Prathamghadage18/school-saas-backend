from rest_framework.routers import DefaultRouter

from .views import TeacherProfileViewSet, TimetableEntryViewSet

router = DefaultRouter()
router.register('teachers', TeacherProfileViewSet, basename='teacher')
router.register('timetable', TimetableEntryViewSet, basename='timetable')

urlpatterns = router.urls
