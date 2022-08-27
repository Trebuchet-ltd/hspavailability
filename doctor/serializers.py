from rest_framework import serializers

from internals.models import AppointmentSlots, DoctorSchedule, Doctor, Appointment
from internals.serializers import GetDoctorReviewSerializer, HospitalWorkingTimeSerializer


class AppointmentSlotSerializer(serializers.ModelSerializer):
    booked = serializers.SerializerMethodField()
    class Meta:
        model = AppointmentSlots
        fields = ["id","start", "end", "booked"]
    
    def get_booked(self, AppointmentSlot):
        return False if AppointmentSlot.booked_by is None else True

    def validate(self, data):
        if(data['start'] >= data['end']):
            raise serializers.ValidationError({'start':"Start shouldn't be greater than end"})
        return data

class PatientAppointmentSlotSerializer(serializers.ModelSerializer):
    doctor = serializers.StringRelatedField(source='day.doctor.name',read_only='True')
    date = serializers.StringRelatedField(source='day.date', read_only='True')
    class Meta:
        model = AppointmentSlots
        fields = ["id","start", "end", "doctor","date"]

class DoctorScheduleSerializer(serializers.ModelSerializer):
    slots = AppointmentSlotSerializer(many=True)
    stats = serializers.SerializerMethodField()

    def create(self, validated_data):
        slots = validated_data.pop('slots')
        schedule = DoctorSchedule.objects.create(**validated_data) 
        AppointmentSlots.objects.bulk_create([AppointmentSlots(**slot,day=schedule) for slot in slots])
        return schedule

    def validate_slots(self, data):
        slot_len = len(data)
        for i in range(slot_len-1):
            for j in range(i+1,slot_len):
                if(data[i]['start'] > data[j]['end'] or data[i]['end'] < data[j]['start'] ):
                    continue
                raise serializers.ValidationError("time intersects")
        return data

    class Meta:
        model = DoctorSchedule
        fields = ["id","date","slots", "stats","doctor"]
        extra_kwargs = {
            'doctor': {'write_only':True}
        }
    def get_stats(self, doctorSchedule):
        appointments = AppointmentSlots.objects.filter(day=doctorSchedule.id)
        total = appointments.count()
        available = appointments.filter(booked_by__isnull=True).count()
        return {"total":total,"available":available} 



class DoctorSerializer(serializers.ModelSerializer):
    reviews = GetDoctorReviewSerializer(many=True, required=False, read_only=True)
    working_time = HospitalWorkingTimeSerializer(many=True, read_only=True)
    #ranges = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Doctor
        fields = ["id", 'name', 'phone_number', 'hospital', 'department', 'user', 'working_time',
                  'rating', 'patients', 'experience', 'specialization', "about", "reviews", "image", "whatsapp_number",
                  "email_id", 'ima_number']
        extra_kwargs = {
            'hospital': {'read_only': True},
            'user': {'required': False},

        }


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = [
            'doctor', 'date', 'approved', 'patient', 'start', 'end'
        ]
        extra_kwargs = {
            'approved': {'read_only': True},
        }
