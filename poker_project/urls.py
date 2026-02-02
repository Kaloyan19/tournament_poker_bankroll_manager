# tournament_poker_bankroll_manager/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Your poker app
    path('', include('tournaments.urls')),

    # Custom auth - SIMPLER VERSION
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),

    path('accounts/logout/', auth_views.LogoutView.as_view(
        template_name='registration/logged_out.html'
    ), name='logout'),
]

# REMOVE the RedirectView line for now - it might conflict