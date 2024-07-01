from firebase_connection import db
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from transactionsaver import serializers
from rest_framework import generics
from firebase_admin import auth
import requests
from.users_views import FirebaseAuthentication
from django.http import JsonResponse
from django.shortcuts import render

class SaveInstitution(generics.GenericAPIView):
    serializer_class=serializers.InstitutionSerializer
    """
    This is the endpoint of saving institution
    """
    authentication_classes=(FirebaseAuthentication,)
    def post(self,request):
     
        
        instData={
            'call_back_url':self.request.data['call_back_url'],
            'identifier':self.request.data['identifier'],
            'name':self.request.data['name'],
            'phone':self.request.data['phone'],
            'url_method':self.request.data['url_method'],
            'url_query_parameter':['phone','name','paymentNumber','paymentTime','amount','reason','SinglePurchaseAmount'],
            'active':self.request.data['active'],
            'users':[]
        }
        identif=request.data['identifier']
        inst_docs=db.collection("institutions").get()
        if len(inst_docs)==0:
            db.collection("institutions").add(instData)
        else:
            check=False
            if len(inst_docs)>0:
                for doc in inst_docs:
                    dat=doc.to_dict()
                    if identif==dat['identifier']:
                        check=True
                        break
                if check:
                    return Response(data="identifier already exist")
                else:
                    db.collection("institutions").add(instData)
                    data={'data':instData}
                    return JsonResponse(data,status=status.HTTP_201_CREATED)
class UpdateInstitution(generics.CreateAPIView):
    serializer_class = serializers.InstitutionSerializer
    authentication_classes = (FirebaseAuthentication,)

    def put(self, request, institution_id):
        url_method = 'POST'
        instData = {
            'call_back_url': request.data.get('call_back_url'),
            'identifier': request.data.get('identifier'),
            'name': request.data.get('name'),
            'phone': request.data.get('phone'),
            'url_method': url_method,
            'url_query_parameter': ['phone', 'name', 'paymentNumber', 'paymentTime', 'amount', 'reason', 'SinglePurchaseAmount'],
            'active': request.data.get('active'),
            'users': []
        }

        inst_identifier = request.data.get('identifier')
        inst_ref = db.collection("institutions").document(institution_id).get()

        if inst_ref.exists:
            data = inst_ref.to_dict()
            if inst_identifier == data.get('identifier'):
                db.collection("institutions").document(institution_id).update(instData)
                return JsonResponse(data={'data': instData}, status=status.HTTP_202_ACCEPTED)
            else:
                return JsonResponse(data={'error': 'Identifier should be unique.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse(data={'error': 'Institution not found.'}, status=status.HTTP_404_NOT_FOUND)
class GetAllInstitutions(APIView):
    # Endpoint for get all institutions
    authentication_classes=(FirebaseAuthentication,)
    def get(self,request):
        institutions_list=[]
        results=db.collection("institutions").get()
        for doc in results:
            inst_id=doc.id
            data={
                "inst_id":doc.id,
                "inst_data":doc.to_dict()
            }
            institutions_list.append(data)
        return Response(data=institutions_list,status=status.HTTP_200_OK)
    
class GetInstitutionDetails(generics.GenericAPIView):
    # endpoints for institution details
    serializer_class=serializers.InstitutionSerializer
    authentication_classes=(FirebaseAuthentication,)
    def get(self,request,inst_id):
        result=db.collection("institutions").document(inst_id).get()
        data={
             
            'inst_id': result.id,
            'inst_data':result.to_dict()
        }
        return Response(data=data,status=status.HTTP_200_OK)

def home(request):
    """
    This method is to render to home page .
    """
    return render(request,'home.html')
from django.http import HttpResponseServerError
    
def get_institutions(request):
    """
    This method is for getting all institutions and render them to institution page .
    """
    try:
        results = db.collection("institutions").get()
        context = []
        for doc in results:
            instId=doc.id
            data = doc.to_dict()
            inst_data = {
                'inst_id': doc.id,
                'name': data['name'],
                'active': data['active'],
                'identifier': data['identifier'],
                'phone': data['phone'],
            }
            context.append(inst_data)
        return render(request, 'institutions.html', {'institutions': context,'inst_id':instId})
    except Exception as e:
        print(e)
        return HttpResponseServerError("An error occurred while fetching institutions data.")
def login(request):
    """
    This method is to render to login  page .
    """
    return render(request,'login.html')

def institution_details(request, instId):
    """
    This method is for getting institution details,
    to render them to an institution details page.
    """
    results = db.collection("institutions").document(instId).get()
    data = None
    if results.exists:
        data = results.to_dict()
    return render(request, 'institution_detail.html', {'details': data, 'instId': instId})

def update_institution(request, instId):
    """
    This method is  for updating an institution 
    to render to the form of updating an institution .
    """
    response = db.collection("institutions").document(instId).get()
    resp = response.to_dict()
    data = {
        'call_back_url': resp['call_back_url'],
        'identifier': resp['identifier'],
        'name': resp['name'],
        'phone': resp['phone'],
        'url_method': resp['url_method'],
        'url_query_parameter': resp.get('url_query_parameter', []),
        'active': resp['active'],
        'users': resp.get('users', [])
    }
    return render(request, 'update_institution.html', {'data': data, 'inst_id': instId})
