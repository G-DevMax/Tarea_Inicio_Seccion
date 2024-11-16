# liberias
from django.urls import reverse_lazy

from django.views.generic import CreateView, DetailView, UpdateView, DeleteView

from django.contrib.auth import login, authenticate

from django.contrib.auth.base_user import AbstractBaseUser

from django.contrib.auth.models import PermissionsMixin, UserManager

from django.contrib.auth.validators import UnicodeUsernameValidator

from django.core.mail import send_mail

from django.db import models

from django.utils import timezone

from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model

from .forms import CustomUserCreationForm, UserUpdateForm

from django.urls import reverse

from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView

from django.contrib.auth.mixins import UserPassesTestMixin

# código de view
User = get_user_model()

class UserCreateAndLoginView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("tasks:index")

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        raw_pw = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=raw_pw)
        if user is not None:
            login(self.request, user)
        return response

class OnlyYouMixin(UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.pk == self.kwargs['pk'] or user.is_superuser

# Vista de Detalles del usuario
class UserDetail(OnlyYouMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'

# Vista de Actualización del Usuario
class UserUpdate(OnlyYouMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/user_edit.html'

    def get_success_url(self):
        return reverse('user_detail', kwargs={'pk': self.kwargs['pk']})

# Vista de Eliminación de Usuario
class UserDelete(OnlyYouMixin, DeleteView):
    model = User
    template_name = 'accounts/user_delete.html'
    success_url = reverse_lazy('login')

# Cambio de contraseña
class PasswordChange(PasswordChangeView):
    template_name = 'accounts/password_change.html'

# Cambio de contraseña correcta
class PasswordChangeDone(PasswordChangeDoneView):
    template_name = 'accounts/user_detail.html'

class AbstractUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=150,
        unique=True,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_("first name"), max_length=150, blank=True)
    last_name = models.CharField(_("last name"), max_length=150, blank=True)
    email = models.EmailField(_("email address"), blank=True)

    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        abstract = True

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        full_name = "%s %s" % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

