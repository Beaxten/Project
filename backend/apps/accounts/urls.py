from django.urls import path
from .views import BalanceView, ProfileView

urlpatterns = [
    path('balance/', BalanceView.as_view(), name='balance'),
    path('profile/', ProfileView.as_view(), name='profile'),
]