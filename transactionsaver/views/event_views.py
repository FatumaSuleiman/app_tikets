from firebase_connection import db
from rest_framework import status
from pindo.models import PindoSMS
from ticket_app.settings import env
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from transactionsaver.serializers import EventSerializer,EventDataSerializer,BuyTicketsSerializer,sendSMSTicketSerializer
from django.http import JsonResponse
from transactionsaver.views.users_views import FirebaseAuthentication
from transactionsaver.views.ticket_category_views import SendSMSAndSaveData1,create_ticket
from django.http import JsonResponse
from django.shortcuts import render
class SaveEvent(GenericAPIView):
    serializer_class = EventSerializer
    authentication_classes = (FirebaseAuthentication,)

    def post(self, request, institution_id):
        eventData = {
            'call_back_url': self.request.data['call_back_url'],
            'eventID': self.request.data['eventID'],
            'eventDevice': self.request.data['eventDevice'],
            'name': self.request.data['name'],
            'date': self.request.data['date'],
            'eventLocation': self.request.data['eventLocation'],
            'singlePurchaseAmount': self.request.data['singlePurchaseAmount'],
            'active': self.request.data['active'],
            'description': self.request.data['description'],
            'time': self.request.data['time'],
            'current_group_number': self.request.data['current_group_number'],
            'group_number_assignation_required': self.request.data['group_number_assignation_required'],
            'how_many_per_group': self.request.data['how_many_per_group'],
            'unfinished_group': self.request.data['unfinished_group'],
            'unfinished_group_remaining_members': self.request.data['unfinished_group_remaining_members'],
            'momoCode': self.request.data['momoCode']
        }

        event_id = request.data['eventID']
        inst_ref = db.collection("institutions")
        docs = db.collection("institutions").document(institution_id).collection("events").get()

        if len(docs) == 0:
            inst_ref.document(institution_id).collection("events").add(eventData)
            return JsonResponse({'data': eventData}, status=status.HTTP_201_CREATED)
        else:
            check = False
            for doc in docs:
                data = doc.to_dict()
                if event_id == data['eventID']:
                    check = True
                    break

            if check:
                return Response(data="eventId already exists", status=status.HTTP_400_BAD_REQUEST)
            else:
                inst_ref.document(institution_id).collection("events").add(eventData)
                return JsonResponse({'data': eventData}, status=status.HTTP_201_CREATED)
     
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
class UpdateInstitutionEvent(GenericAPIView):
    """
    This is the endpoint for updating event
    """
    serializer_class = EventSerializer
    authentication_classes = (FirebaseAuthentication,)
import logging

class UpdateInstitutionEvent(GenericAPIView):
    # This is the endpoint of updating event
    serializer_class=EventSerializer
    authentication_classes=(FirebaseAuthentication,)

    def put(self, request, inst_id, event_id):
        try:
            # Ensure logging is configured
            logging.basicConfig(level=logging.DEBUG)

            eventId = request.data.get('eventID')
            if not eventId:
                return Response(data="eventID is required", status=status.HTTP_400_BAD_REQUEST)

            # Log the request data
            logging.debug(f"Request data: {request.data}")

            eventData = {
                'call_back_url': request.data.get('call_back_url'),
                'eventID': request.data.get('eventID'),
                'eventDevice': request.data.get('eventDevice'),
                'name': request.data.get('name'),
                'date': request.data.get('date'),
                'eventLocation': request.data.get('eventLocation'),
                'singlePurchaseAmount': request.data.get('singlePurchaseAmount'),
                'active': request.data.get('active'),
                'description': request.data.get('description'),
                'time': request.data.get('time'),
                'current_group_number': request.data.get('current_group_number'),
                'group_number_assignation_required': request.data.get('group_number_assignation_required'),
                'how_many_per_group': request.data.get('how_many_per_group'),
                'unfinished_group': request.data.get('unfinished_group'),
                'unfinished_group_remaining_members': request.data.get('unfinished_group_remaining_members'),
                'momoCode': request.data.get('momoCode')
            }

            if eventData['singlePurchaseAmount'] is None:
                return Response(data="singlePurchaseAmount is required", status=status.HTTP_400_BAD_REQUEST)
            event_d = db.collection("institutions").document(inst_id).collection("events").document(event_id).get()
            if event_d.exists:
                data = event_d.to_dict()
                if  eventId == data['eventID']:
                    event_up=db.collection("institutions").document(inst_id).collection("events").document(event_id)
                    event_up.update(eventData)
                    return Response(data={'data': eventData}, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response(data={'data': 'eventID should be unique'})

        except Exception as e:
            logging.error(f"Error occurred: {e}")
            return Response(data={'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
def institution_events(request,institution_id):
    """
    This method is for getting all  events  of institution and render them to the Events page .
    """
    results=db.collection("institutions").document(institution_id).collection("events").get()
    context=[]
    for doc in results:
        event_id=doc.id 
        event_data=doc.to_dict()
        data={
            'event_id':event_id,
            'name':event_data['name'],
            'eventID':event_data['eventID'],
            'eventDevice':event_data['eventDevice'],
            'eventLocation':event_data['eventLocation'],
            'date':event_data['date'],
            'time':event_data['time'],
            'active':event_data['active']

        }
        context.append(data)
        
    return render(request,'institution_events.html',{'events':context,'institution_id':institution_id})

def get_institution_event_detail(request, inst_id, event_id):
    """
      This method is for getting an event details  of an  institution and render them to the Event details page .
    """
    response = db.collection("institutions").document(inst_id).collection("events").document(event_id).get()
    data = None
    if response.exists:
        data = response.to_dict()
    return render(request, 'institution_event_details.html', {'event_data': data, 'inst_id': inst_id, 'event_id': event_id})

def update_institution_events(request, inst_id, event_id):
    """
    This method is for updating   events  of an  institution and render them to 
    the form of updating an event  .
    """
    # Get the event document
    response = db.collection("institutions").document(inst_id).collection("events").document(event_id).get()
    
    if not response.exists:
        return render(request, 'update_institution_events.html', {'error': 'Event not found', 'inst_id': inst_id, 'event_id': event_id})
    
    resp = response.to_dict()

    data = {
        'name': resp.get('name', ''),
        'eventID': resp.get('eventID', ''),
        'eventDevice': resp.get('eventDevice', ''),
        'eventLocation': resp.get('eventLocation', ''),
        'description': resp.get('description', ''),
        'date': resp.get('date', ''),
        'time': resp.get('time', ''),
        'momoCode': resp.get('momoCode', ''),
        'singlePurchaseAmount': resp.get('singlePurchaseAmount', ''),
        'current_group_number': resp.get('current_group_number', ''),
        'unfinished_group': resp.get('unfinished_group', ''),
        'unfinished_group_remaining_members': resp.get('unfinished_group_remaining_members', ''),
        'group_number_assignation_required': resp.get('group_number_assignation_required', ''),
        'call_back_url': resp.get('call_back_url', ''),
        'how_many_per_group': resp.get('how_many_per_group', ''),
        'active': resp.get('active', False)
    }

    return render(request, 'update_institution_events.html', {'data': data, 'inst_id': inst_id, 'event_id': event_id})
class SendSMSTicket(GenericAPIView):
    serializer_class=sendSMSTicketSerializer
    authentication_classes = (FirebaseAuthentication,)
    def post(self, request, *args, **kwargs):
        ticketNumber = request.data.get('ticketNumber')
        instId = request.data.get('instId')
        eventId = request.data.get('eventId')
        
        inst_identifier = ''
        event_name = ''
        eventID = ''
        telephone = ''
        phone = ''
    
        inst_doc = db.collection("institutions").document(instId).get()
        if inst_doc.exists:
            doc = inst_doc.to_dict()
            inst_identifier = doc.get('identifier')
        
        event_doc = db.collection("institutions").document(instId).collection("events").document(eventId).get()
        if event_doc.exists:
            doc = event_doc.to_dict()
            event_name = doc.get('name')
            eventID = doc.get('eventID')
        
        tickets = db.collection("institutions").document(instId).collection("events").document(eventId).collection("tickets").get()
        if tickets:
            for ticket in tickets:
                ticket_data = ticket.to_dict()
                ticketNumber = ticket_data.get('ticketNumber')
                telephone = ticket_data.get('phone')

        msg = f'You have received a ticket for {event_name}. Click here to access your ticket: {env("NOKANDA_TICKET_APP_URL")}{inst_identifier}/{eventID}/{ticketNumber}'
        
        if telephone:
            if "+25" in telephone:
                phone = telephone
            else:
                if telephone[:2] == "25":
                    phone = "+" + str(telephone)
                else:
                    phone = "+25" + str(telephone)
        
        response = PindoSMS.sendSMS(phone, msg)
        return Response(data={'data': response})
        



