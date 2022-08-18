from urllib import request
from rest_framework import serializers

from internals.serializers import GetImageSerializer, GetBuildingSerializer, DoctorSerializer, GetDepartmentSerializer
from .models import Markers, Reviews, SuspiciousMarking, HelpRequest, Tokens, Language, Notification, \
    BannerImage, bed, HelpRequestMedical

bed_names = {}
for i in bed:
    bed_names[i[0]] = i[1]


class GetMarkerSerializer(serializers.ModelSerializer):
    images = GetImageSerializer(many=True, required=False, read_only=True)
    comment_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Markers
        fields = [
            'id', 'name', 'Phone', 'size', 'financial_rating', 'avg_cost', 'covid_rating', 'beds_available',
            'care_rating', 'oxygen_rating', 'ventilator_availability', 'oxygen_availability', 'icu_availability',
            'lat', 'lng', 'datef', 'added_by_id', 'images', 'display_address', 'comment_count', 'address',
            'pending_approval', 'category', 'type', 'ownership', 'about',
        ]
        extra_kwargs = {
            'pending_approval': {'read_only': True},
            'size': {'read_only': True},
            'financial_rating': {'read_only': True},
            'avg_cost': {'read_only': True},
            'covid_rating': {'read_only': True},
            'beds_available': {'read_only': True},
            'care_rating': {'read_only': True},
            'oxygen_rating': {'read_only': True},
            'ventilator_availability': {'read_only': True},
            'oxygen_availability': {'read_only': True},
            'icu_availability': {'read_only': True},
            'datef': {'read_only': True},
            'added_by_id': {'read_only': True},
            'address': {'read_only': True}
        }

    def get_comment_count(self, marker):
        return marker.comment.all().count()


class GetReviewSerializer(serializers.ModelSerializer):
    images = GetImageSerializer(many=True, required=False)
    written_by_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Reviews
        fields = [
            'id', 'marker', 'financial_rating', 'total_rating', 'avg_cost', 'covid_rating', 'care_rating',
            'oxygen_rating',
            'beds_available', 'size', 'ventilator_availability', 'oxygen_availability',
            'icu_availability', 'comment', 'written_by', 'images', 'written_by_name', 'datef'

        ]

    def get_written_by_name(self, review):
        return review.written_by.username


class GetSusSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuspiciousMarking
        fields = [
            'id', 'marker', 'comment', 'created_by_id', 'datef'
        ]


def to_representation(self, data):
    if (data.helped_by != self.context['request'].user):
        if data.account_no:
            data.account_no = data.account_no[-4:]
    data = super(GetHelpRequestSerializer, self).to_representation(data)
    return data


class GetHelpRequestSerializer(serializers.ModelSerializer):
    gender_name = serializers.CharField(source='get_gender_display', read_only=True)
    uid = serializers.ReadOnlyField(source="user.id")

    class Meta:
        model = HelpRequest
        fields = [
            'id', "uid", 'req', 'Name', 'age', 'gender', 'address', 'gender_name',
            'requirement', 'public', 'mobile_number', 'request_type',
            'reason', 'attachment'
        ]


class GetMedicalRequestSerializer(GetHelpRequestSerializer):
    class Meta:
        model = HelpRequestMedical
        fields = GetHelpRequestSerializer.Meta.fields + [
            "symptoms", "symdays", "spo2", "oxy_bed"
        ]


class DetailMarkerSerializer(GetMarkerSerializer):
    comment = GetReviewSerializer(read_only=True, required=False, many=True)
    buildings = GetBuildingSerializer(read_only=True, required=False, many=True)
    doctors = DoctorSerializer(read_only=True, required=False, many=True, )
    departments = GetDepartmentSerializer(many=True, read_only=True)

    class Meta(GetMarkerSerializer.Meta):
        fields = GetMarkerSerializer.Meta.fields + ['comment', 'buildings', 'doctors', "departments"]


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = [
            'id', 'name'
        ]


class GetTokensSerializer(serializers.ModelSerializer):
    language = LanguageSerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Tokens
        fields = [
            'user', 'private_token', 'invite_token', 'invited', 'points', 'reviews', 'reports',
            'language', 'profile', 'phone_number', 'last_seen', 'gender', 'age', 'address'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'text', 'seen', 'deleted',
        ]
        extra_kwargs = {
            'text': {'read_only': True},
        }


class BannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImage
        fields = [
            'image'
        ]
