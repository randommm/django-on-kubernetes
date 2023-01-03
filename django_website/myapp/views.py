from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response

class HomePage(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(dict(
            message=f'You\'re logged as {request.user}',
        ))
