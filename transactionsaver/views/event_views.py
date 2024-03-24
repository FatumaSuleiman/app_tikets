from firebase_connection import db
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from transactionsaver.serializers import EventSerializer,EventDataSerializer,BuyTicketsSerializer
from django.http import JsonResponse
from transactionsaver.views.users_views import FirebaseAuthentication
from transactionsaver.views.transaction_views import create_tickets_v2,SendSMSAndSaveData_V2
from transactionsaver.views.ticket_category_views import SendSMSAndSaveData1,create_ticket
class SaveEvent(GenericAPIView):
     
    #This is the endpoint of saving Event
    serializer_class=EventSerializer
    authentication_classes=(FirebaseAuthentication,)
    def post(self,request,institution_id):
        
        eventData={
            'call_back_url':self.request.data['call_back_url'],
            'eventId':self.request.data['eventId'],
            'eventDevice':self.request.data['eventDevice'],
            'name':self.request.data['name'],
            'date':self.request.data['date'],
            'eventLocation':self.request.data['eventLocation'],
            'SinglePurchaseAmount':self.request.data['SinglePurchaseAmount'],
            'active':self.request.data['active'],
            'description':self.request.data['description'],
            'time':self.request.data['time'],
            'current_group_number':self.request.data['current_group_number'],
            'group_number_assignation_required':self.request.data['group_number_assignation_required'],
            'how_many_per_goup':self.request.data['how_many_per_goup'],
            'unfinished_group':self.request.data['unfinished_group'],
            ' unifinished_group_remaining_members':self.request.data['unifinished_group_remaining_members']
        }
        event_id=request.data['eventId']
        inst_ref=db.collection("institutions")
        docs=db.collection("institutions").document(institution_id).collection("events").get()
        if len(docs)==0:
            inst_ref.document(institution_id).collection("events").add(eventData) 
        else:
            check=False
            if len(docs)>0:
                for doc in docs:
                    data=doc.to_dict()
                    if event_id==data['eventId']:
                        check=True
                        break
                if check:
                    return Response(data="eventId already exist")
                else:
                    inst_ref=db.collection("institutions")
                    inst_ref.document(institution_id).collection("events").add(eventData)
                    return Response(data={'data':eventData},status=status.HTTP_201_CREATED)
     
class GetAllInstitutionevents(APIView):
    # Endpoint for get all events of an institution
    authentication_classes=(FirebaseAuthentication,)
    def get(self,request,inst_id):
        event_list=[]
        results=db.collection("institutions").document(inst_id).collection("events").get()
        for doc in results:
            event_id=doc.id
            data={
                "event_id":event_id,
                "event_data":doc.to_dict()
            }
            event_list.append(data)
        return Response(data=event_list,status=status.HTTP_200_OK)
    
class GetEventDetails(GenericAPIView):
    # endpoint for event details
    serializer_class=EventSerializer
    authentication_classes=(FirebaseAuthentication,)
    def get(self,request,inst_id,event_id):
        result=db.collection("institutions").document(inst_id).collection('events').document(event_id).get()
        data={
            'event_id': result.id,
            'event_data':result.to_dict()
        }
        return Response(data=data,status=status.HTTP_200_OK)
class AddTicketV3(GenericAPIView):
    serializer_class=BuyTicketsSerializer
    def post(self,request,institutionId,eventId):
        seriazed_data = BuyTicketsSerializer(data=self.request.data)
        if seriazed_data.is_valid():
            trans_obj = seriazed_data.data
            obj = seriazed_data.data
            # Find key data from referenceNumber
            referencenNumber=obj['referenceNumber']
            ticketCategoryId=referencenNumber
            trans_obj1={
                'phone':obj['senderPhone'],
                'name':obj['sender'],
                'paymentNumber':obj['transactionNumber'],
                'paymentTime':obj['transactionTime'],
                'amount':obj['amount'],
                'reason':'Buying Ticket',
                'validated':False,
                'instId':institutionId,
                'eventId':eventId,
                'ticketCategoryId':ticketCategoryId,
                'quantity':0
            }
            tickets = create_tickets_v2(trans_obj1)
            # Send data to firebase
            SendSMSAndSaveData_V2(tickets, trans_obj1, "INDIVIDUAL").start()
            # # Send sms to ticket buyer
            # SendTicketSMSs(tickets, transObj).start()

            return Response(data={"transaction":tickets})
        else:
             return Response(data={"data":seriazed_data.errors}, status=status.HTTP_400_BAD_REQUEST)
        

        