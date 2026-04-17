from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from accounts.serializers import UserSerializer
from accounts.models import User

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all() 
    permission_classes = [AllowAny]
