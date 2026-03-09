from django.urls import path
from marketplace import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.home, name='home'),
    path('seller/<slug:seller_username_slug>/<slug:product_name_slug>/', views.product_page, name = 'product_page'),
]