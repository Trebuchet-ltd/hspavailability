from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from chats.models import Bundle
from home.models import Tokens
from home.serializer import GetTokensSerializer


def get_image(token: Tokens):
    return token.profile.url if token.profile else ""


class UserSearchSerializer(serializers.ModelSerializer):
    private_token = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', "first_name", "last_name", "private_token", "profile",)

    @staticmethod
    def get_profile(user):
        try:
            return get_image(user.tokens)
        except ObjectDoesNotExist:
            return ""

    @staticmethod
    def get_private_token(user):
        try:
            return user.tokens.private_token
        except ObjectDoesNotExist:
            return ""


class UserSerializer(serializers.ModelSerializer):
    tokens = GetTokensSerializer(many=False, read_only=True, required=False)
    friends = serializers.SerializerMethodField()
    chat_friends = serializers.SerializerMethodField()

    # invited = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', "first_name", "last_name", 'tokens', 'friends', 'chat_friends')

    @classmethod
    def get_friends(cls, user):
        friends = [{"name": tkn.user.username, "email": tkn.user.email,
                    "token": tkn.private_token, "profile": get_image(tkn), "invited": True} for
                   tkn in
                   Tokens.objects.filter(invite_token=user.tokens.private_token)] + \
                  [
                      {"name": user.username, "email": user.email, "token": user.tokens.private_token,
                       "profile": get_image(user.tokens), "invited": False} for user in
                      user.tokens.friends.all()] if hasattr(user, 'token') else []
        return friends

    @classmethod
    def get_chat_friends(cls, user):
        return filter(lambda friend: Bundle.objects.filter(user__tokens__private_token=friend["token"]).exists(),
                      cls.get_friends(user))


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("name",)
