# Copyright (c) 2025, Yuriy Khalak.
# Server-side part of LogisticX.

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
