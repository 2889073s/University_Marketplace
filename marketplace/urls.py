from django.urls import path
from marketplace import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.home, name='home'),
    path('seller/<slug:seller_username_slug>/<slug:product_name_slug>/', views.product_page, name = 'product_page'),
    path('seller/<slug:seller_username_slug>/', views.seller_page, name = 'seller_page' ),
    path('profile/', views.profile_page, name= 'profile_page'),
    path('register/', views.register,  name = 'register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('sell', views.sell_page, name = 'sell_page'),
    path('search/', views.search_page, name = 'search_page'),
    path('review/<slug:seller_username_slug>/', views.review_page, name = 'review_page'),
    path('profile/edit-product/<slug:product_name_slug>/', views.edit_product_page, name="edit_product_page"),
    path('profile/delete-product/<slug:product_name_slug>/', views.delete_product_page, name="delete_product_page"),


]
