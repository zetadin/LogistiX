from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

# Create your views here.

def warroom(request):
    if(request.user.is_authenticated and request.user.is_active):
        context = {}
        template = loader.get_template('warroom.html')
        return HttpResponse(template.render(context, request))
    else:
        return(redirect('/menu'))