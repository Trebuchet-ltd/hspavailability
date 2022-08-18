import json
import logging

import django_filters
import requests
from django.contrib.auth.models import User
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from rest_framework import viewsets, generics, filters, permissions, status
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

import maps.settings as settings
from internals.models import Images
from internals.views import add_points
from v2.views import give_points
from .serializer import *
from authentication.permissions import IsOwnerUser


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    print(x_forwarded_for)
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def get_loction_python(request):
    ip = get_client_ip(request)
    ipsearchurl = f'https://ipapi.co/{ip}/json/'
    loc_data = requests.get(ipsearchurl, headers={
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'})
    return json.loads(loc_data.content)


def update_marker(id):
    """
    formula for each attribute = Σ(0.99^(x)*sum(data of x days before))/Σ(0.99^x)
    """
    ob = Markers.objects.get(id=id)
    rev = Reviews.objects.filter(marker__id=id)
    fin = []
    avg = []
    covid = []
    bed = []
    care = []
    oxy = []
    vent = []
    oxya = []
    icu = []
    size = []
    day = []
    den = []
    denb = []
    deno = []
    denv = []
    deni = []
    denoa = []
    for x in rev:
        day.append(x.day)
    dmax = max(day)
    for x in rev:
        d = 0.99 ** (dmax - x.day)
        den.append(d)
        fin.append(d * x.financial_rating)
        avg.append(d * x.avg_cost)
        covid.append(d * x.covid_rating)
        size.append(d * (x.size + 1))
        care.append(d * x.care_rating)
        if x.beds_available != 0:
            bed.append(d * (x.beds_available - 1))
            denb.append(d)
        if x.oxygen_rating != 0:
            oxy.append(d * x.oxygen_rating)
            deno.append(d)
        if x.ventilator_availability != 0:
            vent.append(d * (x.ventilator_availability - 1))
            denv.append(d)
        if x.oxygen_availability != 0:
            oxya.append(d * (x.oxygen_availability - 1))
            denoa.append(d)
        if x.icu_availability != 0:
            icu.append(d * (x.icu_availability - 1))
            deni.append(d)
    dens = sum(den)
    ob.financial_rating = round(sum(fin) / dens, 1)
    ob.avg_cost = sum(avg) / dens
    ob.size = round(sum(size) / dens - 1)
    ob.covid_rating = round(sum(covid) / dens, 1)
    ob.care_rating = round(sum(care) / dens, 1)
    ob.oxygen_rating = round(sum(oxy) / sum(deno), 1) if deno else 0
    ob.beds_available = round(sum(bed) * 100 / sum(denb), 2) if denb else 0
    ob.ventilator_availability = round(sum(vent) * 100 / sum(denv), 2) if denv else 0
    ob.oxygen_availability = round(sum(oxya) * 100 / sum(denoa), 2) if denoa else 0
    ob.icu_availability = round(sum(icu) * 100 / sum(deni), 2) if deni else 0
    ob.save()


class LimitOffsetPaginationWithMaxLimit(LimitOffsetPagination):
    max_limit = 100


class MarkerApiViewSet(viewsets.ModelViewSet, generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Markers.objects.all().filter().order_by('id')
    serializer_class = GetMarkerSerializer
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    page_size = 100
    max_page_size = 100
    max_limit = 100

    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = {'financial_rating': ['gte', 'lte', 'exact'],
                        'oxygen_rating': ['gte', 'lte', 'exact'], 'ventilator_availability': ['gte', 'lte', 'exact'],
                        'oxygen_availability': ['gte', 'lte', 'exact'], 'icu_availability': ['gte', 'lte', 'exact'],
                        'avg_cost': ['gte', 'lte', 'exact'],
                        'care_rating': ['gte', 'lte', 'exact'], 'covid_rating': ['gte', 'lte', 'exact'],
                        'beds_available': ['gte', 'lte', 'exact'], 'category': ['in'], 'type': ['in'],
                        'ownership': ['in'], 'medicine': ['in']}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.condition = False

    def get_serializer_class(self):
        if self.action == 'list':
            return GetMarkerSerializer
        if self.action == 'retrieve':
            return DetailMarkerSerializer
        return GetMarkerSerializer

    def perform_create(self, serializer):
        print(self.request.data)
        user = self.request.user
        loc = Point(float(self.request.data['lng']), float(self.request.data['lat']),
                    srid=4326)  # Point(x,y). x=lng and y=lat
        url = f"https://eu1.locationiq.com/v1/reverse.php?key=pk.959200a41370341f608a91b67be6e8eb&lat={self.request.data['lat']}&lon={self.request.data['lng']}&format=json"
        det = requests.get(url)
        add_points(self.request.user, settings.add_hospital_point)
        if det.status_code == 200:
            data = json.loads(det.content.decode())

            serializer.save(address=data["address"], display_address=data["display_name"], added_by=user, location=loc,
                            pending_approval=True)

        else:
            raise serializers.ValidationError({"detail": "Address not obtainable from Latitude and Longitude"})

    def perform_update(self, serializer):
        instance = self.get_object()
        print(instance.Phone)
        print(self.request.data)
        lst = ['', '0', '00', '000', '0000', '00000', '000000', '0000000', '00000000', '000000000', '0000000000']
        if instance.Phone not in lst and instance.Phone != self.request.data['Phone']:
            raise serializers.ValidationError({
                "detail": "Please Do Not edit exiting valid Phone Numbers."
                          " Please Report if you think the existing phone number is wrong."
            })
        else:
            serializer.save()

    def get_pagination_class(self):
        if self.condition:
            return LimitOffsetPaginationWithMaxLimit
        return PageNumberPagination

    pagination_class = property(fget=get_pagination_class)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        self.condition = request._request.GET.get('limit', False)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        else:
            serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        distance = float(self.request.GET.get('distance', 10000000))
        queryset = super(MarkerApiViewSet, self).filter_queryset(queryset)
        try:
            lat = float(self.request.GET.get('lat', 0))
            lng = float(self.request.GET.get('lng', 0))
        except ValueError:
            data = get_loction_python(self.request)
            try:
                lat = float(data['latitude'])
                lng = float(data['longitude'])
            except Exception as e:
                logging.exception(e)
                lat, lng = 0, 0
        if lat and lng:
            loc = Point(lng, lat, srid=4326)
            if queryset.count() > 400:
                queryset = queryset.filter(
                    lat__gte=lat - 2.5,
                    lat__lte=lat + 2.5,
                    lng__gte=lng - 2.5,
                    lng__lte=lng + 2.5,
                )
            queryset = queryset.filter(location__distance_lte=(loc, D(m=distance))).annotate(
                distance=Distance('location', loc)).order_by('distance')
        return queryset


class ReviewViewSet(viewsets.ModelViewSet, generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Reviews.objects.all().order_by('id')
    serializer_class = GetReviewSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def perform_create(self, serializer):
        user = self.request.user
        print(self.request.data)
        rev = Reviews.objects.filter(marker=self.request.data['marker'], written_by=self.request.user).exists()
        print(rev)
        if rev:
            raise serializers.ValidationError({"detail": "Only One Review Allowed Per Hospital"})
        serializer.save(written_by=user)

    def create(self, request, *args, **kwargs):
        response = viewsets.ModelViewSet.create(self, request, *args, **kwargs)
        mob = Markers.objects.get(id=response.data['marker'])
        rev = Reviews.objects.get(id=response.data['id'])
        rev.day = (rev.datef - mob.datef).days
        update_marker(response.data['marker'])
        return response


class SusViewSet(viewsets.ModelViewSet, generics.GenericAPIView):
    queryset = SuspiciousMarking.objects.all()
    serializer_class = GetSusSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = HelpRequest.objects.all()
    serializer_class = GetHelpRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def retrieve(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        help_req = HelpRequest.objects.get(pk=pk)
        serializer = GetHelpRequestSerializer(help_req)
        print(help_req.request_type)
        if help_req.request_type == "M":
            serializer = GetMedicalRequestSerializer(HelpRequestMedical.objects.get(id=pk))
        elif help_req.request_type == "B":
            serializer = GetBloodRequestSerializer(HelpRequestBlood.objects.get(id=pk))
        elif help_req.request_type == "FI":
            serializer = GetFinancialRequestSerializer(HelpRequestBlood.objects.get(id=pk))

        return Response(serializer.data)

    def get_serializer_class(self, r_type_new=""):
        try:
            r_type = r_type_new if r_type_new else self.request.GET["type"]
            if r_type == "M":
                return GetMedicalRequestSerializer
            elif r_type == "FI":
                return HelpRequestFinancial
            elif r_type == "B":
                return HelpRequestBlood
            else:
                return HelpRequest
        except Exception as e:
            print(e)
            return GetHelpRequestSerializer

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        if "r_rype" in kwargs.items():
            serializer_class = self.get_serializer_class(kwargs["r_type"])
        else:
            serializer_class = self.get_serializer_class()

        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        r_type = request.data["request_type"]
        serializer = self.get_serializer(data=request.data, r_type=r_type)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def filter_queryset(self, queryset):
        user = self.request.user
        queryset = super(PatientViewSet, self).filter_queryset(queryset)
        return list(set(queryset.filter(user=user.id) | queryset.filter(public=True)))

    @action(detail=False, methods=["get", "post"], url_path='friends')
    def friends(self, request, *args, **kwargs):
        token = Tokens.objects.get(user_id=self.request.user.id)
        invite_token = token.invite_token
        private_token = token.private_token
        users = User.objects.filter(tokens__private_token=invite_token) \
                | User.objects.filter(tokens__invite_token=private_token)
        self.queryset = self.queryset.filter(user__in=users)
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.queryset, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["get", "post"], url_path='all')
    def all(self, request, *args, **kwargs):
        self.queryset = self.queryset.all().exclude(user=request.user)
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(self.queryset, many=True)

        return Response(serializer.data)

    @action(detail=False, methods=["get", ], url_path='help')
    def me_helped(self, request, *args, **kwargs):
        patient = HelpRequest.objects.filter(confirmed__in=request.user)

        page = self.paginate_queryset(patient)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(patient, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path='help')
    def help(self, request, pk):
        user = request.user
        patient = HelpRequest.objects.get(pk=pk)
        patient.help_requests.add(user)
        patient.helped_by = user
        patient.save()
        serializer = self.get_serializer(patient, many=False)
        return Response(serializer.data, status=201)

    # @action(detail=True, methods=["post"], url_path='accept', permission_classes=[IsOwnerUser, ])
    # def accept(self, request, pk):
    #     user = request.user
    #     patient = Patient.objects.get(pk=pk)
    #     patient.help_requests.add(user)
    #     patient.helped_by = user
    #     patient.save()
    #     serializer = self.get_serializer(patient, many=False)
    #     return Response(serializer.data, status=201)


class ImageViewSet(viewsets.ModelViewSet, generics.GenericAPIView):
    queryset = Images.objects.all()
    serializer_class = GetImageSerializer
    parser_class = [FileUploadParser]

    def perform_create(self, serializer):
        user = self.request.user
        give_points(user.tokens.private_token, 'image')
        serializer.save(user=user)


class LanguageApiViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    http_method_names = ['get', 'post']
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['name']


class NotificationApiViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsOwnerUser]
    http_method_names = ['get', 'post']
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['text']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user, ).exclude(deleted=True)

    @action(detail=False, methods=["get", "post"], url_path='read')
    def read(self):
        notifications = Notification.objects.filter(user=self.request.user, seen=False)
        for notification in notifications:
            notification.seen = True
            notification.save()

    @action(detail=False, methods=["get", "post"], url_path='del')
    def delete(self):
        notifications = Notification.objects.filter(user=self.request.user, deleted=False)
        for notification in notifications:
            notification.deleted = True
            notification.save()


class BannerImageViewSet(viewsets.ModelViewSet):
    queryset = BannerImage.objects.all()
    serializer_class = BannerImageSerializer
    http_method_names = ['get', 'post']
