from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomePage.as_view(), name='api_initial_page'),
]
