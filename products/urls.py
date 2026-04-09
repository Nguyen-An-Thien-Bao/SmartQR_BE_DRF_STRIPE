from django.urls import path
from .views import CategoryListCreateView, CategoryDetailView, MenuItemListCreateView, MenuItemDetailView, CategoryMenuItemListCreateView

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view()),
    path("categories/<int:pk>/", CategoryDetailView.as_view()),
    path("categories/menu-items/", CategoryMenuItemListCreateView.as_view()),


    path("menu-items/", MenuItemListCreateView.as_view()),
    path("menu-items/<int:pk>/", MenuItemDetailView.as_view()),
]