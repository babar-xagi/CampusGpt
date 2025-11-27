from django.shortcuts import render , redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.views.decorators.http import require_http_methods

def home(request):
    """Render the home page."""
    return render(request, 'home.html')
