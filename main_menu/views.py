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


def login_view(request):
    if request.user.is_authenticated:
         redirect('/menu')
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        return redirect('/menu')
    else:
        # Return an 'invalid login' error message.
        response = redirect('/menu')
        response['Location'] += '?login_err=1'
        return response

def logout_view(request):
    logout(request)
    # Redirect to a success page.