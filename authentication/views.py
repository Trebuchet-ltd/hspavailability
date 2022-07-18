import logging

import django_filters
from django.contrib.auth.models import User, Group
from oauth2_provider.contrib.rest_framework import TokenHasScope, OAuth2Authentication
from rest_framework import status, filters
from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response

from home.models import Language, Tokens
from rest_framework_social_oauth2.authentication import SocialAuthentication
from v2.views import give_points
from .authentication import CsrfExemptSessionAuthentication
from .permissions import IsOwner
from .serializer import UserSerializer, GroupSerializer, UserSearchSerializer


class UserApiViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwner]
    serializer_class = UserSerializer
    authentication_classes = [CsrfExemptSessionAuthentication, SocialAuthentication, OAuth2Authentication]
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'put', 'patch', 'head', 'options']
    parser_class = [FileUploadParser]

    def get_queryset(self):
        try:
            return User.objects.filter(id=self.request.user.id)
        except User.DoesNotExist:
            return User.objects.none()
        except Exception:

            return User.objects.none()

    def list(self, request, *args, **kwargs):

        if not request.user.is_superuser:
            self.queryset = self.queryset.filter(pk=request.user.pk)
        return viewsets.ModelViewSet.list(self, request, *args, **kwargs)

    @action(detail=False, methods=["get", "post", "patch"], url_path='me')
    def me(self, request, *args, **kwargs):
        if request.method == "PATCH":
            data = request.data
            user = request.user
            token = Tokens.objects.get(private_token=user.tokens.private_token)
            tokens = request.data.get('tokens')
            if not tokens:
                try:
                    print(f"{request.FILES['image']}")
                    profile = request.FILES['image']
                    print(profile)
                    token.save()
                    token.profile.save(profile.name, profile)
                    return Response(status=200)
                except Exception as e:
                    print(e)
                    raise e

            languages = tokens.get('language')
            phone_number = tokens.get('phone_number')
            print(f"{languages = }")
            token.language.all().delete()
            for ln in languages:
                l, _ = Language.objects.get_or_create(name=ln['name'])
                token.language.add(l.id)

            token.phone_number = phone_number
            token.gender = tokens.get('gender')
            token.age = tokens.get('age')
            token.address = tokens.get('address')
            token.save()
            serializer = UserSerializer(user, data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        else:

            self.queryset = self.queryset.filter(pk=request.user.pk)
            return viewsets.ModelViewSet.list(self, request, *args, **kwargs)
        return viewsets.ModelViewSet.list(self, request, *args, **kwargs)

    @action(detail=False, methods=["post"], url_path='friend')
    def friend(self, request, *args, **kwargs):
        try:
            tkn = Tokens.objects.get(private_token=request.data.get('token'))
            user = request.user
            print('adding friend called')
            if tkn:
                if tkn.user != request.user:
                    print(tkn.user)
                    print('adding friend fn called')
                    user.tokens.add_friend(tkn.user)
                    return Response({'detail': "friend added"}, status=200)
                return Response({"detail": "you have to choose any user other than you"},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
            return Response({"detail": "token is required"},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        except Tokens.DoesNotExist:
            return Response({"detail": "user does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UserSearchApiViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UserSearchSerializer
    queryset = User.objects.all()
    http_method_names = ['get', "options"]
    filter_backends = [filters.SearchFilter, django_filters.rest_framework.DjangoFilterBackend]
    search_fields = ['username', 'first_name', 'last_name']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class GroupList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasScope]
    required_scopes = ['groups']
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
