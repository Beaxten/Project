from django.urls import path
from .views import TransferView, HistoryView

urlpatterns = [
    path('transfer/', TransferView.as_view()),
    path('history/',  HistoryView.as_view()),
]
