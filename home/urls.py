from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MarkerApiViewSet, ReviewViewSet, SusViewSet, PatientViewSet, ImageViewSet

router = DefaultRouter()
router.register(r'marker', MarkerApiViewSet)
router.register(r'review', ReviewViewSet)
router.register(r'suspicious', SusViewSet)
router.register(r'patient', PatientViewSet)
router.register(r'image', ImageViewSet)

urlpatterns = [path(r'', include(router.urls))]
