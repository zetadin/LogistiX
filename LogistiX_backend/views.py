from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponse
from django.template import loader
from django.template.loader import render_to_string
from .forms import UserRegistrationForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token_gen


# The registration view and POST handler
def registration_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_activate_email(request, user, form.cleaned_data.get('email'))

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

def send_activate_email(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('template_activate_account.html', {
        'username': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token_gen.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if not email.send():
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')
    pass

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token_gen.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
    else:
        messages.error(request, 'Activation link is invalid!')

    template = loader.get_template('after_activation.html')
    context={}
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