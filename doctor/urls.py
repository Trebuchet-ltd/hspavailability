from django.urls import path, include
from rest_framework.routers import DefaultRouter

from doctor.views import AppointmentViewSet, DoctorScheduleViewSet

router = DefaultRouter()
router.register(r'appointment', AppointmentViewSet)
router.register(r'doctor_schedule', DoctorScheduleViewSet)
urlpatterns = [path(r'', include(router.urls))]
