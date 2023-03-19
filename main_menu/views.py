from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    template = loader.get_template('menu.html')
    context = {
        "login_err": request.GET.get('login_err', None)
    }
    return HttpResponse(template.render(context, request))

def logout_view(request):
    logout(request)
    # Redirect to a success page.