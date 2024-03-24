from django.contrib import admin
from django.urls import path
from transactionsaver.views import users_views

urlpatterns = [
   path('token', users_views.GenerateToken.as_view(), name='token'),  
]
