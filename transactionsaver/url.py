from django.urls import path
from transactionsaver.views.transaction_views import (AddTicket, AddTicketV2, AddTicketV3, GenerateTicket1, GenerateTicketsFromExcel,Testing,FetchEventData,
                                                      EventStatisticData,FindDuplicate,GenerateTicketsBetweenDates,GenerateTicketsFromStartDateToendDate)
from transactionsaver.views.validate_tickect_views import ValidateTicket,SearchTicketByPhone,SearchTicketByPaymentNumber,GetValidatedTicketByPaymentNumber
from transactionsaver.views.ticketing_views import( institution_events,ticket_category,institution_event_stats,SaveCardTransaction,success,institution_event_free_tickets,GetTicketCategories,
                                                   MergeTickets,GetTicketsFromCategory,get_all_event_tickets,validate_ticket,GetAllEventTickets)
from transactionsaver.views.institution_views import SaveInstitution,UpdateInstitution,GetAllInstitutions,GetInstitutionDetails,home,get_institutions,login,institution_details,update_institution
from transactionsaver.views.event_views import SaveEvent,GetAllInstitutionevents,GetEventDetails,institution_events,get_institution_event_detail,UpdateInstitutionEvent,update_institution_events,SendSMSTicket
from transactionsaver.views.ticket_category_views import (AddTicketCategory,GetAlleventTicketCategory,GetCategoryDetails,UpdateTicketCategory,SaveTickets,ValidTicketsForEvent,InvalidTicketsForEvent,GenerateTicketsFromExcel1,
                                                          get_all_event_ticketCategories,get_event_ticket_category_detail,update_event_ticket_categorise)
from transactionsaver.views.users_views import CreateUser,GenerateToken
urlpatterns = [
    path('nokandaService/ticket/generate', AddTicket.as_view(), name="create_ticket" ),
    path('nokandaService/ticket/validate', ValidateTicket.as_view(), name="ticket_validate" ),
    path('nokandaService/institutions/ticket/generate', GenerateTicket1.as_view(),name="generate_institution_ticket"),
    path('nokandaService/excel/ticket/generate', GenerateTicketsFromExcel.as_view(),name="generate_excel_ticket"),
    path('nokandaService/institutions/<str:institution_id>/events/<str:phone_number>', institution_events ,name="institutionEvent"),
    path('nokandaService/institutions/<str:institution_id>/events/<str:event_id>/ticketCategory/<str:phone_number>', ticket_category,name="ticketCategory"),
    path('nokandaService/ticket/testing', Testing.as_view(), name="testing" ),
    path('nokandaService/ticket/fetcheventdata', FetchEventData.as_view(), name="fetcheventdata" ),
    path('nokandaService/institutions/<str:institution_id>/eventstats', institution_event_stats,name="institutionEventStats"),
    path('nokandaService/institutions/<str:institution_id>/eventstats/<str:event_id>', EventStatisticData, name="event_statistics" ),
    path('nokandaService/institutions/<str:institution_id>/events/<str:event_id>/saveCardtrans', SaveCardTransaction.as_view(), name="saveCardTransaction" ),
    path('nokandaService/success', success, name="success"),
    path('nokandaService/institutions/<str:institution_id>/eventfreeticket', institution_event_free_tickets,name="institution_event_free_tickets"),
    path('nokandaService/ticket/searchTicketByPhone', SearchTicketByPhone.as_view(), name="searchTicketByPhone" ),
    path('nokandaService/ticket/findduplicate', FindDuplicate.as_view(), name="findduplicate" ),
    path('api/tickets/categories', GetTicketCategories.as_view(), name="ticketCategories" ),
    path('api/tickets/merge', MergeTickets.as_view(), name="mergeTickets" ),
    path('api/institutions/<str:instId>/events/<str:eventId>/tickets/<str:categoryId>/fromCategory', GetTicketsFromCategory.as_view(), name="categoryTickets" ),
    path('institutions/createInstitutions',SaveInstitution.as_view() , name='saveInstitution'),  
    path('institutions/updateInstitutions/<str:institution_id>', UpdateInstitution.as_view(), name="updateinstitution" ),
    path('institutions/getAllInstitutions', GetAllInstitutions.as_view(), name="allInstitutions" ),
    path('institutions/getInstitutionDetails/<str:inst_id>', GetInstitutionDetails.as_view(), name="institutionDetails" ),
    path('events/createEvents/<str:institution_id>', SaveEvent.as_view(), name="saveEvent" ), 
    path('events/updateEvents/<str:inst_id>/<str:event_id>', UpdateInstitutionEvent.as_view(), name="updateEvent" ),
    path('events/getAll_institutionEvents/<str:inst_id>',GetAllInstitutionevents.as_view(), name="AllEvent" ),
    path('events/getEventDetails/<str:inst_id>/<str:event_id>', GetEventDetails.as_view(), name="EventDetails" ),
    path('categories/saveTicketCategory/<str:institution_id>/<str:event_id>', AddTicketCategory.as_view(), name="AddTicketCategory" ), 
    path('categories/getAll_EventCategories/<str:inst_id>/<str:event_id>',GetAlleventTicketCategory.as_view(), name="AllEventCategories" ),
    path('categories/getEventCategoryDetails/<str:inst_id>/<str:event_id>/<str:categ_id>', GetCategoryDetails.as_view(), name="CategoryDetails" ),
    path('categories/updateTicketCategory/<str:institution_id>/<str:event_id>/<str:categ_id>', UpdateTicketCategory.as_view(), name="UpdateTicketCategory" ),
    path('tickets/generate/createTickets/', SaveTickets.as_view(), name="SaveTickets" ),
    path('tickets/getAll_ValidTickets/<str:inst_id>/<str:eventId>', ValidTicketsForEvent.as_view(), name="Valid_ticket" ),
    path('tickets/getAll_InvalidTickets/<str:inst_id>/<str:eventId>', InvalidTicketsForEvent.as_view(), name="Invalid_ticket" ),
    path('tickets/ticket/generate_v2', AddTicketV2.as_view(), name="create_ticket_v2" ),
    path('tickets/ticket/generate_v3/<str:institution_id>/<str:event_id>', AddTicketV3.as_view(), name="create_ticket_v3" ),
    path('tickets/generateTicketsFromExcelFile', GenerateTicketsFromExcel1.as_view(), name="generate_tickets" ),
    path('tickets/searchTicketByPaymentNumber', SearchTicketByPaymentNumber.as_view(), name="searchTicketByPaymentNumber" ),
    path('tickets/searchValidatedTicketsByPaymentNumber', GetValidatedTicketByPaymentNumber.as_view(), name="validatedTicketByPaymentNumber" ),
    path('tickets/generate/tickets_betweenDates', GenerateTicketsBetweenDates.as_view(), name="validTicketsBetweenDates" ),
    path('tickets/generate/tickets_from_startDate_to_endDate', GenerateTicketsFromStartDateToendDate.as_view(), name="validTicketsFromDates_toEndDates" ),
    path('institutions/home' ,home,name='home'),
    path('institutions/get_institutions',get_institutions,name='List of institutions'),
    path('' ,login ,name='login'),
    path('institutions/institutionDetails/<str:instId>' ,institution_details,name='institutionDetails'),
    path('institutions/update_institutions/<str:instId>',update_institution,name='updateInstitution'),
    path('institutions/<str:institution_id>/events/', institution_events, name='institution_events'),
    path('institutions/<str:inst_id>/events/<str:event_id>', get_institution_event_detail, name='institution_event_details'),
    path('institutions/<str:inst_id>/events/<str:event_id>/updateEvent', update_institution_events, name='update_institution_event'),
    path('categories/<str:institution_id>/events/<str:event_id>/ticketCategory', get_all_event_ticketCategories, name='ticketCategories'),
    path('institutions/<str:inst_id>/events/<str:event_id>/ticketCategory/<str:categ_id>', get_event_ticket_category_detail, name='ticketCategory_details'),
    path('institutions/<str:institution_id>/categories/<str:event_id>/<str:categ_id>/updateTicket_category' ,update_event_ticket_categorise,name='updateEventTicketCategory'),
    path('institutions/<str:institution_id>/events/<str:event_id>/ticket/' ,get_all_event_tickets,name='event_tickets'),
    path('tickets/sms/ticket' ,SendSMSTicket.as_view(),name='ticket_sms'),
    path('tickets/<str:inst_id>/events/<str:event_id>/tickets' ,GetAllEventTickets.as_view(),name='EventTickets'),





]