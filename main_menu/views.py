from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    template = loader.get_template('menu.html')
    context = {
        "login_err": request.GET.get('login_err', None),
        "reg_ok": request.GET.get('reg_ok', None)
    }
    return HttpResponse(template.render(context, request))

