from datetime import datetime
# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from firebase_connection import db
from transactionsaver.serializers import ValidateTicketSerializer,SearchTicketByPhoneSerializer,SearchTicketByTransactionNumberSerializer
from rest_framework.generics import GenericAPIView
from transactionsaver.views.users_views import FirebaseAuthentication


class ValidateTicket(GenericAPIView):
    """
    This method is for validating a tickect, we check if the ticket has been used
    if not we mark it as used and add the time it was used(validatedAt)
    """
    serializer_class=ValidateTicketSerializer
    authentication_classes=(FirebaseAuthentication,)
    def post(self, *args, **kwargs):
        try:
            ticketNumber = self.request.data['ticketNumber']
            instId = self.request.data['instId']
            eventId=self.request.data['eventId']

            print('We are here')    
            results = db.collection('institutions').document(instId).collection('events').document(eventId).collection(
                "tickets").where('ticketNumber', '==', ticketNumber).get()
            print(results)

            if results:
                for doc in results:
                    if doc.to_dict()['valid']:
                        if doc.to_dict()['validated']:
                            response = {
                                'message': 'ticket already used',
                                'validatedAt': doc.to_dict()['validatedAt'],
                            }
                            return Response(data=response, status=status.HTTP_226_IM_USED)
                        else:
                            db.collection(u'institutions').document(instId).collection('events').document(eventId).collection("tickets").document(
                                doc.id).update({'validated': True, 'validatedAt': datetime.now()})
                            return Response(data="Ticket is validated successfully", status=status.HTTP_200_OK)

                    else:
                        return Response(data="Ticket is not Valid", status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(data="Ticket does not Exist", status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response(data="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SearchTicketByPhone(GenericAPIView):
    """
    This method is for searching ticket by payer phone or ticket owner phone
    """
    serializer_class=SearchTicketByPhoneSerializer
    authentication_classes=(FirebaseAuthentication,)
    def post(self, *args, **kwargs):
        try:
            phone = self.request.data['phone']
            instId = self.request.data['instId']
            eventId=self.request.data['eventId']

            print('We are here')    
            results = db.collection('institutions').document(instId).collection('events').document(eventId).collection(
                "tickets").get()
            print(len(results))
            tickets=[]
            if results:
                for doc in results:
                    ticket=doc.to_dict()
                    
                    
                    if ticket['phone'].strip()==phone.strip():
                        response = {
                                'amount': ticket['amount'],
                                'name': ticket['name'],
                                'paymentNumber':ticket['paymentNumber'],
                                'paymentTime':ticket['paymentTime'],
                                'phone':ticket['phone'],
                                'reason':ticket['reason'],
                                'singlePurchaseAmount':ticket['singlePurchaseAmount'],
                                'ticketCategoryId':ticket['ticketCategoryId'],
                                'ticketNumber':ticket['ticketNumber'],
                                'valid':ticket['valid'],
                                'validated':ticket['validated'],
                                'validatedAt':ticket['validatedAt'],
                                'validatedBy':ticket['validatedBy']
                            }
                        
                        tickets.append(response) 
                    else:
                        
                        #Check with ticket owner
                        if len(ticket['reason'])>0:
                            if len(ticket['reason'])>=10:
                                print(ticket['reason'])
                                if ticket['reason'].__contains__(phone):
                                    response = {
                                                    'amount': ticket['amount'],
                                                    'name': ticket['name'],
                                                    'paymentNumber':ticket['paymentNumber'],
                                                    'paymentTime':ticket['paymentTime'],
                                                    'phone':ticket['phone'],
                                                    'reason':ticket['reason'],
                                                    'singlePurchaseAmount':ticket['singlePurchaseAmount'],
                                                    'ticketCategoryId':ticket['ticketCategoryId'],
                                                    'ticketNumber':ticket['ticketNumber'],
                                                    'valid':ticket['valid'],
                                                    'validated':ticket['validated'],
                                                    'validatedAt':ticket['validatedAt'],
                                                    'validatedBy':ticket['validatedBy']
                                                }
                                    tickets.append(response)
                            else:
                                pass
                        
                    
                return Response(data=tickets, status=status.HTTP_200_OK)
            else:
                return Response(data="No tickets found", status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response(data="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SearchTicketByPaymentNumber(GenericAPIView):
    serializer_class = SearchTicketByTransactionNumberSerializer
    authentication_classes = (FirebaseAuthentication,)

    def post(self, request, *args, **kwargs):
        try:
            paymentNumber = request.data.get('paymentNumber')
            instId = request.data.get('instId')
            eventId = request.data.get('eventId')
            results = db.collection('institutions').document(instId).collection('events').document(eventId).collection("tickets").get()
            
            tickets = []
            for doc in results:
                ticket = doc.to_dict()
                if paymentNumber in ticket['paymentNumber']:
                    response = {
                        'amount': ticket['amount'],
                        'name': ticket['name'],
                        'paymentNumber': ticket['paymentNumber'],
                        'paymentTime': ticket['paymentTime'],
                        'phone': ticket['phone'],
                        'reason': ticket['reason'],
                        'singlePurchaseAmount': ticket['singlePurchaseAmount'],
                        'ticketCategoryId': ticket['ticketCategoryId'],
                        'ticketNumber': ticket['ticketNumber'],
                        'valid': ticket['valid'],
                        'validated': ticket['validated'],
                        'validatedAt': ticket['validatedAt'],
                        'validatedBy': ticket['validatedBy']
                    }
                    tickets.append(response)

            return Response(data=tickets, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(data="Internal Server Error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetValidatedTicketByPaymentNumber(GenericAPIView):
    """
    This method is for getting  validated tickets  by paymentNumber  
    """
    serializer_class=SearchTicketByTransactionNumberSerializer
    authentication_classes=(FirebaseAuthentication,)
    def post(self, *args, **kwargs):
        try:
            paymentNumber = self.request.data['paymentNumber']
            instId = self.request.data['instId']
            eventId=self.request.data['eventId']    
            results = db.collection('institutions').document(instId).collection('events').document(eventId).collection(
                "tickets").get()
            print(len(results))
            tickets=[]
            if results:
                for doc in results:
                    ticket=doc.to_dict()
                    if ticket['paymentNumber']==paymentNumber and ticket['validated']==True:
                        response = {
                                'amount': ticket['amount'],
                                'name': ticket['name'],
                                'paymentNumber':ticket['paymentNumber'],
                                'paymentTime':ticket['paymentTime'],
                                'phone':ticket['phone'],
                                'reason':ticket['reason'],
                                'singlePurchaseAmount':ticket['singlePurchaseAmount'],
                                'ticketCategoryId':ticket['ticketCategoryId'],
                                'ticketNumber':ticket['ticketNumber'],
                                'valid':ticket['valid'],
                                'validated':ticket['validated'],
                                'validatedAt':ticket['validatedAt'],
                                'validatedBy':ticket['validatedBy']
                            }
                        
                        tickets.append(response) 
                return Response(data=tickets, status=status.HTTP_200_OK)
               
            else:
                return Response(data="No tickets found", status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            print(e)
            return Response(data="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



