from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MarkerApiViewSet, ReviewViewSet, SusViewSet, PatientViewSet, ImageViewSet, LanguageApiViewSet, \
    BannerImageViewSet

router = DefaultRouter()
router.register(r'marker', MarkerApiViewSet)
router.register(r'review', ReviewViewSet)
router.register(r'suspicious', SusViewSet)
router.register(r'patient', PatientViewSet)
router.register(r'image', ImageViewSet)
router.register(r'language', LanguageApiViewSet)
router.register(r'banner', BannerImageViewSet)


urlpatterns = [path(r'', include(router.urls))]
