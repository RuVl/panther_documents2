import logging

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView

from authapp.forms import ShopUserRegisterForm, ShopUserLoginForm
from authapp.models import ShopUser


logger = logging.getLogger('gunicorn')


class ShopUserRegisterView(CreateView):
    form_class = ShopUserRegisterForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('auth:wait_verify')

    def get(self, request, *args, **kwargs):
        # If already authorised - go to office
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('auth:office'))

        return super().get(request, args, kwargs)

    def form_valid(self, form: ShopUserRegisterForm):
        response = super().form_valid(form)

        # Send email with activation key
        user: ShopUser = self.object
        domain = self.request.get_host()

        verify_link = reverse('auth:verify', args=[user.email, user.activation_key])
        title = f'Подтверждение учетной записи {user.username}'
        message = f'Для подтверждения учетной записи {user.username} на портале ' \
                  f'{domain} перейдите по ссылке: \n{self.request.scheme}://{domain}{verify_link}'

        if not send_mail(title, message, None, [user.email], fail_silently=False):
            user.delete()
            logger.warning("Can't send email!")
            # TODO page something went wrong

        return response


class VerifyView(TemplateView):
    template_name = 'auth/verification.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        email = self.kwargs.get('email')
        activation_key = self.kwargs.get('activation_key')

        if email is None:
            context['activate_status'] = 'wait'
            return context

        user = ShopUser.objects.get(email=email)
        if user.is_active:
            context['activate_status'] = 'already'
        elif user.activation_key == activation_key and not user.is_activation_key_expired():
            user.is_active = True
            user.save()
            auth.login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            context['activate_status'] = 'success'
        else:  # Expired, wrong or no activation key
            context['activate_status'] = 'fail'

        return context


class ShopUserLoginView(LoginView):
    form_class = ShopUserLoginForm
    template_name = 'auth/login.html'
    next_page = reverse_lazy('auth:office')

    def get(self, request, *args, **kwargs):
        # If already authorised - go to office
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('auth:office'))

        return super().get(request, args, kwargs)


class ShopUserLogoutView(LogoutView):
    next_page = reverse_lazy('main:home')


@login_required()
def office(request):
    return render(request, 'auth/office.html')
