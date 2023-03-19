from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    #path(r'^(?:(?P<login_err>\d+)/)?/$', views.index, name='index'),
    #path('m_login', views.login_view, name='m_login'),
    #path('', views.logout_view, name='m_logout'),
]