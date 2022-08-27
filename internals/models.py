from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from home.models import Markers, Reviews, Language

gender = [
    ('M', 'male'),
    ('F', 'female'),
    ('NB', 'Non Binary'),
    ('NP', 'Prefer Not to Say')
]
choices = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))


class EquipmentName(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class DepartmentName(models.Model):
    name = models.CharField(max_length=200)
    icon = models.ImageField(upload_to="pic", blank=True, null=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    name = models.CharField(max_length=200)
    floor_plan = models.ImageField(upload_to="building", blank=True)
    hospital = models.ForeignKey(Markers, related_name='buildings', on_delete=models.CASCADE)


class Floors(models.Model):
    number = models.IntegerField()
    building = models.ForeignKey(Building, related_name='floors', on_delete=models.CASCADE)


class Department(models.Model):
    name = models.ForeignKey(DepartmentName, on_delete=models.PROTECT)
    rating = models.FloatField(default=0)
    x = models.IntegerField(default=0)
    y = models.IntegerField(default=0)
    hospital = models.ForeignKey(Markers, related_name='departments', on_delete=models.CASCADE)
    floor = models.ForeignKey(Floors, null=True, blank=True, related_name='departments', on_delete=models.PROTECT)


class Equipment(models.Model):
    name = models.ForeignKey(EquipmentName, on_delete=models.PROTECT)
    department = models.ForeignKey(Department, related_name='equipment', on_delete=models.CASCADE)


class WorkingTime(models.Model):
    days = (
        (1, "monday"), (2, "tuesday"), (3, "Wednesday"), (4, "Thursday"), (5, "friday"), (6, "saturday"), (7, "sunday"))
    day = models.IntegerField(default=1, choices=days)
    starting_time = models.TimeField()
    ending_time = models.TimeField()


class HospitalWorkingTime(models.Model):
    working_time = models.ForeignKey(WorkingTime, on_delete=models.RESTRICT, blank=True, null=True)
    hospital = models.ForeignKey(Markers, on_delete=models.CASCADE, blank=True, null=True)
    doctor = models.ForeignKey("Doctor", on_delete=models.CASCADE, related_name="working_time")


class Doctor(models.Model):
    days = []
    name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=14)

    whatsapp_number = models.CharField(max_length=14, null=True, blank=True)
    email_id = models.EmailField(max_length=254, blank=True, null=True)

    hospital = models.ManyToManyField(Markers, related_name='doctors', through=HospitalWorkingTime)
    department = models.ManyToManyField(Department, related_name='doctors', blank=True, null=True)
    user = models.OneToOneField(User, related_name='doctor', on_delete=models.PROTECT, default=None, null=True,
                                blank=True)

    ima_number = models.CharField(max_length=30, blank=True, null=True)

    about = models.TextField(blank=True, null=True, max_length=1000)
    rating = models.FloatField(default=0)
    patients = models.PositiveIntegerField(default=0)
    experience = models.PositiveIntegerField(default=0)
    specialization = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to="pic", null=True, blank=True)
    language = models.ManyToManyField(Language, related_name='doctor')

    # qualification =

    def __str__(self):
        return f"Dr: {self.name}"

    def get_slot_range(self):
        days = sorted(list(set([slot.date for slot in self.slots.all()])))
        if len(days):
            day = days[0]
            for i in range(1, len(days)):
                if abs(day.day - days[i].day) > 2:
                    pass


class DoctorSchedule(models.Model):
    class Meta:
        unique_together = ('doctor', 'date')

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="doctor")
    date = models.DateField()

    def __str__(self):
        return self.date.strftime('%d/%m/%Y') + " " + self.doctor.name


class AppointmentSlots(models.Model):
    day = models.ForeignKey(DoctorSchedule, on_delete=models.SET_NULL, related_name="slots")
    start = models.TimeField()
    end = models.TimeField()
    booked_by = models.ForeignKey(User, related_name="booked_user", on_delete=models.CASCADE, null=True)


class DoctorReviews(models.Model):
    content = models.TextField(max_length=3000)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="doctor_reviews")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=choices, default=0)


class Images(models.Model):
    image = models.ImageField(upload_to="pic", blank=True)
    review = models.ForeignKey(Reviews, default=None, null=True, blank=True, related_name='images',
                               on_delete=models.PROTECT)
    hospital = models.ForeignKey(Markers, related_name='images', on_delete=models.CASCADE, null=True, blank=True)
    department = models.ForeignKey(Department, related_name='images', on_delete=models.PROTECT, default=None, null=True,
                                   blank=True)
    equipment = models.ForeignKey(Equipment, related_name='images', on_delete=models.PROTECT, default=None, null=True,
                                  blank=True)
    useinmarker = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='uploaded_images', blank=True, null=True)


class Nurse(models.Model):
    name = models.CharField(max_length=30)
    gender = models.CharField(choices=gender, max_length=2)
    hospital = models.ForeignKey(Markers, on_delete=models.SET_NULL, blank=True, null=True, related_name='nurse')
    experience = models.PositiveIntegerField(default=0)
    patients = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="pic", null=True, blank=True)
    user = models.OneToOneField(User, related_name='nurse', on_delete=models.PROTECT, default=None, null=True,
                                blank=True)
    rating = models.FloatField(default=0)
    home_care = models.BooleanField(default=False)
    about = models.TextField(blank=True, null=True, max_length=1000)
    phone_number = models.CharField(max_length=14)
    review = models.ForeignKey(Reviews, default=None, null=True, blank=True, related_name='nurse',
                               on_delete=models.PROTECT)

    whats_app = models.IntegerField(max_length=10, blank=True, null=True)
    services = models.IntegerField(max_length=50, blank=True, null=True)
    availability = models.BooleanField(default=False)


class NurseReviews(models.Model):
    content = models.TextField(max_length=3000)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="nurse_reviews")
    nurse = models.ForeignKey(Nurse, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=choices, default=1)


class Ambulance(models.Model):
    choices = ((1, 1), (2, 2), (3, 3), (4, 4), (5, 5))
    name = models.CharField(max_length=30, blank=True, null=True)
    driver_name = models.CharField(max_length=30)
    hospital = models.ForeignKey(Markers, on_delete=models.SET_NULL, blank=True, null=True, related_name='ambulance')
    phone_number = models.CharField(max_length=14)
    image = models.ImageField(upload_to="pic", null=True, blank=True)
    rating = models.PositiveIntegerField(choices=choices, default=0)

    def __str__(self):
        return self.name


class AmbulanceReviews(models.Model):
    content = models.TextField(max_length=3000)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="ambulance_reviews")
    ambulance = models.ForeignKey(Ambulance, on_delete=models.CASCADE, related_name="ambulance_reviews")
    rating = models.IntegerField(choices=choices, default=1)

    def __str__(self):
        return f'{self.ambulance.name} review by {self.created_by.first_name}'


class BloodBank(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    hospital = models.ForeignKey(Markers, on_delete=models.SET_NULL, blank=True, null=True, related_name='blood_bank')
    rating = models.FloatField()
    blood_avail_Bpos = models.FloatField(blank=True, null=True)
    blood_avail_Apos = models.FloatField(blank=True, null=True)
    blood_avail_ABpos = models.FloatField(blank=True, null=True)
    blood_avail_Opos = models.FloatField(blank=True, null=True)
    blood_avail_Bneg = models.FloatField(blank=True, null=True)
    blood_avail_Aneg = models.FloatField(blank=True, null=True)
    blood_avail_ABneg = models.FloatField(blank=True, null=True)
    blood_avail_Oneg = models.FloatField(blank=True, null=True)


class Appointment(models.Model):
    """Contains info about appointment"""

    class Meta:
        unique_together = ('doctor', 'date',)

    doctor = models.ForeignKey(Doctor, related_name="appointment", on_delete=models.CASCADE)
    date = models.DateField(help_text="YYYY-MM-DD")
    approved = models.BooleanField(default=False)
    patient = models.ForeignKey(User, related_name="appointment_user", on_delete=models.CASCADE)
    start = models.TimeField()
    end = models.TimeField()

    # def __str__(self):
    #     return '{} {} {}. Patient: {}'.format(self.date, self.time, self.doctor, self.patient)

    # @property
    # def time(self):
    #     return self.TIMESLOT_LIST[self.timeslot][1]
