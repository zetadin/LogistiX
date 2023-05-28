from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.warroom, name='warroom_index'),
    path('mapeditor', views.mapeditor, name='mapeditor'),
]