

from django.urls import path
from . import views
urlpatterns = [
    
    path('sendsms', views.sendsms.as_view(), name='sendsms'),
    
]
