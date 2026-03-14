from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .csv_db import (
    get_user_by_email,
    verify_password,
    generate_token,
    save_token,
    delete_token,
    email_exists,
    create_user
)
from smartbank.authentication import CSVTokenAuthentication


# ─────────────────────────────────────────
#  POST /api/auth/login/
# ─────────────────────────────────────────
class LoginView(APIView):
    authentication_classes = []  # no auth needed to login

    def post(self, request):
        email    = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()

        # 1. Check both fields provided
        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Find user by email
        user = get_user_by_email(email)
        if not user:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 3. Verify password
        if not verify_password(password, user['password_hash']):
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # 4. Generate token and save it
        token = generate_token()
        save_token(token, user['user_id'])

        # 5. Return token + user info (never return password_hash)
        return Response({
            'token': token,
            'user': {
                'id':    user['user_id'],
                'name':  user['name'],
                'email': user['email'],
                'role':  user['role'],
            }
        }, status=status.HTTP_200_OK)


# ─────────────────────────────────────────
#  POST /api/auth/register/
# ─────────────────────────────────────────
class RegisterView(APIView):
    authentication_classes = []  # no auth needed to register

    def post(self, request):
        name     = request.data.get('name', '').strip()
        email    = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        cnic     = request.data.get('cnic', '').strip()

        # 1. Check all fields provided
        if not name or not email or not password or not cnic:
            return Response(
                {'error': 'All fields are required: name, email, password, cnic.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Validate CNIC — must be exactly 13 digits
        if not cnic.isdigit() or len(cnic) != 13:
            return Response(
                {'error': 'CNIC must be exactly 13 digits.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Validate password length
        if len(password) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Check email not already used
        if email_exists(email):
            return Response(
                {'error': 'An account with this email already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 5. Create the user (also creates empty statement CSV)
        create_user(name, email, password, cnic)

        return Response(
            {'message': 'Registered successfully. You can now log in.'},
            status=status.HTTP_201_CREATED
        )


# ─────────────────────────────────────────
#  POST /api/auth/logout/
# ─────────────────────────────────────────
class LogoutView(APIView):
    authentication_classes = [CSVTokenAuthentication]  # must be logged in

    def post(self, request):
        # request.auth contains the token string (set by CSVTokenAuthentication)
        token = request.auth
        if token:
            delete_token(token)

        return Response(
            {'message': 'Logged out successfully.'},
            status=status.HTTP_200_OK
        )