from firebase_connection import db
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from transactionsaver import serializers
from rest_framework import generics
from firebase_admin import auth
import requests
from.users_views import FirebaseAuthentication

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
                    return Response(data={'data':instData},status=status.HTTP_201_CREATED)
 
class UpdateInstitution(generics.GenericAPIView):
    serializer_class=serializers.InstitutionSerializer
    """
    This is the endpoint for updating institution
    """
    authentication_classes=(FirebaseAuthentication,)
    def put(self,request,institution_id):
       
        url_method='POST'
        instData={
             'call_back_url':self.request.data['call_back_url'],
            'identifier':self.request.data['identifier'],
            'name':self.request.data['name'],
            'phone':self.request.data['phone'],
            'url_method':url_method,
            'url_query_parameter':['phone','name','paymentNumber','paymentTime','amount','reason','SinglePurchaseAmount'],
            'active':self.request.data['active'],
            'users':[]

        }
        db.collection("institutions").document(institution_id).update(instData)
        return Response(data={'data':instData},status=status.HTTP_202_ACCEPTED)
    
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
