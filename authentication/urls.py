from django.urls import path, include
from django.contrib.auth.models import User, Group
from .views import UserList, GroupList, UserDetails

# Setup the URLs and include login URLs for the browsable API.
urlpatterns = [
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('users/', UserList.as_view()),
    path('users/<pk>/', UserDetails.as_view()),
    path('groups/', GroupList.as_view()),
    # ...
]