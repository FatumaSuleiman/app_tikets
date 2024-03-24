from pydoc import text
from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from rest_framework import status
from . import models as pindomodels


class sendsms(APIView):
    def post(self, *args, **kwargs):
        data={
            "to":self.request.data['to'],
            "text":self.request.data['text'],
            
        }
        
        response=pindomodels.PindoSMS.sendSMS(data['to'],data['text'])
        
        
        return Response(response)