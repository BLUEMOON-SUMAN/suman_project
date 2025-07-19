from user.jwt_claim_serializer import TokenObtainPairSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response

from rest_framework import permissions
from rest_framework.views import APIView

class OnlyAuthenticatedUserView(APIView) :
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self,request):

        user = request.user
        print(f"user정보 : {user}")
        return Response({'message' : "Accepted"})


class TokenObtainPairView(TokenObtainPairView) :
    serializer_class = TokenObtainPairSerializer
    