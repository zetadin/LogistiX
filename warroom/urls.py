from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.warroom, name='warroom_index'),
    path('mapeditor', views.mapeditor, name='mapeditor'),
    path('map_setup', views.map_setup, name='map_setup'),
    path('generate_map', views.generate_map, name='warroom.generate_map'),

    # views that dump JSON data
    path('getmap', views.MapListView.as_view(), name='getmap'),
    path('getplatoons', views.PlatoonsListView.as_view(), name='getplatoons'),
    
]