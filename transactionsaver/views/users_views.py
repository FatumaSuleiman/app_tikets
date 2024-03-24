from firebase_connection import db
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from transactionsaver.serializers import UserSerializer,PasswordUserSerializer
from firebase_admin import auth
from django.http import HttpResponse,JsonResponse
import requests
from rest_framework import authentication
from ticket_app import settings
import json
from transactionsaver.views.exceptions import InvalidAuthToken

class CreateUser(GenericAPIView):
    serializer_class=UserSerializer
    def post(self,request):
        email=request.data['email']
        password=request.data['email']
        try:
            user=auth.create_user(
                email=email,
                password=password
            )
            return Response(data={"message":f"user created successfully for user{user.uid}"})
        except auth.EmailAlreadyExistsError:
            return HttpResponse(status_code=400,detail=f"Account already created for the  email{email}" )

class GenerateToken(GenericAPIView):
    serializer_class = UserSerializer
    def post(self, *args, **kwargs):
        data={
            "email":self.request.data['email'],
            "password":self.request.data['password'],
            "returnSecureToken":True
        }
        r = requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=' +settings.FIREBASE,data=data)
        json = r.json()
        if 'error' in json and json['error'] is not None:
            return Response({'Error':"Invalid Username or Password"}, status.HTTP_400_BAD_REQUEST)
        else:
            data ={
                "access_token":json["idToken"],
                "refreshToken":json["refreshToken"],
                "expiresIn":json["expiresIn"],
            }
        return Response(data)
        
class FirebaseAuthentication(authentication.BaseAuthentication):

    def authenticate(self,request):
        token=request.headers.get('Authorization')
        if token is None:
            raise InvalidAuthToken("Invalid authentication token")
            # return None
        else:
            try:
                decoded_token=auth.verify_id_token(token)
                if not decoded_token is None:
                    return (decoded_token,None)
                else:
                    raise FirebaseError()
            except Exception:
                raise InvalidAuthToken("Invalid authentication token")
