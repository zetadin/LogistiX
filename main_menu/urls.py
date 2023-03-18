from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #path('', views.login_view, name='m_login'),
    #path('', views.logout_view, name='m_logout'),
]