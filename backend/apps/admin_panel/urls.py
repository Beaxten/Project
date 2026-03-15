from django.urls import path
from .views import AdminUsersView, AdminAllTransactionsView , AdminFraudAlertsView

urlpatterns = [
    path('users/',        AdminUsersView.as_view()),
    path('transactions/', AdminAllTransactionsView.as_view()),
    path('fraud-alerts/', AdminFraudAlertsView.as_view()),  
]
