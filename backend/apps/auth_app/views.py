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


class LoginView(APIView):
    authentication_classes = []  

    def post(self, request):
        email    = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()

        if not email or not password:
            return Response(
                {'error': 'Email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_user_by_email(email)
        if not user:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not verify_password(password, user['password_hash']):
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token = generate_token()
        save_token(token, user['user_id'])

        return Response({
            'token': token,
            'user': {
                'id':    user['user_id'],
                'name':  user['name'],
                'email': user['email'],
                'role':  user['role'],
            }
        }, status=status.HTTP_200_OK)


class RegisterView(APIView):
    authentication_classes = []  

    def post(self, request):
        name     = request.data.get('name', '').strip()
        email    = request.data.get('email', '').strip()
        password = request.data.get('password', '').strip()
        cnic     = request.data.get('cnic', '').strip()

        if not name or not email or not password or not cnic:
            return Response(
                {'error': 'All fields are required: name, email, password, cnic.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cnic.isdigit() or len(cnic) != 13:
            return Response(
                {'error': 'CNIC must be exactly 13 digits.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(password) < 6:
            return Response(
                {'error': 'Password must be at least 6 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if email_exists(email):
            return Response(
                {'error': 'An account with this email already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        create_user(name, email, password, cnic)

        return Response(
            {'message': 'Registered successfully. You can now log in.'},
            status=status.HTTP_201_CREATED
        )


class LogoutView(APIView):
    authentication_classes = [CSVTokenAuthentication]  # must be logged in

    def post(self, request):
        token = request.auth
        if token:
            delete_token(token)

        return Response(
            {'message': 'Logged out successfully.'},
            status=status.HTTP_200_OK
        )