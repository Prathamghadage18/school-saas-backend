from rest_framework.routers import DefaultRouter

from .views import SchoolTenantViewSet

router = DefaultRouter()
router.register('tenants', SchoolTenantViewSet, basename='tenant')

urlpatterns = router.urls
