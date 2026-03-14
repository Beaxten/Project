from django.urls import path

urlpatterns = [
    path('transfer/', TransferView.as_view()),
    path('history/',  HistoryView.as_view()),
]
