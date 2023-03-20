from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from .forms import UserRegistrationForm


# The registration view and POST handler
def registration_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            #user.save()
            activateEmail(request, user, form.cleaned_data.get('email'))

            response = redirect('/menu')
            response['Location'] += '?reg_ok=1'  
            return response
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = UserRegistrationForm()

    context = {'form': form}
    template = loader.get_template('register.html')
    return HttpResponse(template.render(context, request))

def activateEmail(request, user, to_email):
    #messages.success(request, f'Activation link sent to your email. Activate your account before logging in.')
    pass


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