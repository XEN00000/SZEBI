from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return Response({
                "status": "success",
                "user": {
                    "username": user.username,
                    "is_admin": user.is_superuser
                }
            })
        return Response({"error": "Nieprawidłowe dane logowania"}, status=status.HTTP_401_UNAUTHORIZED)