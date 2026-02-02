from django.urls import path
from . import views

app_name = 'tournaments'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    path('add_tournament/', views.add_tournament, name='add_tournament'),
    path('tournaments/', views.tournament_list, name='tournament_list'),
    path('tournaments/<int:pk>/edit/', views.edit_tournament, name='edit_tournament'),
    path('tournaments/<int:pk>/delete/', views.delete_tournament, name='delete_tournament'),

    path('add_adjustment/', views.add_adjustment, name='add_adjustment'),
]