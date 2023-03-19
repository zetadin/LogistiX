from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.forms import UserCreationForm


# The registration view and POST handler
def registration_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, f'Your account has been created. You can log in now!')    
            return redirect('/menu')
    else:
        form = UserCreationForm()

    context = {'form': form}
    template = loader.get_template('register.html')
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

# logout is handled by django.contrib.auth and redirects to menu