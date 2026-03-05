from django.urls import path
from marketplace import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.home, name='home'),
]