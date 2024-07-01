import datetime
import math
import random
from webbrowser import get

import openpyxl
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework import generics
from firebase_connection import db
from pindo.models import PindoSMS
from ticket_app.settings import env
from transactionsaver.serializers import BuyTicketsSerializer, TicketDataSerializer,EventDataSerializer,SearchTicketBetweenDatesSerializer,SearchTicketByDateSerializer,TicketsDataSerializer
import threading
import re
import smtplib
import os
from email.message import EmailMessage
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from transactionsaver.views.users_views import FirebaseAuthentication
from datetime import date,datetime

class SendSMSAndSaveData(threading.Thread):
    def __init__(self,tickets, transObj, tr_type):
        self.tickets = tickets
        self.transObj = transObj
        self.tr_type=tr_type
        threading.Thread.__init__(self)

    def run(self):
        send_to_firebase_and_message(self.tickets,self.transObj,self.tr_type)

    def join(self, timeout=None):
        """ Stopping the thread. """
        self._stopevent.set()
        threading.Thread.join(self, timeout)


class SendSMSAndSaveData_V2(threading.Thread):
    def __init__(self,tickets, transObj, tr_type):
        self.tickets = tickets
        self.transObj = transObj
        self.tr_type=tr_type
        threading.Thread.__init__(self)

    def run(self):
        send_to_firebase_and_message_v2(self.tickets,self.transObj,self.tr_type)

    def join(self, timeout=None):
        """ Stopping the thread. """
        self._stopevent.set()
        threading.Thread.join(self, timeout)


def send_to_firebase_and_message(tickets,trans_obj,tr_type):
    """
    this is the method to save the transaction and ticket of
    a given institution (entity) to firebase and then
    send the qr message to the corresponding user.
    """

    institution_id = trans_obj['instId']
    device_id=trans_obj['deviceId']
    institution_identifier=0
    eventID=0
    eventName=''
    # find event of the institution that is using the device for paying
    event_doc = db.collection(u'institutions').document(institution_id).collection('events').where('eventDevice','==',device_id).get()
    
    # Find identifier of institution
    inst_doc=db.collection(u'institutions').document(institution_id).get()
    ins_obj=inst_doc.to_dict()
    institution_identifier=ins_obj['identifier']
    #createInstitutionTransaction(trans_obj=trans_obj, inst_id=institution_id)
    create_ticket=True
    if len(event_doc)>0:
        create_ticket=createInstitutionEventTransaction(trans_obj=trans_obj, inst_id=institution_id,event_id=event_doc[0].id)
        eventID=event_doc[0].to_dict()['eventId']
        eventName=event_doc[0].to_dict()['name']
    if create_ticket==False:
        print("We couldn't create ticket due to the transaction number that is alread exist "+trans_obj['paymentNumber'])
    reason_phone=''
    if is_email(trans_obj["reason"])==False:    
        reason_phone = get_phone_fromReason(trans_obj["reason"])
    if tr_type == "INSTITUTION" and create_ticket:
        for ticket in tickets:
            check_data = db.collection("tickets").where('paymentNumber', '==', ticket["paymentNumber"]).get()
            #if len(check_data) == 0:
            db.collection("tickets").add(ticket)
            if len(tickets) > 1:
                if ticket["phone"]!="N/A":
                    send_message(ticket["phone"], ticket["ticketNumber"], inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
            else:
                if ticket["phone"]!="N/A":
                    send_message(reason_phone, ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
    elif tr_type == "INDIVIDUAL" and create_ticket:
        #check_data = db.collection("tickets").where('paymentNumber', '==', trans_obj["paymentNumber"]).get()
        #if len(check_data) == 0: 
        for ticket in tickets:
                #createInstitutionTickets(ticket=ticket, inst_id=institution_id)
                if len(event_doc)>0:
                    createInstitutionEventTickets(ticket=ticket, inst_id=institution_id,event_id=event_doc[0].id)
                    if len(tickets) > 1:
                        if ticket["phone"]!="N/A":
                            send_message(ticket["phone"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                        
                        if len(ticket["reason"])>1:
                            send_ticket_in_email(ticket["reason"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                     
                    else:
                        if len(reason_phone)>9:
                            if ticket["phone"]!="N/A":
                                send_message(reason_phone, ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                            
                            if len(ticket["reason"])>1:
                                send_ticket_in_email(ticket["reason"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                     
                        else:
                            if ticket["phone"]!="N/A":
                                send_message(ticket["phone"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                            
                            if len(ticket["reason"])>1:
                                send_ticket_in_email(ticket["reason"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                     
    else:
        for ticket in tickets:
            if create_ticket:
                createInstitutionTickets(ticket=ticket, inst_id=institution_id)
            # db.collection("tickets").add(ticket)
            if len(tickets) > 1:
                if ticket["phone"]!="N/A" and create_ticket:
                 send_message(ticket["phone"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
            else:
                if ticket["phone"]!="N/A" and create_ticket:
                    send_message(reason_phone, ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)



def send_to_firebase_and_message_v2(tickets,trans_obj,tr_type):
    """
    this is the method to save the transaction and ticket of
    a given institution (entity) to firebase and then
    send the qr message to the corresponding user.
    """

    institution_id = trans_obj['instId']
    eventId=trans_obj['eventId']
    institution_identifier=0
    eventID=0
    eventName=''
    # find event of the institution that is using the device for paying
    event_doc = db.collection(u'institutions').document(institution_id).collection('events').where('eventID','==',eventId).get()
    
    # Find identifier of institution
    inst_doc=db.collection(u'institutions').document(institution_id).get()
    if inst_doc.exists:   
         ins_obj=inst_doc.to_dict()
         institution_identifier=ins_obj['identifier']
         print('111111111111111111111',institution_identifier)
    #createInstitutionTransaction(trans_obj=trans_obj, inst_id=institution_id)
    create_ticket=True
    if len(event_doc)>0:
        create_ticket=createInstitutionEventTransaction(trans_obj=trans_obj, inst_id=institution_id,event_id=event_doc[0].id)
        eventID=event_doc[0].to_dict()['eventID']
        eventName=event_doc[0].to_dict()['name']
    if create_ticket==False:
        print("We couldn't create ticket due to the transaction number that is alread exist"+trans_obj['paymentNumber'])
    reason_phone=''
    if is_email(trans_obj["reason"])==False:    
        reason_phone = trans_obj['phone']
    if tr_type == "INSTITUTION" and create_ticket:
        for ticket in tickets:
            check_data = db.collection("tickets").where('paymentNumber', '==', ticket["paymentNumber"]).get()
            #if len(check_data) == 0:
            db.collection("tickets").add(ticket)
            if len(tickets) > 1:
                if ticket["phone"]!="N/A":
                    send_message(ticket["phone"], ticket["ticketNumber"], inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
            else:
                if ticket["phone"]!="N/A":
                    send_message(reason_phone, ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
    elif tr_type == "INDIVIDUAL" and create_ticket:
        #check_data = db.collection("tickets").where('paymentNumber', '==', trans_obj["paymentNumber"]).get()
        #if len(check_data) == 0: 
        for ticket in tickets:
                #createInstitutionTickets(ticket=ticket, inst_id=institution_id)
                if len(event_doc)>0:
                    createInstitutionEventTickets(ticket=ticket, inst_id=institution_id,event_id=event_doc[0].id)
                    if len(tickets) > 1:
                        if ticket["phone"]!="N/A":
                            send_message(ticket["phone"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                        
                        if len(ticket["reason"])>1:
                            send_ticket_in_email(ticket["reason"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                     
                    else:
                        if len(reason_phone)>9:
                            if ticket["phone"]!="N/A":
                                send_message(reason_phone, ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                            
                            if len(ticket["reason"])>1:
                                send_ticket_in_email(ticket["reason"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                     
                        else:
                            if ticket["phone"]!="N/A":
                                send_message(ticket["phone"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                            
                            if len(ticket["reason"])>1:
                                send_ticket_in_email(ticket["reason"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
                     
    else:
        for ticket in tickets:
            if create_ticket:
                createInstitutionTickets(ticket=ticket, inst_id=institution_id)
            # db.collection("tickets").add(ticket)
            if len(tickets) > 1:
                if ticket["phone"]!="N/A" and create_ticket:
                 send_message(ticket["phone"], ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)
            else:
                if ticket["phone"]!="N/A" and create_ticket:
                    send_message(reason_phone, ticket["ticketNumber"],inst_identifier=institution_identifier,event_id=eventID,event_name=eventName)




def send_to_firebase_and_message1(tickets,trans_obj,tr_type,number_of_allowed_ticket):

    reason_phone = get_phone_fromReason(trans_obj["reason"])
    if tr_type == "INSTITUTION":
        for ticket in tickets:
            check_data = db.collection("tickets").where('paymentNumber', '==', ticket["paymentNumber"]).get()
            if number_of_allowed_ticket> len(check_data) :
                db.collection("tickets").add(ticket)
                if len(tickets) > 1:
                    send_message(ticket["phone"], ticket["ticketNumber"])
                else:
                    send_message(trans_obj["phone"], ticket["ticketNumber"])
                        # Send message to reason phone
                    #send_message(reason_phone, ticket["ticketNumber"])
    elif tr_type == "INDIVIDUAL":
        check_data = db.collection("tickets").where('paymentNumber', '==', trans_obj["paymentNumber"]).get()
        if len(check_data) == 0:
            for ticket in tickets:
                db.collection("tickets").add(ticket)
                if len(tickets) > 1:
                    send_message(ticket["phone"], ticket["ticketNumber"])
                else:
                    send_message(trans_obj["phone"], ticket["ticketNumber"])
                    # Send message to reason phone
                    send_message(reason_phone, ticket["ticketNumber"])
    else:
        for ticket in tickets:
            db.collection("tickets").add(ticket)
            if len(tickets) > 1:
                send_message(ticket["phone"], ticket["ticketNumber"])
            else:
                send_message(trans_obj["phone"], ticket["ticketNumber"])
                # Send message to reason phone
                send_message(reason_phone, ticket["ticketNumber"])










#
# def send_sms_to_customer(tickets, trans_obj):
#     reason_phone = get_phone_fromReason(trans_obj["reason"])
#     if len(tickets) > 1:
#         for ticket in tickets:
#             # Send message to given phone
#             send_message(ticket["phone"], ticket["ticketNumber"])
#     else:
#         send_message(trans_obj["phone"], tickets[0]["ticketNumber"])
#         # Send message to reason phone
#         send_message(reason_phone, tickets[0]["ticketNumber"])
#


def send_message(telephone, ticketNumber, inst_identifier,event_id,event_name):
    msg = f'You have received a ticket for '+event_name+' click here to access your ticket '+env("NOKANDA_TICKET_APP_URL")+''+str(inst_identifier)+'/'+event_id+'/'+ticketNumber+''

    # Prepare phone to send message to

    phone = ""
    if "+25" in telephone:
        phone = telephone
    else:
        if telephone[0:2] == "25":
            phone = "+" + str(telephone)
        else:
            phone = "+25" + str(telephone)
    response = PindoSMS.sendSMS(phone, msg)
    return response


def get_phone_fromReason(reason):
    if len(reason)>10:
        if reason[0:2] == "25":
            return reason[0:12]
        else:
            return reason[0:10]
    else:
        return reason

from datetime import datetime
def get_ticket_number():
    min_n = 12345
    max_n = 99999
    min_n = math.ceil(min_n)
    max_n = math.floor(max_n)
    ticketNumber=math.floor(random.randint(5, 10000)*(max_n - min_n + 1)+min_n)
    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    ticketNumber=str(ticketNumber)+dt_string
    check_data = db.collection("tickets").where('ticketNumber', '==', ticketNumber).get()
    if len(check_data)>0:
        get_ticket_number()
    else:
         return ticketNumber


def create_tickets(data):
    tickets = []
    # Find event on which a device is linked to and thus get single purchase amount
    institution_id = data['instId']
    device_id=data['deviceId']
    event_doc = db.collection(u'institutions').document(institution_id).collection('events').where('eventDevice','==',device_id).get()
    singlePurchaseAmount=10000

    if len(event_doc)>0:
        p_object=event_doc[0].to_dict()
        singlePurchaseAmount=int(p_object['SinglePurchaseAmount'])
        print("This is category Id")
        print(data['ticketCategoryId'])
        ticketCategoryId=int(data['ticketCategoryId'])
        #Check the category of ticket being paid and check paid amount are enough
        ticketCategory_doc = db.collection(u'institutions').document(institution_id).collection('events').document(event_doc[0].id).collection('ticket_category').where('category_id','==',data['ticketCategoryId']).get()
        valid=True    
        
        if len(ticketCategory_doc)>0:
            #There is specific ticket category
            ticketCategory_object=ticketCategory_doc[0].to_dict()
            singlePurchaseAmount=int(ticketCategory_object['amount'])
            
            if ticketCategory_object['is_group']==True:
                print("Yes it's group")
                #Ticket category is for group
                if singlePurchaseAmount>int(data['amount']):
                    valid=False
                group_quantity=0
                if ticketCategory_object['group_quantity']:
                    group_quantity=int(ticketCategory_object['group_quantity'])
                number_of_ticket=group_quantity
                

                if p_object['groupnumber_assignation_required']==True:
                    #Group/table assignation for the event is required
                    how_many_per_group=p_object['how_many_per_group']
                    unfinished_group=p_object['unfinished_group']
                    unfinished_group_remaining_members=p_object['unfinished_group_remaining_members']
                    current_group_number=p_object['current_group_number']
                    ticket_group_number=0
                    
                    new_unfinished_group=unfinished_group
                    new_unfinished_group_remaining_members=unfinished_group_remaining_members
                    new_current_group_number=current_group_number 
                    print('how_many_per_group')
                    print(how_many_per_group)
                    print('group_quantity')
                    print(group_quantity)
                    if group_quantity==how_many_per_group:
                        # The quantity of member of the group is equal 
                        # to number of people that should be in a group in this event
                        if group_quantity>unfinished_group_remaining_members:
                           ticket_group_number=current_group_number+1
                           new_current_group_number=ticket_group_number
                        elif group_quantity<unfinished_group_remaining_members:
                            ticket_group_number=unfinished_group
                            new_unfinished_group_remaining_members=new_unfinished_group_remaining_members-group_quantity
                        else:
                            new_current_group_number=new_current_group_number+1
                            ticket_group_number=unfinished_group
                            new_unfinished_group=new_current_group_number
                            new_unfinished_group_remaining_members=how_many_per_group

                        
                    elif group_quantity>how_many_per_group:
                        # The quantity of member of the group is greater 
                        # to number of people that should be in a group in this event
                        pass
                    else:
                        # The quantity of member of the group is less 
                        # to number of people that should be in a group in this event
                        if group_quantity>unfinished_group_remaining_members:
                           ticket_group_number=current_group_number+1
                           new_current_group_number=ticket_group_number
                        elif group_quantity<unfinished_group_remaining_members:
                            ticket_group_number=unfinished_group
                            new_unfinished_group_remaining_members=new_unfinished_group_remaining_members-group_quantity
                        else:
                            ticket_group_number=unfinished_group
                            new_unfinished_group=new_current_group_number
                            new_unfinished_group_remaining_members=how_many_per_group
                    
                    # Creating ticket

                    # If it's free ticket
                    if ticketCategory_object['is_free']==True:
                        number_of_ticket=int(float(data['quantity']))

                    if number_of_ticket == 1:
                        # if len(ticketCategory_doc)>0:
                        #     ticketCategory_object=ticketCategory_doc.to_dict()
                        #     if int(ticketCategory_object['amount'])>int(data['amount']):
                        #         valid=False
                        

                        ticket_obj = {
                            "amount": data['amount'],
                            "name": data["name"],
                            "paymentNumber": data["paymentNumber"],
                            "paymentTime": data["paymentTime"],
                            "phone": data["phone"],
                            "reason": data["reason"],
                            "validatedAt": "",
                            'ticketNumber': str(get_ticket_number()),
                            'singlePurchaseAmount': singlePurchaseAmount,
                            'validated':False,
                            'validatedBy':'',
                            'ticketCategoryId':data['ticketCategoryId'],
                            'valid':valid,
                            'ticket_group_number':ticket_group_number
                        }
                        tickets.append(ticket_obj)
                    else:
                        for i in range(0, number_of_ticket):
                           # if int(data['amount'])/(singlePurchaseAmount*(i+1))<1:
                            #    valid=False

                            ticket_obj = {
                                "amount": singlePurchaseAmount,
                                "name": data["name"],
                                "paymentNumber": data["paymentNumber"],
                                "paymentTime": data["paymentTime"],
                                "phone": data["phone"],
                                #"reason": get_phone_fromReason(data["reason"]),
                                "reason": data["reason"],
                                "validatedAt": "",
                                'ticketNumber': str(get_ticket_number()),
                                'singlePurchaseAmount':singlePurchaseAmount,
                                'validated':False,
                                'validatedBy':'',
                                'ticketCategoryId':data['ticketCategoryId'],
                                'valid':valid,
                                'ticket_group_number':ticket_group_number
                            }
                            tickets.append(ticket_obj)


                    db.collection(u'institutions').document(institution_id).collection('events').document(event_doc[0].id).update({'current_group_number':new_current_group_number,'unfinished_group':new_unfinished_group,'unfinished_group_remaining_members':new_unfinished_group_remaining_members})
                else:

                    #Group/table assignation for the event is not required
                    # if it's for free ticket
                    if ticketCategory_object['is_free']==True:
                        number_of_ticket=int(float(data['quantity']))


                    if number_of_ticket == 1:
                        # if len(ticketCategory_doc)>0:
                        #     ticketCategory_object=ticketCategory_doc.to_dict()
                        #     if int(ticketCategory_object['amount'])>int(data['amount']):
                        #         valid=False
                        

                        ticket_obj = {
                            "amount": data['amount'],
                            "name": data["name"],
                            "paymentNumber": data["paymentNumber"],
                            "paymentTime": data["paymentTime"],
                            "phone": data["phone"],
                            "reason": data["reason"],
                            "validatedAt": "",
                            'ticketNumber': str(get_ticket_number()),
                            'singlePurchaseAmount': singlePurchaseAmount,
                            'validated':False,
                            'validatedBy':'',
                            'ticketCategoryId':data['ticketCategoryId'],
                            'valid':valid
                        }
                        tickets.append(ticket_obj)
                    else:
                        for i in range(0, number_of_ticket):
                           # if int(data['amount'])/(singlePurchaseAmount*(i+1))<1:
                            #    valid=False

                            ticket_obj = {
                                "amount": singlePurchaseAmount,
                                "name": data["name"],
                                "paymentNumber": data["paymentNumber"],
                                "paymentTime": data["paymentTime"],
                                "phone": data["phone"],
                                "reason": get_phone_fromReason(data["reason"]),
                                "validatedAt": "",
                                'ticketNumber': str(get_ticket_number()),
                                'singlePurchaseAmount':singlePurchaseAmount,
                                'validated':False,
                                'validatedBy':'',
                                'ticketCategoryId':data['ticketCategoryId'],
                                'valid':valid
                            }
                            tickets.append(ticket_obj)

                
            else:

                # Ticket category is not for group/table
                if singlePurchaseAmount <= 1 or singlePurchaseAmount > data['amount']:
                    number_of_ticket = 1
                else:
                    number_of_ticket = int(data['amount'] / singlePurchaseAmount)

                if number_of_ticket<1:
                    number_of_ticket=1 

                # if it's for free ticket
                if ticketCategory_object['is_free']==True:
                        number_of_ticket=int(float(data['quantity']))

                if number_of_ticket == 1:
                    # if len(ticketCategory_doc)>0:
                    #     ticketCategory_object=ticketCategory_doc.to_dict()
                    #     if int(ticketCategory_object['amount'])>int(data['amount']):
                    #         valid=False
                    if singlePurchaseAmount>int(data['amount']):
                        valid=False

                    ticket_obj = {
                        "amount": data['amount'],
                        "name": data["name"],
                        "paymentNumber": data["paymentNumber"],
                        "paymentTime": data["paymentTime"],
                        "phone": data["phone"],
                        "reason": data["reason"],
                        "validatedAt": "",
                        'ticketNumber': str(get_ticket_number()),
                        'singlePurchaseAmount': singlePurchaseAmount,
                        'validated':False,
                        'validatedBy':'',
                        'ticketCategoryId':data['ticketCategoryId'],
                        'valid':valid
                    }
                    tickets.append(ticket_obj)
                else:
                    for i in range(0, number_of_ticket):
                        if int(data['amount'])/(singlePurchaseAmount*(i+1))<1:
                            if ticketCategory_object['is_free']==False:
                                valid=False

                        ticket_obj = {
                            "amount": singlePurchaseAmount,
                            "name": data["name"],
                            "paymentNumber": data["paymentNumber"],
                            "paymentTime": data["paymentTime"],
                            "phone": data["phone"],
                            "reason": get_phone_fromReason(data["reason"]),
                            "validatedAt": "",
                            'ticketNumber': str(get_ticket_number()),
                            'singlePurchaseAmount':singlePurchaseAmount,
                            'validated':False,
                            'validatedBy':'',
                            'ticketCategoryId':data['ticketCategoryId'],
                            'valid':valid
                        }
                        tickets.append(ticket_obj)
        else:
            # there is no specific ticket category
            if singlePurchaseAmount <= 1 or singlePurchaseAmount > data['amount']:
                number_of_ticket = 1
            else:
                number_of_ticket = int(data['amount'] / singlePurchaseAmount)

            if number_of_ticket<1:
                number_of_ticket=1 

            if number_of_ticket == 1:
                # if len(ticketCategory_doc)>0:
                #     ticketCategory_object=ticketCategory_doc.to_dict()
                #     if int(ticketCategory_object['amount'])>int(data['amount']):
                #         valid=False
                if singlePurchaseAmount>int(data['amount']):
                    valid=False

                ticket_obj = {
                    "amount": data['amount'],
                    "name": data["name"],
                    "paymentNumber": data["paymentNumber"],
                    "paymentTime": data["paymentTime"],
                    "phone": data["phone"],
                    "reason": data["reason"],
                    "validatedAt": "",
                    'ticketNumber': str(get_ticket_number()),
                    'singlePurchaseAmount': singlePurchaseAmount,
                    'validated':False,
                    'validatedBy':'',
                    'ticketCategoryId':data['ticketCategoryId'],
                    'valid':valid
                }
                tickets.append(ticket_obj)
            else:
                for i in range(0, number_of_ticket):
                    if int(data['amount'])/(singlePurchaseAmount*(i+1))<1:
                        valid=False

                    ticket_obj = {
                        "amount": singlePurchaseAmount,
                        "name": data["name"],
                        "paymentNumber": data["paymentNumber"],
                        "paymentTime": data["paymentTime"],
                        "phone": data["phone"],
                        "reason": get_phone_fromReason(data["reason"]),
                        "validatedAt": "",
                        'ticketNumber': str(get_ticket_number()),
                        'singlePurchaseAmount':singlePurchaseAmount,
                        'validated':False,
                        'validatedBy':'',
                        'ticketCategoryId':data['ticketCategoryId'],
                        'valid':valid
                    }
                    tickets.append(ticket_obj)


    return tickets


def create_tickets_v2(data):
    tickets = []
    # Find event on which a device is linked to and thus get single purchase amount
    institution_id = data['instId']
    eventId=data['eventId']
    event_doc = db.collection(u'institutions').document(institution_id).collection('events').where('eventID','==',eventId).get()
    singlePurchaseAmount=10000
    print(data)
    print(event_doc)
    if len(event_doc)>0:
        p_object=event_doc[0].to_dict()
        singlePurchaseAmount=int(p_object['singlePurchaseAmount'])
        print("This is category Id")
        print(data['ticketCategoryId'])
        ticketCategoryId=int(data['ticketCategoryId'])
        #Check the category of ticket being paid and check paid amount are enough
        ticketCategory_doc = db.collection(u'institutions').document(institution_id).collection('events').document(event_doc[0].id).collection('ticket_category').where('category_id','==',data['ticketCategoryId']).get()
        valid=True    
        
        if len(ticketCategory_doc)>0:
            #There is specific ticket category
            ticketCategory_object=ticketCategory_doc[0].to_dict()
            singlePurchaseAmount=int(ticketCategory_object['amount'])
            
            if ticketCategory_object['is_group']==True:
                print("Yes it's group")
                #Ticket category is for group
                if singlePurchaseAmount>int(data['amount']):
                    valid=False
                group_quantity=0
                if ticketCategory_object['group_quantity']:
                    group_quantity=int(ticketCategory_object['group_quantity'])
                number_of_ticket=group_quantity
                

                if p_object['groupnumber_assignation_required']==True:
                    #Group/table assignation for the event is required
                    how_many_per_group=p_object['how_many_per_group']
                    unfinished_group=p_object['unfinished_group']
                    unfinished_group_remaining_members=p_object['unfinished_group_remaining_members']
                    current_group_number=p_object['current_group_number']
                    ticket_group_number=0
                    
                    new_unfinished_group=unfinished_group
                    new_unfinished_group_remaining_members=unfinished_group_remaining_members
                    new_current_group_number=current_group_number 
                    print('how_many_per_group')
                    print(how_many_per_group)
                    print('group_quantity')
                    print(group_quantity)
                    if group_quantity==how_many_per_group:
                        # The quantity of member of the group is equal 
                        # to number of people that should be in a group in this event
                        if group_quantity>unfinished_group_remaining_members:
                           ticket_group_number=current_group_number+1
                           new_current_group_number=ticket_group_number
                        elif group_quantity<unfinished_group_remaining_members:
                            ticket_group_number=unfinished_group
                            new_unfinished_group_remaining_members=new_unfinished_group_remaining_members-group_quantity
                        else:
                            new_current_group_number=new_current_group_number+1
                            ticket_group_number=unfinished_group
                            new_unfinished_group=new_current_group_number
                            new_unfinished_group_remaining_members=how_many_per_group

                        
                    elif group_quantity>how_many_per_group:
                        # The quantity of member of the group is greater 
                        # to number of people that should be in a group in this event
                        pass
                    else:
                        # The quantity of member of the group is less 
                        # to number of people that should be in a group in this event
                        if group_quantity>unfinished_group_remaining_members:
                           ticket_group_number=current_group_number+1
                           new_current_group_number=ticket_group_number
                        elif group_quantity<unfinished_group_remaining_members:
                            ticket_group_number=unfinished_group
                            new_unfinished_group_remaining_members=new_unfinished_group_remaining_members-group_quantity
                        else:
                            ticket_group_number=unfinished_group
                            new_unfinished_group=new_current_group_number
                            new_unfinished_group_remaining_members=how_many_per_group
                    
                    # Creating ticket

                    # If it's free ticket
                    if ticketCategory_object['is_free']==True:
                        number_of_ticket=int(float(data['quantity']))

                    if number_of_ticket == 1:
                        # if len(ticketCategory_doc)>0:
                        #     ticketCategory_object=ticketCategory_doc.to_dict()
                        #     if int(ticketCategory_object['amount'])>int(data['amount']):
                        #         valid=False
                        

                        ticket_obj = {
                            "amount": data['amount'],
                            "name": data["name"],
                            "paymentNumber": data["paymentNumber"],
                            "paymentTime": data["paymentTime"],
                            "phone": data["phone"],
                            "reason": data["reason"],
                            "validatedAt": "",
                            'ticketNumber': str(get_ticket_number()),
                            'singlePurchaseAmount': singlePurchaseAmount,
                            'validated':False,
                            'validatedBy':'',
                            'ticketCategoryId':data['ticketCategoryId'],
                            'valid':valid,
                            'ticket_group_number':ticket_group_number
                        }
                        tickets.append(ticket_obj)
                    else:
                        for i in range(0, number_of_ticket):
                           # if int(data['amount'])/(singlePurchaseAmount*(i+1))<1:
                            #    valid=False

                            ticket_obj = {
                                "amount": singlePurchaseAmount,
                                "name": data["name"],
                                "paymentNumber": data["paymentNumber"],
                                "paymentTime": data["paymentTime"],
                                "phone": data["phone"],
                                #"reason": get_phone_fromReason(data["reason"]),
                                "reason": data["reason"],
                                "validatedAt": "",
                                'ticketNumber': str(get_ticket_number()),
                                'singlePurchaseAmount':singlePurchaseAmount,
                                'validated':False,
                                'validatedBy':'',
                                'ticketCategoryId':data['ticketCategoryId'],
                                'valid':valid,
                                'ticket_group_number':ticket_group_number
                            }
                            tickets.append(ticket_obj)


                    db.collection(u'institutions').document(institution_id).collection('events').document(event_doc[0].id).update({'current_group_number':new_current_group_number,'unfinished_group':new_unfinished_group,'unfinished_group_remaining_members':new_unfinished_group_remaining_members})
                else:

                    #Group/table assignation for the event is not required
                    # if it's for free ticket
                    if ticketCategory_object['is_free']==True:
                        number_of_ticket=int(float(data['quantity']))


                    if number_of_ticket == 1:
                        # if len(ticketCategory_doc)>0:
                        #     ticketCategory_object=ticketCategory_doc.to_dict()
                        #     if int(ticketCategory_object['amount'])>int(data['amount']):
                        #         valid=False
                        

                        ticket_obj = {
                            "amount": data['amount'],
                            "name": data["name"],
                            "paymentNumber": data["paymentNumber"],
                            "paymentTime": data["paymentTime"],
                            "phone": data["phone"],
                            "reason": data["reason"],
                            "validatedAt": "",
                            'ticketNumber': str(get_ticket_number()),
                            'singlePurchaseAmount': singlePurchaseAmount,
                            'validated':False,
                            'validatedBy':'',
                            'ticketCategoryId':data['ticketCategoryId'],
                            'valid':valid
                        }
                        tickets.append(ticket_obj)
                    else:
                        for i in range(0, number_of_ticket):
                           # if int(data['amount'])/(singlePurchaseAmount*(i+1))<1:
                            #    valid=False

                            ticket_obj = {
                                "amount": singlePurchaseAmount,
                                "name": data["name"],
                                "paymentNumber": data["paymentNumber"],
                                "paymentTime": data["paymentTime"],
                                "phone": data["phone"],
                                "reason": get_phone_fromReason(data["reason"]),
                                "validatedAt": "",
                                'ticketNumber': str(get_ticket_number()),
                                'singlePurchaseAmount':singlePurchaseAmount,
                                'validated':False,
                                'validatedBy':'',
                                'ticketCategoryId':data['ticketCategoryId'],
                                'valid':valid
                            }
                            tickets.append(ticket_obj)

                
            else:

                # Ticket category is not for group/table
                if singlePurchaseAmount <= 1 or singlePurchaseAmount > data['amount']:
                    number_of_ticket = 1
                else:
                    number_of_ticket = int(data['amount'] / singlePurchaseAmount)

                if number_of_ticket<1:
                    number_of_ticket=1 

                # if it's for free ticket
                if ticketCategory_object['is_free']==True:
                        number_of_ticket=int(float(data['quantity']))

                if number_of_ticket == 1:
                    # if len(ticketCategory_doc)>0:
                    #     ticketCategory_object=ticketCategory_doc.to_dict()
                    #     if int(ticketCategory_object['amount'])>int(data['amount']):
                    #         valid=False
                    if singlePurchaseAmount>int(data['amount']):
                        valid=False

                    ticket_obj = {
                        "amount": data['amount'],
                        "name": data["name"],
                        "paymentNumber": data["paymentNumber"],
                        "paymentTime": data["paymentTime"],
                        "phone": data["phone"],
                        "reason": data["reason"],
                        "validatedAt": "",
                        'ticketNumber': str(get_ticket_number()),
                        'singlePurchaseAmount': singlePurchaseAmount,
                        'validated':False,
                        'validatedBy':'',
                        'ticketCategoryId':data['ticketCategoryId'],
                        'valid':valid
                    }
                    tickets.append(ticket_obj)
                else:
                    for i in range(0, number_of_ticket):
                        if int(data['amount'])/(singlePurchaseAmount*(i+1))<1:
                            if ticketCategory_object['is_free']==False:
                                valid=False

                        ticket_obj = {
                            "amount": singlePurchaseAmount,
                            "name": data["name"],
                            "paymentNumber": data["paymentNumber"],
                            "paymentTime": data["paymentTime"],
                            "phone": data["phone"],
                            "reason": get_phone_fromReason(data["reason"]),
                            "validatedAt": "",
                            'ticketNumber': str(get_ticket_number()),
                            'singlePurchaseAmount':singlePurchaseAmount,
                            'validated':False,
                            'validatedBy':'',
                            'ticketCategoryId':data['ticketCategoryId'],
                            'valid':valid
                        }
                        tickets.append(ticket_obj)
        else:
            # there is no specific ticket category
            if singlePurchaseAmount <= 1 or singlePurchaseAmount > data['amount']:
                number_of_ticket = 1
            else:
                number_of_ticket = int(data['amount'] / singlePurchaseAmount)

            if number_of_ticket<1:
                number_of_ticket=1 

            if number_of_ticket == 1:
                # if len(ticketCategory_doc)>0:
                #     ticketCategory_object=ticketCategory_doc.to_dict()
                #     if int(ticketCategory_object['amount'])>int(data['amount']):
                #         valid=False
                if singlePurchaseAmount>int(data['amount']):
                    valid=False

                ticket_obj = {
                    "amount": data['amount'],
                    "name": data["name"],
                    "paymentNumber": data["paymentNumber"],
                    "paymentTime": data["paymentTime"],
                    "phone": data["phone"],
                    "reason": data["reason"],
                    "validatedAt": "",
                    'ticketNumber': str(get_ticket_number()),
                    'singlePurchaseAmount': singlePurchaseAmount,
                    'validated':False,
                    'validatedBy':'',
                    'ticketCategoryId':data['ticketCategoryId'],
                    'valid':valid
                }
                tickets.append(ticket_obj)
            else:
                for i in range(0, number_of_ticket):
                    if int(data['amount'])/(singlePurchaseAmount*(i+1))<1:
                        valid=False

                    ticket_obj = {
                        "amount": singlePurchaseAmount,
                        "name": data["name"],
                        "paymentNumber": data["paymentNumber"],
                        "paymentTime": data["paymentTime"],
                        "phone": data["phone"],
                        "reason": get_phone_fromReason(data["reason"]),
                        "validatedAt": "",
                        'ticketNumber': str(get_ticket_number()),
                        'singlePurchaseAmount':singlePurchaseAmount,
                        'validated':False,
                        'validatedBy':'',
                        'ticketCategoryId':data['ticketCategoryId'],
                        'valid':valid
                    }
                    tickets.append(ticket_obj)


    return tickets



class AddTicket(generics.GenericAPIView):
    serializer_class=TicketsDataSerializer
    def post(self,request):
        seriazed_data = TicketsDataSerializer(data=self.request.data)
        if seriazed_data.is_valid():
            trans_obj = seriazed_data.data
            tickets = create_tickets(trans_obj)
            # Send data to firebase
            SendSMSAndSaveData(tickets, trans_obj, "INDIVIDUAL").start()

            # # Send sms to ticket buyer
            # SendTicketSMSs(tickets, transObj).start()

            return Response(data={"transaction":tickets})

        else:
            return Response(data={"data":seriazed_data.errors}, status=status.HTTP_400_BAD_REQUEST)
class Testing(APIView):

    def post(self,request):
        
        event_doc = db.collection(u'institutions').document("SKDL2pgPj2YPGHVcgIlc").collection('events').where('eventDevice','==',"QP1A.190711.020").get()
        inst_doc=db.collection(u'institutions').document("SKDL2pgPj2YPGHVcgIlc").get()
        ins_obj=inst_doc.to_dict()
        print(ins_obj['identifier'])
        singlePurchaseAmount=0
        results = db.collection('institutions').document('SKDL2pgPj2YPGHVcgIlc').collection('events').document('HZIOQoxuoVIb8Gy7vsGX').collection(
                "tickets").where('ticketNumber', '==', '1275042063392698').get()

        reason_phone='078338'
        print('-------------')
        print(len(reason_phone))
        print(results[0].to_dict())
        ticketCategory_doc = db.collection(u'institutions').document('SKDL2pgPj2YPGHVcgIlc').collection('events').document('HZIOQoxuoVIb8Gy7vsGX').collection('ticket_category').where('category_id','==','03').get()
        print(ticketCategory_doc[0].to_dict())

        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, 'suleima@hexakomb.com')):
            print("Valid Email")
        else:
            print('Invalid Email')

        if len(event_doc)>0:
            p_object=event_doc[0].to_dict()
            singlePurchaseAmount=int(p_object['SinglePurchaseAmount'])
            return Response(data={"transaction":singlePurchaseAmount})

        

        
import collections
from datetime import datetime
class FindDuplicate(APIView):

    def post(self,request):
        
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y%H%M%S")
        #print(get_ticket_number())
        results = db.collection('institutions').document('Mlkxodkn0sTiA6m0ABKl').collection('events').document('3hhCZyJoVbZVCTTc9pOK').collection(
                 "tickets").get()
        alltickets=[]
        for r in results:
            ticket=r.to_dict()
            alltickets.append(ticket['ticketNumber'])
            if ticket['ticketNumber'].__contains__('5463619388097257'):
                print(ticket['ticketNumber'])

        # # duplicates=[]
        # # for ticket in alltickets:
        # #     for t in alltickets:
        # #         if ticket['ticketNumber']==t['ticketNumber']:
        # #             duplicates.append(ticket)

        print([item for item, count in collections.Counter(alltickets).items() if count > 1])    
        #print(len(results))
        return Response(data={"tickets":alltickets,"number of duplicates":len(alltickets)})

    


def get_phone(reason):
    if len(reason)>10:
        if reason[0:2] == "25":
            return reason[2:12]
        elif reason[0:3] == "+25":
            return reason[3:12]
        else:
            return reason[0:11]



class GenerateTicket(APIView):

    def get(self, *args, **kwargs):
        collection = db.collection('institutions').document('yZpzD8LoPDFSq4GHzw0g').collection('transactions')
        tickets = []
        for doc in collection.stream():
            docObj = doc.to_dict()
            mytickets=[]
            amountPaid= int(docObj['amountPaid'])
            singlePurchaseAmount=10000
            number_of_ticket=1
            if singlePurchaseAmount <= 1 or singlePurchaseAmount > amountPaid:
                number_of_ticket = 1
            else:
                 number_of_ticket = int(amountPaid / singlePurchaseAmount)
            if number_of_ticket>1:
                #print(doc.id)
                #print(number_of_ticket)
                #print(get_phone(docObj["payerPhoneNumber"]))
                print('-----------------')
            if number_of_ticket==1:
                ticket_obj = {
                "amount": 10000,
                "name": docObj['payerNames'],
                "paymentNumber": docObj["transactionNumber"],
                "paymentTime": docObj["paymentDate"],
                "phone": get_phone(docObj["payerPhoneNumber"]),
                "reason": get_phone(docObj["reason"]),
                "validatedAt": "",
                'ticketNumber': str(get_ticket_number()),
                'singlePurchaseAmount':singlePurchaseAmount,
                'validated':False
                }
                tickets.append(ticket_obj)
                mytickets.append(ticket_obj)
            else:
                # if number_of_ticket>1:
                #     number_of_ticket=number_of_ticket-1
                #     print("We are here");   
                #     print(number_of_ticket) 
                for i in range(0, number_of_ticket):
                    ticket_obj = {
                    "amount": 10000,
                    "name": docObj['payerNames'],
                    "paymentNumber": docObj["transactionNumber"],
                    "paymentTime": docObj["paymentDate"],
                    "phone": get_phone(docObj["payerPhoneNumber"]),
                    "reason": get_phone(docObj["reason"]),
                    "validatedAt": "",
                    'ticketNumber': str(get_ticket_number()),
                    'singlePurchaseAmount':singlePurchaseAmount,
                    'validated':False
                    }
                    mytickets.append(ticket_obj)
                    tickets.append(ticket_obj)
            if number_of_ticket>0: 
                print(get_phone(docObj["payerPhoneNumber"]))
                print('-----------------')
                send_to_firebase_and_message1(mytickets,docObj,"INSTITUTION",number_of_ticket)       
                print(len(mytickets))            
            

        #SendSMSAndSaveData(tickets, docObj, "INSTITUTION").start()

        return Response(data=tickets)

class GenerateTicket1(APIView):

    def get(self, *args, **kwargs):
        collection = db.collection('tickets')
        tickets = []
        for doc in collection.stream():
            docObj = doc.to_dict()
            print("djuma")
            print(doc.id)
            #if doc.id=='AWIK8TlGSF8W8ph3afGP':
            try:
                db.collection(u'tickets').document(doc.id).update({'validated':False})
            except ValueError as e:
                print(e)    
                
        #SendSMSAndSaveData(tickets, docObj, "INSTITUTION").start()

        return Response(data=tickets)


from datetime import datetime
class GenerateTicketsFromExcel(APIView):

    def post(self,request):
        tickets = []
        excel_file = request.FILES["file"]
        wb = openpyxl.load_workbook(excel_file)

        worksheet = wb["Sheet1"]
        counter=0
        for row in worksheet.rows:
            if counter>0:
                if row[3].value is not None:
                    number_of_ticket = int(row[3].value / 10000)
                    for i in range(0, number_of_ticket):
                        #db.collection("tickets").add(ticket)

                        trans_objct={
                            "amountPaid":"10000",
                            "payerNames":row[1].value,
                            "payerPhoneNumber":str(row[2].value),
                            "paymentDate":datetime.today().strftime('%Y-%m-%d-%H:%M:%S'),
                            "reason":"001",
                            "transactionNumber":"1111"

                        }    
                        #datetime.datetime.now()

                        db.collection("institutions/2XqSaEp2OE8LppxAr2GD/transactions").add(trans_objct)

                        ticket_obj = {
                            "name": row[1].value,
                            "phone": str(row[2].value),
                            "amount": 10000,
                            "paymentNumber": "111",
                            "paymentTime": datetime.today().strftime('%Y-%m-%d-%H:%M:%S'),
                            "reason": "001",
                            "validatedAt": "",
                            'ticketNumber': str(get_ticket_number()),
                            'singlePurchaseAmount': 10000
                        }

                        tickets.append(ticket_obj)

            counter = counter+1
        SendSMSAndSaveData(tickets, tickets[0], "EXCEL").start()
        return Response(data=tickets)





# class AddTransactions(APIView):
#     def post(self,request):
#         try:
        
#             seriazed_data = TransactionDataSerializer(data=self.request.data)
#             if seriazed_data.is_valid():
#                 trans_obj = seriazed_data.data
#                 createInstitutionTransaction(trans_obj=trans_obj, inst_id=trans_obj['instId'])
#                 return Response(data={"transaction":trans_obj}, status=status.HTTP_200_OK)

#             else:
#                 return Response(data={"data":seriazed_data.errors}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             print(e)
#             return Response(data="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def createInstitutionTransaction(trans_obj,inst_id):
    """
    Method to save the transaction for specific institution. 
    to firebase.
    """
    try:
        transaction_object = {
            "name":trans_obj['name'],
            "amount":trans_obj['amount'],
            "paymentNumber":trans_obj['paymentNumber'],
            "paymentTime":trans_obj['paymentTime'],
            "phone":trans_obj['phone'],
            "reason":trans_obj['reason'],
         }
        db.collection("institutions").document(inst_id).collection("transactions").add(transaction_object)
    except Exception as e:
        print(e)
        return Response(data="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def createInstitutionEventTransaction(trans_obj,inst_id,event_id):
    """
    Method to save the transaction for specific institution. 
    to firebase.
    """
    try:
        transaction_object = {
            "name":trans_obj['name'],
            "amount":trans_obj['amount'],
            "paymentNumber":trans_obj['paymentNumber'],
            "paymentTime":trans_obj['paymentTime'],
            "phone":trans_obj['phone'],
            "reason":trans_obj['reason'],
         }
        transaction = db.collection(u'institutions').document(inst_id).collection("events").document(event_id).collection('transactions').where('paymentNumber','==',trans_obj['paymentNumber']).get()
        if len(transaction)>0:
            return False
        else:
            db.collection("institutions").document(inst_id).collection("events").document(event_id).collection('transactions').add(transaction_object)
            return True
    except Exception as e:
        print(e)
        return False
        #return Response(data="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def createInstitutionTickets(ticket,inst_id):
    """
    This is the method to save the ticket of a specific event of institution to
    firebase.
    """
    try:
        db.collection("institutions").document(inst_id).collection("tickets").add(ticket)
    except Exception as e:
        print(e)
        return Response(data="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def createInstitutionEventTickets(ticket,inst_id,event_id):
    """
    This is the method to save the ticket of a specific event of institution to
    firebase.
    """
    try:
        db.collection("institutions").document(inst_id).collection("events").document(event_id).collection('tickets').add(ticket)
    except Exception as e:
        print(e)
        return Response(data="Internal Server error", status=status.HTTP_500_INTERNAL_SERVER_ERROR)



#Service for event info for institution
class FetchEventData(GenericAPIView):
    serializer_class=EventDataSerializer
    authentication_classes=(FirebaseAuthentication,)
    def post(self,request):
        seriazed_data = EventDataSerializer(data=self.request.data)
        if seriazed_data.is_valid():
            data = seriazed_data.data
            eventId=data['eventId']
            institutionId=data['institutionId']
            ticketNumber=data['ticketNumber']
            institution_doc = db.collection(u'institutions').where('identifier','==',int(institutionId)).get()
            if len(institution_doc)>0:
                p_object=institution_doc[0].to_dict()
                #print(institution_doc[0].id)
                event_doc = db.collection(u'institutions').document(institution_doc[0].id).collection('events').where('eventID','==',eventId).get()
                if len(event_doc)>0:
                    e_object=event_doc[0].to_dict()
                    ticket_doc = db.collection(u'institutions').document(institution_doc[0].id).collection('events').document(event_doc[0].id).collection('tickets').where('ticketNumber','==',ticketNumber).get()
                    if len(ticket_doc)>0:
                        t_object=ticket_doc[0].to_dict()    
                        event={
                            "eventLocation":e_object['eventLocation'],
                            "date":e_object['date'],
                            "name":e_object['name'],
                            "time":e_object['time'],
                            "description":e_object['description'],
                            "ticketAmount":t_object['amount'],
                            "ticketReason":t_object['reason']

                        }
                        return Response(data={"data":event})
                    else:
                        return Response(data={"data":"no data found"}, status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response(data={"data":"no data found"}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(data={'data':'no data found'},status=status.HTTP_204_NO_CONTENT)

def EventStatisticData(request,institution_id,event_id):
    """
    This method is for getting ticket categories for a specific
    events.
    """
    try:
        responses = db.collection(u'institutions').document(institution_id).collection('events').document(event_id).collection('tickets').order_by(
        u'amount').get()
        event=db.collection(u'institutions').document(institution_id).collection('events').document(event_id).get()
        eventName=event.to_dict()['name']
        eventLocation=event.to_dict()['eventLocation']
        eventTime=event.to_dict()['time']
        eventDate=event.to_dict()['date']
        context = []
        ticket_scanned=0
        ticket_sold=0
        total_sales=0
        i=0
        for doc in responses:
            if  "valid" in  doc.to_dict().keys() and  "validated" in doc.to_dict().keys():
                if doc.to_dict()['valid']==True and doc.to_dict()['validated']==True:
                    ticket_scanned+=1
                if doc.to_dict()['valid']:
                    ticket_sold+=1
                    total_sales+=doc.to_dict()['amount']
            # combined = {
            #     'data':doc.to_dict()
            # }
            # context.append(combined)

            # Get ticket categories with their tickets generated
        
        all_ticket_categories=[]
        tickets_categories = db.collection(u'institutions').document(institution_id).collection('events').document(event_id).collection('ticket_category').order_by(
        u'category_id').get() 
            
        for t in tickets_categories:
            obj=t.to_dict()
                
            query = db.collection(u'institutions').document(institution_id).collection('events').document(event_id).collection('tickets').where('ticketCategoryId','==',obj['category_id'])
            tickets = query.get()
            
            valid_tickets=query.where('valid','==',True).get()
            in_valid_tickets=query.where('valid','==',False).get() 
            combinedData = {
                   'id':t.id,
                   'data':t.to_dict(),
                   'number_of_tickets':len(tickets),
                   'valid_tickets':len(valid_tickets),
                   'in_valid_tickets':len(in_valid_tickets)
               }

            all_ticket_categories.append(combinedData)

            # For No Category Specified
            no_category_query = db.collection(u'institutions').document(institution_id).collection('events').document(event_id).collection('tickets').where('ticketCategoryId','==','0')
            no_category_tickets=no_category_query.get()   
            no_category_valid_tickets=no_category_query.where('valid','==',True).get()
            no_category_in_valid_tickets=no_category_query.where('valid','==',False).get()         
        return render(request, 'event_statistic_data.html', {'ticket_scanned':ticket_scanned,'ticket_sold':ticket_sold,'total_sales':total_sales,'event':eventName,'eventLocation':eventLocation,'eventTime':eventTime,'eventDate':eventDate,'tickets_categories':all_ticket_categories,'no_category_tickets':len(no_category_tickets),'no_category_valid_tickets':len(no_category_valid_tickets),'no_category_in_valid_tickets':len(no_category_in_valid_tickets)})
    except Exception as e:
        print(e)


# Send ticket in email
def send_ticket_in_email(email, ticketNumber, inst_identifier,event_id,event_name):
    content = f'You have received a ticket for '+event_name+' click here to access your ticket '+env("NOKANDA_TICKET_APP_URL")+''+str(inst_identifier)+'/'+event_id+'/'+ticketNumber+''
    print("We are going to send email")
    # Prepare phone to send message to
    print("This is the email to send to")
    print(email)
    if len(email)>1:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if(re.fullmatch(regex, email)):
            
            EMAIL_ADDRESS=os.environ.get('EMAIL_HOST_USER')
            EMAIL_PASSWORD=os.environ.get('EMAIL_HOST_PASSWORD')
            RECEIVE_EMAIL=email

            msg=EmailMessage()
            msg['subject']='Nokanda'
            msg['From']=EMAIL_ADDRESS
            msg['To']=RECEIVE_EMAIL
            msg.set_content(content)

            #EmailThread(user, form).start()

            with smtplib.SMTP_SSL(os.environ.get('EMAIL_HOST'),465) as smtp:
                smtp.login(EMAIL_ADDRESS,EMAIL_PASSWORD)
                smtp.send_message(msg)

        else:
            print('Invalid Email')
    
    response = 'Done'
    return response


# Check if it's email
def is_email(content):
    check=False
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.fullmatch(regex, content)):
        check=True
    return check

#Endpoint to generate tickets from payment api
class AddTicketV2(generics.GenericAPIView):
    serializer_class=BuyTicketsSerializer
    authentication_classes=(FirebaseAuthentication,)
    def post(self,request):
        seriazed_data = BuyTicketsSerializer(data=self.request.data)
        if seriazed_data.is_valid():
            trans_obj = seriazed_data.data
            obj = seriazed_data.data
            # Find key data from referenceNumber
            referencenNumber=obj['referenceNumber']
            if referencenNumber.__contains__("_"):
                    parts=referencenNumber.split('_')
                    if len(parts)==3:
                        instId=parts[0]
                        eventId=parts[1]
                        ticketCategoryId=parts[2]
                        trans_obj={
                            'phone':obj['senderPhone'],
                            'name':obj['sender'],
                            'paymentNumber':obj['transactionNumber'],
                            'paymentTime':obj['transactionTime'],
                            'amount':int(obj['amount']),
                            'reason':'Buying Ticket',
                            'validated':False,
                            'instId':instId,
                            'eventId':eventId,
                            'ticketCategoryId':ticketCategoryId,
                            'quantity':0
                        }
                        
                        tickets = create_tickets_v2(trans_obj)
                        # Send data to firebase
                        SendSMSAndSaveData_V2(tickets, trans_obj, "INDIVIDUAL").start()
                        # # Send sms to ticket buyer
                        # SendTicketSMSs(tickets, transObj).start()

                        return Response(data={"transaction":tickets},status=status.HTTP_201_CREATED)
                    else:
                        return Response(data={"data":seriazed_data.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"data":seriazed_data.errors}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response(data={"data":seriazed_data.errors}, status=status.HTTP_400_BAD_REQUEST)



#Endpoint to generate tickets from payment api
class AddTicketV3(generics.GenericAPIView):
    serializer_class=BuyTicketsSerializer
    authentication_classes=(FirebaseAuthentication,)
    def post(self,request,institution_id,event_id):
        seriazed_data = BuyTicketsSerializer(data=self.request.data)
        if seriazed_data.is_valid():
                        trans_obj = seriazed_data.data
                        obj = seriazed_data.data
                        # Find key data from referenceNumber
                        referencenNumber=obj['referenceNumber']
                        #ticketCategoryId=referencenNumber
                        trans_obj={
                            'phone':obj['senderPhone'],
                            'name':obj['sender'],
                            'paymentNumber':obj['transactionNumber'],
                            'paymentTime':obj['transactionTime'],
                            'amount':int(obj['amount']),
                            'reason':'Buying Ticket',
                            'validated':False,
                            'instId':institution_id,
                            'eventId':event_id,
                            'ticketCategoryId':referencenNumber,
                            'quantity':0
                        }
                        
                        tickets = create_tickets_v2(trans_obj)
                        # Send data to firebase
                        SendSMSAndSaveData_V2(tickets, trans_obj, "INDIVIDUAL").start()
                        # # Send sms to ticket buyer
                        # SendTicketSMSs(tickets, transObj).start()

                        return Response(data={"transaction":tickets},status=status.HTTP_201_CREATED)
                            
            
        else:
            return Response(data={"data":seriazed_data.errors}, status=status.HTTP_400_BAD_REQUEST)

class GenerateTicketsBetweenDates(generics.GenericAPIView):
    # this method is for generating tickets between dates.
    serializer_class = SearchTicketBetweenDatesSerializer
    authentication_classes = (FirebaseAuthentication,)
    def post(self, *args, **kwargs):
        instId = self.request.data['instId']
        eventId = self.request.data['eventId']
        start_date =date(1995, 1, 1)
        end_date =date.today()
        collection = db.collection("institutions").document(instId).collection("events").document(eventId).collection('tickets').get()
        tickets = []

        if len(collection) > 0: 
            for doc in collection:
                ticket = doc.to_dict()
                paymentTime = ticket['paymentTime']
                paymentDate = datetime.strptime(paymentTime, '%d.%m.%Y').date() 
                if start_date <= paymentDate <= end_date:
                    if ticket['valid']==True:
                        data = {
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
                        tickets.append(data)

            return Response(data=tickets, status=status.HTTP_200_OK)
        else:
            return Response(data='tickets are not found', status=status.HTTP_400_BAD_REQUEST)
    
class GenerateTicketsFromStartDateToendDate(generics.GenericAPIView):
    serializer_class = SearchTicketByDateSerializer
    authentication_classes = (FirebaseAuthentication,)
    # This method is for getting   all valid tickets during period of time.
    def post(self, *args, **kwargs):
        instId = self.request.data['instId']
        eventId = self.request.data['eventId']
        start_date = self.request.data['start_date']
        end_date = self.request.data['end_date']
        start_date1 = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date1 = datetime.strptime(end_date, '%Y-%m-%d').date()
        collection = db.collection("institutions").document(instId).collection("events").document(eventId).collection('tickets').get()
        tickets = []

        if len(collection) > 0:  
            for doc in collection:
                ticket = doc.to_dict()
                paymentTime = ticket['paymentTime']
                paymentDate = datetime.strptime(paymentTime, '%d.%m.%Y').date() 
                if start_date1 <= paymentDate <= end_date1:
                    if ticket['valid']==True:
                        data = {
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
                        tickets.append(data)

            return Response(data=tickets, status=status.HTTP_200_OK)
        else:
            return Response(data='tickets are not found', status=status.HTTP_400_BAD_REQUEST)