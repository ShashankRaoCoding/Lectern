from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.textbook_list, name="textbook_list"),
    path("textbooks/<int:pk>/", views.textbook_detail, name="textbook_detail"),
    path("textbooks/<int:pk>/read/", views.textbook_read, name="textbook_read"),
    path("textbooks/<int:pk>/delete/", views.textbook_delete, name="textbook_delete"),
    path("textbooks/<int:pk>/add/", views.add_content, name="add_content"),
    path("textbooks/<int:pk>/sections/<int:section_pk>/", views.section_read, name="section_read"),
    path("textbooks/<int:pk>/sections/<int:section_pk>/delete/", views.section_delete, name="section_delete"),
    path("preferences/", views.preferences, name="preferences"),
]
