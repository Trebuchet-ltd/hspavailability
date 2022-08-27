import django_filters
from django.contrib.auth.models import User
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.response import Response


# Create your views here.
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from doctor.serializers import PatientAppointmentSlotSerializer, DoctorScheduleSerializer
from internals.models import AppointmentSlots, DoctorSchedule


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = PatientAppointmentSlotSerializer
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = AppointmentSlots.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = {'day__doctor': ['exact'], }

    def get_queryset(self):
        return AppointmentSlots.objects.filter(booked_by=self.request.user)

    def destroy(self, request, pk=None):
        slot = get_object_or_404(self.queryset, pk=pk)
        slot.booked_by = None
        slot.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        slot = get_object_or_404(self.queryset, pk=self.request.data['id'])
        print(slot.booked_by)
        if slot.booked_by:
            return Response({"message": "Slot already booked"}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User.objects.all(), pk=self.request.data['patient']) if self.request.data[
            'patient'] else self.request.user
        user_booked = self.queryset.filter(booked_by=user, day=slot.day).exists()
        if user_booked:
            return Response({"message": "Already booked for the day"}, status=status.HTTP_400_BAD_REQUEST)
        slot.booked_by = user
        slot.save()
        serializer = self.get_serializer(slot)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


"""  def perform_create(self, serializer):
        start = self.request.data['start']
        end = self.request.data['end']
        date = self.request.data['date']
        doctor = self.request.data['doctor']
        patient = self.request.data['patient']
        try:
            print('hi')
            doc = Doctor.objects.get(id=doctor)
            print(doc.slots.all())
            slots = AvailableSlots.objects.get(date=date, start=start, end=end)
            tkn = Tokens.objects.get(user_id=patient)
            if doc.user:
                tkn.add_friend(doc.user)
            slots.booked = True
            slots.save()
            serializer.save()
        except Exception as e:
            raise e
"""


class DoctorScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorScheduleSerializer
    http_method_names = ['get', 'post', 'options', 'delete']
    permission_classes = [IsAuthenticated]
    queryset = DoctorSchedule.objects.all()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = {'date': ['lte', 'gte'], 'doctor': ['exact']}
