from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    template = loader.get_template('menu.html')
    context = {
    }
    return HttpResponse(template.render(context, request))


def login_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        return redirect(view_to_redirect_to)
    else:
        # Return an 'invalid login' error message.
        return redirect(view_to_redirect_to)

def logout_view(request):
    logout(request)
    # Redirect to a success page.