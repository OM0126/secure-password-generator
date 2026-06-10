import datetime
import secrets
import string
from django.views.generic import TemplateView, View
from django.views.generic.edit import FormView
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils import timezone

from .forms import PasswordGeneratorForm, UserRegistrationForm, UserLoginForm
from .utils import generate_secure_password, analyze_password_strength
# UserOTP model and OTP verification have been removed.


def compute_stats(history):
    """
    Computes summary statistics for a given password history list.
    """
    total = len(history)
    if total == 0:
        return {
            "total": 0,
            "avg_entropy": 0.0,
            "weak_count": 0,
            "medium_count": 0,
            "strong_count": 0,
            "very_strong_count": 0,
            "weak_pct": 0,
            "medium_pct": 0,
            "strong_pct": 0,
            "very_strong_pct": 0,
        }
    
    total_entropy = sum(item["entropy"] for item in history)
    avg_entropy = round(total_entropy / total, 1)
    
    weak = sum(1 for item in history if item["strength"] == "Weak")
    medium = sum(1 for item in history if item["strength"] == "Medium")
    strong = sum(1 for item in history if item["strength"] == "Strong")
    very_strong = sum(1 for item in history if item["strength"] == "Very Strong")
    
    return {
        "total": total,
        "avg_entropy": avg_entropy,
        "weak_count": weak,
        "medium_count": medium,
        "strong_count": strong,
        "very_strong_count": very_strong,
        "weak_pct": int(round((weak / total) * 100)),
        "medium_pct": int(round((medium / total) * 100)),
        "strong_pct": int(round((strong / total) * 100)),
        "very_strong_pct": int(round((very_strong / total) * 100)),
    }

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "password_generator/index.html"

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PasswordGeneratorForm()
        
        # Load history and stats from session
        history = self.request.session.get("password_history", [])
        context["history"] = history
        context["stats"] = compute_stats(history)
        return context

class GeneratePasswordView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = PasswordGeneratorForm(request.POST)
        if form.is_valid():
            length = form.cleaned_data["length"]
            use_upper = form.cleaned_data["include_uppercase"]
            use_lower = form.cleaned_data["include_lowercase"]
            use_digits = form.cleaned_data["include_numbers"]
            use_special = form.cleaned_data["include_special"]

            try:
                password = generate_secure_password(
                    length=length,
                    use_upper=use_upper,
                    use_lower=use_lower,
                    use_digits=use_digits,
                    use_special=use_special
                )
                
                analysis = analyze_password_strength(password)
                history = request.session.get("password_history", [])
                
                entry = {
                    "password": password,
                    "length": length,
                    "entropy": analysis["entropy"],
                    "strength": analysis["strength"],
                    "color": analysis["color"],
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "options": {
                        "upper": use_upper,
                        "lower": use_lower,
                        "digits": use_digits,
                        "special": use_special
                    }
                }
                
                history.insert(0, entry)
                request.session["password_history"] = history[:10]
                request.session.modified = True
                
                stats = compute_stats(request.session["password_history"])
                
                return JsonResponse({
                    "success": True,
                    "password": password,
                    "analysis": analysis,
                    "history": request.session["password_history"],
                    "stats": stats
                })
                
            except ValueError as e:
                return JsonResponse({
                    "success": False,
                    "errors": {"__all__": [str(e)]}
                }, status=400)
        else:
            errors = {field: errors[0] for field, errors in form.errors.items()}
            if "__all__" in form.errors:
                errors["non_field_errors"] = form.errors["__all__"][0]
            return JsonResponse({
                "success": False,
                "errors": errors
            }, status=400)

class ClearHistoryView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if "password_history" in request.session:
            del request.session["password_history"]
            request.session.modified = True
            
        return JsonResponse({
            "success": True,
            "history": [],
            "stats": compute_stats([])
        })


# --- Authentication & OTP Views ---


    template_name = "password_generator/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("password_generator:login")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("password_generator:index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data["password"])
        user.save()
        return super().form_valid(form)


class LoginView(FormView):
    template_name = "password_generator/login.html"
    form_class = UserLoginForm
    success_url = reverse_lazy("password_generator:index")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("password_generator:index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.cleaned_data["user"]
        login(self.request, user)
        return super().form_valid(form)



class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("password_generator:login")

    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("password_generator:login")
