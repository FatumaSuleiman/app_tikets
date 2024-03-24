from django.urls import path
from transactionsaver.views.transaction_views import AddTicket, GenerateTicket1, GenerateTicketsFromExcel,Testing,FetchEventData,EventStatisticData,FindDuplicate,AddTicketV2
from transactionsaver.views.validate_tickect_views import ValidateTicket,SearchTicketByPhone
from transactionsaver.views.ticketing_views import institution_events,ticket_category,institution_event_stats,SaveCardTransaction,success,institution_event_free_tickets,GetTicketCategories,MergeTickets,GetTicketsFromCategory
from transactionsaver.views.institution_views import SaveInstitution,UpdateInstitution,GetAllInstitutions,GetInstitutionDetails
from transactionsaver.views.event_views import SaveEvent,GetAllInstitutionevents,GetEventDetails,AddTicketV3
from transactionsaver.views.ticket_category_views import (AddTicketCategory,GetAlleventTicketCategory,GetCategoryDetails,UpdateTicketCategory,SaveTickets,ValidTicketsForEvent,InvalidTicketsForEvent)
from transactionsaver.views.users_views import CreateUser
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
    path('nokandaService/institution/save',SaveInstitution.as_view(), name="saveInstitution" ),
    path('nokandaService/institutions/update/<str:institution_id>', UpdateInstitution.as_view(), name="updateinstitution" ),
    path('nokandaService/institutions/all', GetAllInstitutions.as_view(), name="allInstitutions" ),
    path('nokandaService/institutions/details/<str:inst_id>', GetInstitutionDetails.as_view(), name="institutionDetails" ),
    path('nokandaService/events/create/<str:institution_id>', SaveEvent.as_view(), name="saveEvent" ),
    path('nokandaService/events/all/<str:inst_id>',GetAllInstitutionevents.as_view(), name="AllEvent" ),
    path('nokandaService/event/details/<str:inst_id>/<str:event_id>', GetEventDetails.as_view(), name="EventDetails" ),
    path('nokandaService/ticket_category/save/<str:institution_id>/<str:event_id>', AddTicketCategory.as_view(), name="AddTicketCategory" ),
    path('nokandaService/events/categories/all/<str:inst_id>/<str:event_id>',GetAlleventTicketCategory.as_view(), name="AllEventCategories" ),
    path('nokandaService/event/category/details/<str:inst_id>/<str:event_id>/<str:categ_id>', GetCategoryDetails.as_view(), name="CategoryDetails" ),
    path('nokandaService/ticket_category/update/<str:institution_id>/<str:event_id>/<str:categ_id>', UpdateTicketCategory.as_view(), name="UpdateTicketCategory" ),
    path('nokandaService/Save/generate/tickets/', SaveTickets.as_view(), name="SaveTickets" ),
    path('nokandaService/valid/tickets/all/<str:inst_id>/<str:eventId>', ValidTicketsForEvent.as_view(), name="Valid_ticket" ),
    path('nokandaService/invalid/tickets/all/<str:inst_id>/<str:eventId>', InvalidTicketsForEvent.as_view(), name="Invalid_ticket" ),
    path('nokandaService/users/creates', CreateUser.as_view(), name="SaveUser" ),
    path('nokandaService/ticket/generate/v2', AddTicketV2.as_view(), name="create_ticket_v2" ),
    path('nokandaService/ticket/generate/v3/<str:institutionId>/<str:eventId>', AddTicketV3.as_view(), name="save_ticket_v3" ),
    
    
    
]