from rest_framework import serializers
from datetime import date

class TicketsDataSerializer(serializers.Serializer):
    phone=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    name=serializers.CharField(required=True)
    paymentNumber=serializers.CharField(required=True)
    paymentTime=serializers.CharField(required=True)
    amount = serializers.FloatField()
    reason=serializers.CharField(required=False,allow_null=True,allow_blank=True)
    #singlePurchaseAmount=serializers.FloatField(required=False)
    validated=serializers.BooleanField(default=False,allow_null=True)
    instId=serializers.CharField(required=True)
    #eventId=serializers.CharField(required=True)
    deviceId=serializers.CharField(required=True)
    ticketCategoryId=serializers.CharField(required=True)
    quantity=serializers.DecimalField(
        decimal_places=2, max_digits=15, default=1, allow_null=True)
class TicketDataSerializer(serializers.Serializer):
    phone=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    name=serializers.CharField(required=True)
    paymentNumber=serializers.CharField(required=True)
    paymentTime=serializers.CharField(required=True)
    amount = serializers.FloatField()
    reason=serializers.CharField(required=False,allow_null=True,allow_blank=True)
    #singlePurchaseAmount=serializers.FloatField(required=False)
    validated=serializers.BooleanField(default=False,allow_null=True)
    instId=serializers.CharField(required=True)
    eventId=serializers.CharField(required=True)
    #deviceId=serializers.CharField(required=True)
    ticketCategoryId=serializers.CharField(required=True)
    quantity=serializers.DecimalField(
        decimal_places=2, max_digits=15, default=1, allow_null=True)

class TransactionSerializer(serializers.Serializer):
     transactionNumber=serializers.CharField(required=True)
     sender=serializers.CharField(required=True)
     senderPhone=serializers.CharField(required=True)
     transactionTime=serializers.CharField(required=True)
     amount=serializers.FloatField(required=True)
     referenceNumber=serializers.CharField(required=True)
     reason=serializers.CharField(required=False,allow_null=True,allow_blank=True)
     validated=serializers.BooleanField(default=False,allow_null=True)
     quantity=serializers.DecimalField(
        decimal_places=2, max_digits=15, default=1, allow_null=True)

class BuyTicketsSerializer(serializers.Serializer):
     transactionNumber=serializers.CharField(required=True)
     sender=serializers.CharField(required=True)
     senderPhone=serializers.CharField(required=True)
     transactionTime=serializers.CharField(required=True)
     amount=serializers.CharField(required=True)
     referenceNumber=serializers.CharField(required=True)

class SaveCardTransactionSerializer(serializers.Serializer):
     paymentNumber=serializers.CharField(required=True)
     name=serializers.CharField(required=True)
     senderEmail=serializers.CharField(required=True)
     ticketCategory=serializers.CharField(required=True)
     ticketQuantity=serializers.CharField(required=True)
     paymentTime=serializers.CharField(required=True)

#     phone=serializers.CharField(required=True,allow_null=False,allow_blank=False)
#     name=serializers.CharField(required=True)
#     paymentNumber=serializers.CharField(required=True)
#     paymentTime=serializers.CharField(required=True)
#     amount = serializers.FloatField()
#     reason=serializers.CharField(required=False,allow_null=True,allow_blank=True)
#     instId=serializers.CharField(required=True)


class EventDataSerializer(serializers.Serializer):
    institutionId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    eventId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    ticketNumber=serializers.CharField(required=True,allow_null=False,allow_blank=False)
class ValidateTicketSerializer(serializers.Serializer):
    ticketNumber=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    instId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    eventId=serializers.CharField(required=True,allow_null=False,allow_blank=False)

class SearchTicketByPhoneSerializer(serializers.Serializer):
    phone=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    instId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    eventId=serializers.CharField(required=True,allow_null=False,allow_blank=False)

class SearchTicketByTransactionNumberSerializer(serializers.Serializer):
    paymentNumber=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    instId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    eventId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
class SearchTicketBetweenDatesSerializer(serializers.Serializer):
    instId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    eventId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    start_date=serializers.DateField(default=date(1995,1,1))
    end_date=serializers.DateField(default=date.today())

class SearchTicketByDateSerializer(serializers.Serializer):
    instId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    eventId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
    start_date=serializers.DateField()
    end_date=serializers.DateField()
   

   

class EventSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    eventLocation = serializers.CharField(required=True)
    date = serializers.CharField(required=True)
    eventID = serializers.CharField(required=True)
    eventDevice = serializers.CharField(required=True)
    singlePurchaseAmount = serializers.CharField(required=True)  
    description = serializers.CharField(required=True, allow_null=True)
    call_back_url = serializers.CharField(required=True)
    current_group_number = serializers.IntegerField(required=True)
    time = serializers.CharField(required=True)
    group_number_assignation_required = serializers.BooleanField(default=False)
    active = serializers.BooleanField(default=True)
    how_many_per_group = serializers.IntegerField(required=True)
    unfinished_group = serializers.IntegerField(required=True)
    unfinished_group_remaining_members = serializers.IntegerField(required=True)
    momoCode = serializers.CharField(required=True)
class InstitutionSerializer(serializers.Serializer):
    call_back_url=serializers.CharField(required=True)
    identifier=serializers.IntegerField(required=True)
    name=serializers.CharField(required=True)
    url_method=serializers.CharField(required=True)
    phone=serializers.CharField(required=True)
    url_query_parameter=serializers.ListField()
    users=serializers.CharField(required=True)
    active=serializers.BooleanField(default=True)
class TicketCategorySerializer(serializers.Serializer):
     category_id=serializers.CharField(required=True)
     name=serializers.CharField(required=True)
     amount=serializers.CharField(required=True)
     group_quantity=serializers.CharField(required=True)
     quantity=serializers.IntegerField(required=True)
     is_free=serializers.BooleanField(default=False)
     is_group=serializers.BooleanField(default=False)

class UserSerializer(serializers.Serializer):
     email=serializers.CharField()
     password=serializers.CharField()
class PasswordUserSerializer(serializers.Serializer):
     new_password=serializers.CharField()
class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    instId = serializers.CharField()
    eventId = serializers.CharField()
    categ_id = serializers.CharField()

class sendSMSTicketSerializer(serializers.Serializer):
        ticketNumber=serializers.CharField(required=True,allow_null=False,allow_blank=False)
        instId=serializers.CharField(required=True,allow_null=False,allow_blank=False)
        eventId=serializers.CharField   (required=True,allow_null=False,allow_blank=False)



