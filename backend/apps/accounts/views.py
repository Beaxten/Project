from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from smartbank.authentication import CSVTokenAuthentication


# ─────────────────────────────────────────
#  GET /api/account/balance/
# ─────────────────────────────────────────
class BalanceView(APIView):
    authentication_classes = [CSVTokenAuthentication]

    def get(self, request):
        user = request.user  # dict from CSV set by CSVTokenAuthentication

        return Response({
            'balance':        float(user['balance']),
            'account_number': user['account_number'],
            'name':           user['name'],
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────
#  GET /api/account/profile/
# ─────────────────────────────────────────
class ProfileView(APIView):
    authentication_classes = [CSVTokenAuthentication]

    def get(self, request):
        user = request.user  # dict from CSV

        # Return everything EXCEPT password_hash
        return Response({
            'user_id':        user['user_id'],
            'name':           user['name'],
            'email':          user['email'],
            'cnic':           user['cnic'],
            'account_number': user['account_number'],
            'account_type':   user['account_type'],
            'balance':        float(user['balance']),
            'role':           user['role'],
            'created_at':     user['created_at'],
            'is_active':      user['is_active'],
        }, status=status.HTTP_200_OK)