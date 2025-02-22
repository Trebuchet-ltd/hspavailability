import django_filters
from django.shortcuts import get_object_or_404
# Create your views here.
from rest_framework import viewsets, generics, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from authentication.permissions import IsOwnerOrReadOnly
from home.models import Tokens
from internals.models import *
from internals.serializers import *
from maps import settings


def add_points(user, points):
    try:
        token = Tokens.objects.get(user=user)
        token.points += points
        token.save()
    except Tokens.DoesNotExist:
        pass


class Department_NameApiViewSet(viewsets.ModelViewSet, generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = DepartmentName.objects.all()
    serializer_class = DepartmentNameSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class Equipment_NameApiViewSet(viewsets.ModelViewSet, generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = EquipmentName.objects.all()
    serializer_class = EquipmentNameSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    filter_backends = [filters.SearchFilter]


class DepartmentApiViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Department.objects.all()
    serializer_class = GetDepartmentSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['hospital']


class EquipmentApiViewSet(viewsets.ModelViewSet, generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']


class FloorApiViewSet(viewsets.ModelViewSet, generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Floors.objects.all()
    serializer_class = GetFloorSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']


class BuildingApiViewSet(viewsets.ModelViewSet, generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Building.objects.all()
    serializer_class = GetBuildingSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']


class DoctorApiViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = {'rating': ['gte'], 'experience': ['gte'], 'specialization': ['exact'], 'language': ['exact']}

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.save()
        add_points(request.user, settings.add_doctor_point)

        try:
            working_times = self.request.data["working_time"]
            print(working_times)
            for data in working_times:
                print(f"{data = }")
                hospital = data['hospital']
                print(f"{hospital = }")
                working_time_obj, _ = WorkingTime.objects.get_or_create(day=data["working_time"].get("day"),
                                                                        starting_time=data["working_time"].get(
                                                                            "starting_time"),
                                                                        ending_time=data["working_time"].get(
                                                                            "ending_time"))
                print(working_time_obj)
                hs = Markers.objects.get(id=hospital)
                HospitalWorkingTime.objects.get_or_create(working_time=working_time_obj,
                                                          hospital=hs, doctor=doctor)
        except Exception as e:
            print(e)
        return Response(self.serializer_class(doctor).data, status=201, )


class DoctorReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = DoctorReviews.objects.all()
    serializer_class = GetDoctorReviewSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def perform_create(self, serializer):
        user = self.request.user
        doctor = self.request.data["doctor"]
        rev = DoctorReviews.objects.filter(created_by=user, doctor=doctor).exists()
        add_points(self.request.user, settings.add_feedback_point)
        if rev:
            raise serializers.ValidationError({"detail": "Only One Review Allowed Per Doctor"})
        serializer.save(created_by=user)


class NurseApiViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Nurse.objects.all()
    serializer_class = NurseSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'delete']
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    search_fields = ['name']

    def perform_create(self, serializer):
        user = self.request.user
        add_points(user, settings.add_nurse_point)
        serializer.save()


class NurseReviewViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = NurseReviews.objects.all()
    serializer_class = GetNurseReviewSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def perform_create(self, serializer):
        user = self.request.user
        nurse = self.request.data["nurse"]
        rev = NurseReviews.objects.filter(created_by=user, nurse=nurse).exists()
        add_points(self.request.user, settings.add_feedback_point)
        if rev:
            raise serializers.ValidationError({"detail": "Only One Review Allowed Per Nurse"})
        serializer.save(created_by=user)


class AmbulanceApiViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def perform_create(self, serializer):
        user = self.request.user
        add_points(user, settings.add_ambulance_point)
        serializer.save()


class AmbulanceReviewApiSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = AmbulanceReviews.objects.all()
    serializer_class = GetAmbulanceReviewSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def perform_create(self, serializer):
        user = self.request.user
        ambulance = self.request.data["ambulance"]
        rev = AmbulanceReviews.objects.filter(created_by=user, ambulance=ambulance).exists()
        add_points(self.request.user, settings.add_feedback_point)
        if rev:
            raise serializers.ValidationError({"detail": "Only One Review Allowed Per Ambulance"})
        serializer.save(created_by=user)


class BloodTypeApiViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = BloodBank.objects.all()
    serializer_class = Blood_typeSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options', 'delete']

    def perform_create(self, serializer):
        user = self.request.user
        add_points(user, settings.add_blood_bank_point)
        serializer.save()


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
