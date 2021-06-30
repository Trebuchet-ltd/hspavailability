from rest_framework import serializers

from .models import Images, Markers, Reviews, SuspiciousMarking, Patient, Tokens


class GetImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = [
            'image', 'useinmarker', 'hospital', 'review'
        ]


class GetMarkerSerializer(serializers.ModelSerializer):
    images = GetImageSerializer(many=True, required=False, read_only=True)
    comment_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Markers
        fields = [
            'id', 'name', 'Phone', 'size', 'financial_rating', 'avg_cost', 'covid_rating', 'beds_available',
            'care_rating', 'oxygen_rating', 'ventilator_availability', 'oxygen_availability', 'icu_availability',
            'lat', 'lng', 'datef', 'added_by_id', 'images', 'display_address', 'comment_count', 'address'
        ]
        extra_kwargs = {
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
            'id', 'marker', 'financial_rating', 'avg_cost', 'covid_rating', 'care_rating', 'oxygen_rating',
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


class GetPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            'Name', 'age', 'gender', 'symptoms', 'symdays', 'spo2', 'hospitalday', 'covidresult', 'hospitalpref',
            'attendername', 'attenderphone', 'relation', 'srfid', 'bunum', 'blood', 'bedtype', 'ct', 'ctscore'
        ]


class DetailMarkerSerializer(GetMarkerSerializer):
    comment = GetReviewSerializer(read_only=True, required=False, many=True)

    class Meta(GetMarkerSerializer.Meta):
        fields = GetMarkerSerializer.Meta.fields + ['comment']

class GetTokensSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tokens
        fields = [
            'user', 'private_token', 'invite_token'
        ]