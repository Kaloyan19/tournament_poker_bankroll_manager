from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from tournaments import views as tournament_views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('tournaments.urls')),

    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html'
    ), name='login'),

    path('accounts/logout/', auth_views.LogoutView.as_view(
        template_name='registration/logged_out.html'
    ), name='logout'),

    path('accounts/signup/', tournament_views.signup, name='signup'),

    path('api/', include('tournaments.api_urls')),
]

