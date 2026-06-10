from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class PasswordGeneratorForm(forms.Form):
    length = forms.IntegerField(
        initial=16,
        min_value=8,
        max_value=50,
        label="Password Length",
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "min": "8",
            "max": "50",
            "id": "lengthInput"
        })
    )
    include_uppercase = forms.BooleanField(
        initial=True,
        required=False,
        label="Include Uppercase Letters (A-Z)",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "id": "upperCheck"})
    )
    include_lowercase = forms.BooleanField(
        initial=True,
        required=False,
        label="Include Lowercase Letters (a-z)",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "id": "lowerCheck"})
    )
    include_numbers = forms.BooleanField(
        initial=True,
        required=False,
        label="Include Numbers (0-9)",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "id": "numbersCheck"})
    )
    include_special = forms.BooleanField(
        initial=True,
        required=False,
        label="Include Special Characters (!@#$%^&*)",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input", "id": "specialCheck"})
    )

    def clean(self):
        cleaned_data = super().clean()
        include_uppercase = cleaned_data.get("include_uppercase")
        include_lowercase = cleaned_data.get("include_lowercase")
        include_numbers = cleaned_data.get("include_numbers")
        include_special = cleaned_data.get("include_special")

        if not (include_uppercase or include_lowercase or include_numbers or include_special):
            raise forms.ValidationError(
                "You must select at least one character type to generate a password."
            )

        return cleaned_data


class UserRegistrationForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter your email"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Create password"})
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm password"})
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Choose a username"}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        return cleaned_data


class UserLoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter username or email"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Enter password"})
    )

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get("username_or_email")
        password = cleaned_data.get("password")

        if username_or_email and password:
            user = None
            # Check if email is used instead of username
            if "@" in username_or_email:
                try:
                    db_user = User.objects.get(email__iexact=username_or_email)
                    username = db_user.username
                except User.DoesNotExist:
                    username = username_or_email
            else:
                username = username_or_email

            user = authenticate(username=username, password=password)

            if not user:
                raise forms.ValidationError("Invalid username/email or password.")
            elif not user.is_active:
                raise forms.ValidationError("This account has been disabled.")

            cleaned_data["user"] = user

        return cleaned_data


class OTPVerificationForm(forms.Form):
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            "class": "form-control text-center font-monospace fs-2 tracking-wide",
            "placeholder": "000000",
            "pattern": "[0-9]{6}",
            "maxlength": "6",
            "autofocus": "autofocus",
            "autocomplete": "off"
        })
    )

    def clean_otp(self):
        otp = self.cleaned_data.get("otp")
        if not otp.isdigit():
            raise forms.ValidationError("The OTP code must consist of 6 digits only.")
        return otp
