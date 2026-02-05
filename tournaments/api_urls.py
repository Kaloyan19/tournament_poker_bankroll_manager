from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import TournamentViewSet, BankrollAdjustmentViewSet, UserViewSet

router = DefaultRouter()
router.register(r'tournaments', TournamentViewSet, basename='tournament')
router.register(r'adjustments', BankrollAdjustmentViewSet, basename='adjustment')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]