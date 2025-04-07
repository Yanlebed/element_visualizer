# visualizer/urls.py
from django.urls import path
from . import views

app_name = 'visualizer'

urlpatterns = [
    path('', views.index, name='index'),
    path('visualize/', views.visualize, name='visualize'),
]