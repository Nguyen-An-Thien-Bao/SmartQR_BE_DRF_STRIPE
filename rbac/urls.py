from django.urls import path
from .views import RegisterView, UserList, UserDetail, CustomTokenView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("", UserList.as_view()),
    path("register/", RegisterView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()), #refreshToken
    path("token/access/", CustomTokenView.as_view()), #accessToken
    path("<int:pk>/", UserDetail.as_view())
]