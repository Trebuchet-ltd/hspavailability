from django.urls import path, include
from rest_framework.routers import DefaultRouter

from doctor.views import AppointmentViewSet, DoctorScheduleViewSet, DoctorScheduleTemplateViewSet

router = DefaultRouter()
router.register(r'appointment', AppointmentViewSet)
router.register(r'doctor_schedule', DoctorScheduleViewSet)
router.register(r'doctor_schedule_template', DoctorScheduleTemplateViewSet)
urlpatterns = [path(r'', include(router.urls))]
