import datetime
import random
import string

from django.contrib.auth.models import User
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


# Create your models here.

rating = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
]

sizes = [
    (0, 'small'),
    (1, 'medium'),
    (2, 'large'),
]

gender = [
    ('M', 'male'),
    ('F', 'female'),
    ('NB', 'Non Binary'),
    ('NP', 'Prefer Not to Say')
]

bed = [
    (1, 'normal'),
    (2, 'ventilator'),
    (3, 'ICU')
]
category = [
    ('E', 'Economy'),
    ('N', 'Normal'),
    ('S', 'Speacialty'),
    ('SS', 'Super Specialty'),
    ('U', 'Uncategorized')
]

types = [
    ('H', 'Hospital'),
    ('P', 'Pharmacy'),
    ('C', 'Clinic'),
    ('W', 'Wellness Center'),
    ('U', 'Uncategorized')
]
ownership = [
    ('Pu', 'Public'),
    ('Pr', 'Private'),
    ('Co', 'Co-operative'),
    ('U', 'Uncategorized')
]
department = [
    'Cardiology'
    'Community Health'
    'Dermatology'
    'Endocrinology'
    'ENT'
    'Gastroenterology'
    'Gynaecology'
    'Nephrology'
    'Neurology'
    'Oncology'
    'Radiology'
    'Orthopaedics'
    'Pathology'
    'Pediatrics'
    'Pulmonology'
    'Rheumatology'
    'Venerology'
    'Dietician'
    'Psychiatry'
    'General Physician'
    'Dental'
    'Ayurveda'
    'Homeopathy'
]

medicine = [
    ('Ay', 'Ayurveda'), ('Al', 'Allopathy'), ('Ho', 'Homeopathy')
]

type = [("M", "Medical"), ("B", "Blood"), ("F", "Food"), ("FI", "Financial"), ("O", "Other")]


class Markers(models.Model):
    name = models.CharField(max_length=500)
    Phone = models.CharField(max_length=100, blank=True, null=True)
    size = models.IntegerField(choices=sizes, default=0)
    financial_rating = models.FloatField(default=0)
    avg_cost = models.IntegerField(default=0)
    covid_rating = models.FloatField(default=0)
    beds_available = models.IntegerField(default=0)
    care_rating = models.FloatField(default=0)
    oxygen_rating = models.FloatField(default=0)
    ventilator_availability = models.FloatField(default=0)
    oxygen_availability = models.FloatField(default=0)
    icu_availability = models.FloatField(default=0)
    lat = models.FloatField()
    lng = models.FloatField()
    datef = models.DateField(default=datetime.date.today)
    place_id = models.CharField(max_length=60, default="")
    added_by = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    Suspicious = models.IntegerField(default=0)
    display_address = models.TextField(default="", max_length=3000, blank=True)
    address = models.JSONField(blank=True)
    location = models.PointField(srid=4326, verbose_name='Location')
    category = models.CharField(choices=category, default='U', max_length=2)
    type = models.CharField(choices=types, default='U', max_length=2)
    ownership = models.CharField(choices=ownership, default='U', max_length=2)
    pending_approval = models.BooleanField(default=False)
    video_call = models.CharField(max_length=1000, null=True, blank=True)
    about = models.TextField(default="")
    medicine = models.CharField(choices=medicine, max_length=50, default="Al")

    def __str__(self):
        return self.name


class Reviews(models.Model):
    marker = models.ForeignKey(Markers, related_name="comment", on_delete=models.CASCADE)
    total_rating = models.IntegerField(choices=rating, default=0)
    financial_rating = models.IntegerField(choices=rating, default=1)
    avg_cost = models.IntegerField(default=0)
    covid_rating = models.IntegerField(choices=rating, default=1)
    care_rating = models.IntegerField(choices=rating, default=1)
    oxygen_rating = models.IntegerField(choices=rating, default=1)
    beds_available = models.IntegerField(default=0)
    ventilator_availability = models.IntegerField(default=0)
    oxygen_availability = models.IntegerField(default=0)
    icu_availability = models.IntegerField(default=0)
    comment = models.TextField(blank=True, max_length=3000)
    datef = models.DateField(default=datetime.date.today)
    day = models.IntegerField(default=0)
    size = models.IntegerField(choices=sizes, default=0)
    written_by = models.ForeignKey(User, default=1, on_delete=models.CASCADE)

    def __str__(self):
        return self.written_by.username + ',' + self.marker.name


class SuspiciousMarking(models.Model):
    marker = models.ForeignKey(Markers, on_delete=models.CASCADE)
    comment = models.TextField(max_length=30000)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)
    datef = models.DateField(default=datetime.date.today)


class HelpRequest(models.Model):

    def attachment_size_validator(self, value):
        limit = 3 * 1024 * 1024
        if value.size > limit:
            raise ValidationError('File too large. Size should not exceed 3 MiB.')

    request_type = models.CharField(choices=type, null=True, blank=True, max_length=10)
    Name = models.CharField(max_length=40)
    age = models.IntegerField(default=0)
    gender = models.CharField(choices=gender, max_length=2)
    address = models.TextField(max_length=2048, default='', blank=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
    helped_by = models.ManyToManyField(User, blank=True, related_name='helping_users')
    reason = models.TextField(max_length=1024, blank=True)
    public = models.BooleanField(default=False)
    attachment = models.FileField(null=True, upload_to="patient_attachment", validators=[attachment_size_validator,
                                                                                         FileExtensionValidator(
                                                                                             allowed_extensions=['pdf',
                                                                                                                 'jpeg',
                                                                                                                 'png',
                                                                                                                 'jpg'])])


class HelpRequestMedical(HelpRequest):

    symptoms = models.TextField(max_length=2048, blank=True)
    symdays = models.DateField(blank=True, null=True)
    spo2 = models.IntegerField(default=0)
    oxy_bed = models.BooleanField(default=False)
    bedtype = models.IntegerField(choices=bed, default=0, blank=True, null=True)

    blood = models.CharField(max_length=4, blank=True, null=True)
    ct = models.BooleanField(default=False)
    covidresult = models.BooleanField(default=False)
    ctscore = models.TextField(max_length=20, blank=True, null=True)

    attendername = models.CharField(max_length=40, blank=True, null=True)
    attenderphone = models.CharField(max_length=20, blank=True, null=True)
    relation = models.CharField(max_length=30, blank=True, null=True)

    hospitalpref = models.CharField(max_length=300, blank=True, null=True)
    hospitalprefid = models.ForeignKey(Markers, related_name='hospital_preference', blank=True, null=True,
                                       on_delete=models.PROTECT)
    srfid = models.CharField(max_length=30, blank=True, null=True)
    bunum = models.CharField(max_length=40, blank=True, null=True)

    requirement = models.CharField(max_length=20, blank=True, null=True)


class HelpRequestFinancial(HelpRequest):
    account_holder = models.CharField(max_length=200, null=True, blank=True)
    account_no = models.CharField(max_length=25, null=True, blank=True)
    ifsc = models.CharField(max_length=20, null=True, blank=True)
    bank_name = models.CharField(max_length=30, null=True, blank=True)


class HelpRequestBlood(HelpRequest):
    blood = models.CharField(max_length=4, blank=True, null=True)


# class Patient(models.Model):
#
#
#     def attachment_size_validator(value):
#         limit = 3 * 1024 * 1024
#         if value.size > limit:
#             raise ValidationError('File too large. Size should not exceed 3 MiB.')
#
#     Name = models.CharField(max_length=40)
#     age = models.IntegerField(default=0)
#     gender = models.CharField(choices=gender, max_length=2)
#     address = models.TextField(max_length=2048, default='', blank=True)
#     mobile_number = models.CharField(max_length=15, blank=True, null=True)
#     symptoms = models.TextField(max_length=2048, blank=True)
#     symdays = models.DateField(blank=True, null=True)
#     spo2 = models.IntegerField(default=0)
#     oxy_bed = models.BooleanField(default=False)
#     bedtype = models.IntegerField(choices=bed, default=0, blank=True, null=True)
#
#     blood = models.CharField(max_length=4, blank=True, null=True)
#     ct = models.BooleanField(default=False)
#     covidresult = models.BooleanField(default=False)
#     ctscore = models.TextField(max_length=20, blank=True, null=True)
#
#     attendername = models.CharField(max_length=40, blank=True, null=True)
#     attenderphone = models.CharField(max_length=20, blank=True, null=True)
#     relation = models.CharField(max_length=30, blank=True, null=True)
#
#     hospitalpref = models.CharField(max_length=300, blank=True, null=True)
#     hospitalprefid = models.ForeignKey(Markers, related_name='hospital_preference', blank=True, null=True,
#                                        on_delete=models.PROTECT)
#     srfid = models.CharField(max_length=30, blank=True, null=True)
#     bunum = models.CharField(max_length=40, blank=True, null=True)
#
#     category = models.CharField(choices=category, default='U', max_length=2)#?
#     ownership = models.CharField(choices=ownership, default='U', max_length=2)#?
#
#     user = models.ForeignKey(User, default=1, on_delete=models.CASCADE)
#
#     helped_by = models.ForeignKey(User, blank=True, null=True, related_name='helping', on_delete=models.SET_NULL)
#     requirement = models.CharField(max_length=20, blank=True, null=True)
#     public = models.BooleanField(default=False)
#
#     request_type = models.CharField(choices=type, null=True, blank=True, max_length=10)
#     account_holder = models.CharField(max_length=200, null=True, blank=True)
#     account_no = models.CharField(max_length=25, null=True, blank=True)
#     ifsc = models.CharField(max_length=20, null=True, blank=True)
#     bank_name = models.CharField(max_length=30, null=True, blank=True)
#
#     reason = models.TextField(max_length=1024, blank=True)
#     attachment = models.FileField(null=True, upload_to="patient_attachment", validators=[attachment_size_validator, FileExtensionValidator(allowed_extensions=['pdf', 'jpeg', 'png', 'jpg'])])
#
#


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def create_new_id():
    not_unique = True
    unique_id = id_generator()
    while not_unique:
        unique_id = id_generator()
        if not Tokens.objects.filter(private_token=unique_id):
            not_unique = False
    return str(unique_id)


class Language(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Tokens(models.Model):
    user = models.OneToOneField(User, related_name='tokens', on_delete=models.CASCADE)
    private_token = models.CharField(max_length=10, unique=True, default=create_new_id)
    invited = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    reviews = models.IntegerField(default=0)
    reports = models.IntegerField(default=0)
    images = models.IntegerField(default=0)
    invite_token = models.CharField(max_length=10, blank=True, null=True)
    language = models.ManyToManyField(Language, related_name='spoken_language')
    profile = models.ImageField(upload_to="pic", null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    friends = models.ManyToManyField(User, null=True, blank=True, related_name='friends')
    last_seen = models.DateTimeField(blank=True, null=True)
    age = models.IntegerField(default=0)
    gender = models.CharField(choices=gender, max_length=2, blank=True, null=True)
    address = models.TextField(max_length=2048, default='', blank=True, null=True)
    blood = models.CharField(max_length=4, blank=True, null=True)

    def __str__(self):
        return self.user.username + self.private_token

    def add_friend(self, user):
        self.friends.add(user)
        user.tokens.friends.add(self.user)
        user.tokens.save()
        self.points += 5
        print(self.points)
        self.save()


    @property
    def two_layer_friends(self):
        return User.objects.filter(tokens__private_token=self.invite_token) \
               | User.objects.filter(tokens__invite_token=self.private_token)


class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notification', on_delete=models.CASCADE)
    text = models.TextField()
    heading = models.CharField(max_length=30)
    seen = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)


class BannerImage(models.Model):
    image = models.ImageField(upload_to="pic")
    description = models.CharField(max_length=50)
