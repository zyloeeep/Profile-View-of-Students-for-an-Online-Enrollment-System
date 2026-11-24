
from django import forms
from django.contrib.auth import authenticate, get_user_model


class EmailLoginForm(forms.Form):

    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter your email address",
            "autocomplete": "email",
            "class": "w-full rounded-lg border border-line bg-page px-4 py-3 text-ink focus:outline-none focus:ring-2 focus:ring-brand-solid",
        }),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter your password",
            "autocomplete": "current-password",
            "class": "w-full rounded-lg border border-line bg-page px-4 py-3 text-ink focus:outline-none focus:ring-2 focus:ring-brand-solid",
        }),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            User = get_user_model()

            try:
                user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                user = None
            except User.MultipleObjectsReturned:
                user = None

            if user is not None:
                self.user_cache = authenticate(
                    self.request,
                    username=user.get_username(),
                    password=password,
                )

            if self.user_cache is None:
                raise forms.ValidationError(
                    "Incorrect email address or password."
                )

        return cleaned_data

    def get_user(self):
        return self.user_cache
