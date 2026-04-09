from django.urls import path
from .views import OrderListCreateView, OrderDetailView, OrderItemListView, OrderItemDetailView
from payments.views import mark_order_paid


urlpatterns = [
    path("", OrderListCreateView.as_view()),
    path("<int:pk>/", OrderDetailView.as_view()),
    path("<int:pk>/mark-paid", mark_order_paid),


    path("items/", OrderItemListView.as_view()),
    path("items/<int:pk>/", OrderItemDetailView.as_view()),
]