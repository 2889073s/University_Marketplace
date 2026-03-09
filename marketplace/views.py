from django.shortcuts import render
from django.http import HttpResponse
from marketplace.models import Product, UserProfile 
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    context_dict = {}
    #Just going to display 20 random products on homepage
    #Josh -change below code if you want more products on the homepage
    random_product_list = Product.objects.order_by('?')[:20]
    context_dict["products"] = random_product_list
    return render(request, 'marketplace/home.html', context = context_dict)

def product_page(request,  seller_username_slug, product_name_slug):
    context_dict = {}
    try:
        #if we cant find the .get() method for this product id then rasies a DoesNotExist exeption
        product = Product.objects.get(seller__slug = seller_username_slug ,slug = product_name_slug)
        context_dict["product"] = product
    except Product.DoesNotExist:
        context_dict['product'] = None
    return render(request, 'marketplace/product.html', context= context_dict)


def seller_page(request, seller_username_slug):
    context_dict = {}
    try:
        #if we cant find the .get() method for this product id then rasies a DoesNotExist exeption
        seller = UserProfile.objects.get(slug = seller_username_slug )
        context_dict["seller"] = seller
        sellers_products = Product.objects.filter(seller = seller, is_sold = False)
        context_dict["products"] = sellers_products
    except UserProfile.DoesNotExist:
        context_dict['seller'] = None
        context_dict["products"] = None
    return render(request, 'marketplace/seller.html', context= context_dict)

@login_required
def profile_page(request):
    profile = UserProfile.objects.get(user = request.user )
    #gets the products that the seller is actively selling and ones that have been sold and products that they have bought
    active_products = Product.objects.filter( seller = profile, is_sold = False)
    sold_products = Product.objects.filter( seller = profile, is_sold = True)
    bought_products = Product.objects.filter( buyer = profile)

    context_dict = {
        "profile" : profile,
        "active_products" : active_products,
        "sold_products" : sold_products,
        "bought_products" : bought_products
    }
    return render(request, 'marketplace/profile.html', context= context_dict)




