from django.urls import path
from .views import OrderListCreateView, OrderDetailView, OrderItemListView, OrderItemDetailView


urlpatterns = [
    path("", OrderListCreateView.as_view()),
    path("<int:pk>/", OrderDetailView.as_view()),
    path("items/", OrderItemListView.as_view()),
    path("items/<int:pk>/", OrderItemDetailView.as_view()),
]