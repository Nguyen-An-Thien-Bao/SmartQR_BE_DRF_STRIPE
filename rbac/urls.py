from django.urls import path
from .views import RegisterView, UserList, UserDetail
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("", UserList.as_view()),
    path("register/", RegisterView.as_view()),
    path("token/refresh", TokenRefreshView.as_view()), #refreshToken
    path("token/access", TokenObtainPairView.as_view()), #accessToken
    path("<int:pk>", UserDetail.as_view())
]