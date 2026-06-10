from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
import datetime
import string

from .forms import PasswordGeneratorForm, UserRegistrationForm, UserLoginForm, OTPVerificationForm
from .utils import generate_secure_password, analyze_password_strength
from .models import UserOTP

class PasswordGeneratorUtilTests(TestCase):
    def test_generate_secure_password_length(self):
        for length in [8, 16, 32, 50]:
            password = generate_secure_password(length, True, True, True, True)
            self.assertEqual(len(password), length)

    def test_generate_secure_password_pools(self):
        password = generate_secure_password(30, True, False, False, False)
        self.assertTrue(all(c in string.ascii_uppercase for c in password))

        password = generate_secure_password(30, False, True, False, False)
        self.assertTrue(all(c in string.ascii_lowercase for c in password))

        password = generate_secure_password(30, False, False, True, False)
        self.assertTrue(all(c in string.digits for c in password))

        password = generate_secure_password(8, True, True, True, True)
        self.assertTrue(any(c in string.ascii_uppercase for c in password))
        self.assertTrue(any(c in string.ascii_lowercase for c in password))
        self.assertTrue(any(c in string.digits for c in password))
        self.assertTrue(any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password))

    def test_generate_secure_password_invalid_inputs(self):
        with self.assertRaises(ValueError):
            generate_secure_password(12, False, False, False, False)
        with self.assertRaises(ValueError):
            generate_secure_password(7, True, True, True, True)
        with self.assertRaises(ValueError):
            generate_secure_password(51, True, True, True, True)

    def test_analyze_password_strength(self):
        weak = analyze_password_strength("abc")
        self.assertEqual(weak["strength"], "Weak")
        self.assertLess(weak["entropy"], 40.0)

        strong = analyze_password_strength("A3$gH9!kP2_qL5#mN8*rV1&x")
        self.assertEqual(strong["strength"], "Very Strong")
        self.assertGreaterEqual(strong["entropy"], 80.0)


class PasswordGeneratorFormTests(TestCase):
    def test_form_validation_valid(self):
        form = PasswordGeneratorForm(data={
            "length": 16,
            "include_uppercase": True,
            "include_lowercase": True,
            "include_numbers": True,
            "include_special": True
        })
        self.assertTrue(form.is_valid())

    def test_form_validation_no_checkboxes(self):
        form = PasswordGeneratorForm(data={
            "length": 12,
            "include_uppercase": False,
            "include_lowercase": False,
            "include_numbers": False,
            "include_special": False
        })
        self.assertFalse(form.is_valid())


class AuthenticationFormTests(TestCase):
    def test_registration_form_valid(self):
        form = UserRegistrationForm(data={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123"
        })
        self.assertTrue(form.is_valid())

    def test_registration_form_mismatched_passwords(self):
        form = UserRegistrationForm(data={
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword123",
            "confirm_password": "differentpassword"
        })
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_password", form.errors)

    def test_login_form_invalid_credentials(self):
        form = UserLoginForm(data={
            "username_or_email": "nonexistent",
            "password": "wrongpassword"
        })
        self.assertFalse(form.is_valid())

    def test_otp_form_invalid(self):
        form = OTPVerificationForm(data={"otp": "123a56"})
        self.assertFalse(form.is_valid())


class PasswordGeneratorViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user_password = "securepassword123"
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password=self.user_password
        )

    def test_homepage_redirects_unauthenticated(self):
        # Accessing dashboard as guest should redirect to login
        response = self.client.get(reverse("password_generator:index"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("password_generator:login"), response.url)

    def test_user_registration(self):
        response = self.client.post(reverse("password_generator:register"), {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword123",
            "confirm_password": "newpassword123"
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_and_otp_flow(self):
        # 1. Post valid credentials
        response = self.client.post(reverse("password_generator:login"), {
            "username_or_email": "testuser",
            "password": self.user_password
        })
        # Should redirect to verify OTP page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("password_generator:verify_otp"))
        self.assertIn("pre_auth_user_id", self.client.session)

        # Confirm OTP record was created in database
        otp_record = UserOTP.objects.get(user=self.user)
        self.assertEqual(len(otp_record.otp), 6)
        self.assertTrue(otp_record.is_valid())

        # 2. Try verification with wrong OTP
        verify_response = self.client.post(reverse("password_generator:verify_otp"), {
            "otp": "000000"
        })
        self.assertEqual(verify_response.status_code, 200) # Form invalid returns page
        self.assertNotIn("_auth_user_id", self.client.session)

        # 3. Verify with correct OTP
        verify_response = self.client.post(reverse("password_generator:verify_otp"), {
            "otp": otp_record.otp
        })
        # Should redirect to generator homepage
        self.assertEqual(verify_response.status_code, 302)
        self.assertRedirects(verify_response, reverse("password_generator:index"))
        
        # Verify the user is now authenticated
        self.assertIn("_auth_user_id", self.client.session)
        self.assertNotIn("pre_auth_user_id", self.client.session)
        # Check that OTP database record is deleted
        self.assertFalse(UserOTP.objects.filter(user=self.user).exists())

    def test_expired_otp(self):
        # Request login
        self.client.post(reverse("password_generator:login"), {
            "username_or_email": "testuser",
            "password": self.user_password
        })
        otp_record = UserOTP.objects.get(user=self.user)
        
        # Artificially age the OTP record (simulate 6 minutes ago)
        otp_record.created_at = timezone.now() - datetime.timedelta(minutes=6)
        otp_record.save()

        # Submit the correct OTP
        response = self.client.post(reverse("password_generator:verify_otp"), {
            "otp": otp_record.otp
        })
        self.assertEqual(response.status_code, 200)
        # Verify it has error
        self.assertFormError(response.context['form'], "otp", "This verification code has expired. Please log in again to receive a new code.")
