from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import PermissionDenied

# Create your views here.

def warroom(request):
    if(request.user.is_authenticated and request.user.is_active):
        context = {}
        template = loader.get_template('warroom.html')
        return HttpResponse(template.render(context, request))
    else:
        return(redirect('/menu'))
    

def mapeditor(request):
    if(request.user.is_authenticated and request.user.is_active):
        if(not request.user.is_staff):
            # only acessible to admins
            raise PermissionDenied
        context = {}
        template = loader.get_template('mapeditor.html')
        return HttpResponse(template.render(context, request))
    else:
        return(redirect('/menu'))