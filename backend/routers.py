from rest_framework import routers
from accounts.viewset import UserViewSet

routers = routers.SimpleRouter()
routers.register(r'users', UserViewSet, basename='user')

urlpatterns = routers.urls