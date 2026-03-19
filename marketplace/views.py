from django.shortcuts import render, redirect
from marketplace.models import Product, UserProfile, Tag
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import ProductForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone

# Create your views here.
def home(request):
    context_dict = {}
    #Just going to display 20 random products on homepage
    #Josh -change below code if you want more products on the homepage
    if request.user.is_authenticated: #if user is logged in, doesnt show their own products on the homepage
        try:
            random_product_list = Product.objects.exclude(seller = request.user.userprofile).exclude( is_sold = True).order_by('?')[:20]
        except UserProfile.DoesNotExist:
            random_product_list = Product.objects.exclude( is_sold = True).order_by('?')[:20]
    else:
        random_product_list = Product.objects.exclude( is_sold = True).order_by('?')[:20]
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

def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['profile_picture']

            profile.save()

            registered = True
            return redirect('marketplace:home') 
        else:
            print(user_form.errors, profile_form.errors)
    else:
            user_form = UserForm()
            profile_form = UserProfileForm()

    return render(request,
        'marketplace/register.html',
        context = {'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('marketplace:home'))
            else:
                return HttpResponse("Your account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'marketplace/login.html')
    
@login_required
def user_logout(request):
    logout(request)
    return redirect('marketplace:home')

def search_page(request):
    query = request.GET.get('q', '').strip()
    tag_id = request.GET.get('tag', '').strip()
    sort = request.GET.get('sort', '').strip()

    products = Product.objects.filter(is_sold=False)

    if query:
        products = products.filter(name__icontains=query)

    if tag_id:
        products = products.filter(tag_id=tag_id)

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-list_date')

    tags = Tag.objects.all()

    context_dict = {
        'products': products,
        'tags': tags,
        'query': query,
        'selected_tag': tag_id,
        'selected_sort': sort,
    }

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            'marketplace/partials/search_results.html',
            {'products': products},
            request=request
        )
        return HttpResponse(html)

    return render(request, 'marketplace/search.html', context=context_dict)

@login_required
def sell_page(request):
    context_dict = {}
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = UserProfile.objects.get(user=request.user)
            form.save()
            
            return redirect('marketplace:product_page', product_name_slug=product.slug,seller_username_slug=product.seller.slug)
    else:
        form = ProductForm()
    
    context_dict['form'] = form
    context_dict['seller'] = UserProfile.objects.get(user=request.user)
    
    return render(request, 'marketplace/sell.html', context=context_dict)


def review_page(request, seller_username_slug, product_name_slug):
    context_dict = {}
    return render(request, 'marketplace/review.html', context=context_dict)

@login_required
def edit_product_page(request, product_name_slug):
    profile = UserProfile.objects.get(user=request.user)
    context_dict = {}
    try:
        product = Product.objects.get(seller=profile, slug=product_name_slug)
        context_dict["product"] = product
    except Product.DoesNotExist:
        product = None
    
    if product:
        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES, instance=product)
            if form.is_valid():
                form.save()
                return redirect('marketplace:product_page', product_name_slug=product.slug,seller_username_slug=product.seller.slug)
        else:
            form = ProductForm(instance=product) 

        context_dict['form'] = form
    context_dict['product'] = product


    return render(request, 'marketplace/edit_product.html', context=context_dict)

@login_required
def delete_product_page(request, product_name_slug):
    profile = UserProfile.objects.get(user=request.user)
    context_dict = {}
    try:
        product = Product.objects.get(seller=profile, slug=product_name_slug)
        context_dict["product"] = product
    except Product.DoesNotExist:
        context_dict["product"] = None
    
    if product:
        if request.method == 'POST':
            product.delete()
            return redirect('marketplace:home')
    return render(request, 'marketplace/delete_product.html', context=context_dict)

def buy_product(request, seller_username_slug, product_name_slug):
    if request.method == "POST":
        if request.user.is_authenticated:
            product = Product.objects.get(slug = product_name_slug, seller__slug = seller_username_slug)
            buyer = UserProfile.objects.get(user=request.user )
            seller = product.seller
            if buyer == seller:
                messages.success(request, ("You can't buy your own product"))
                return redirect('marketplace:product_page',product.seller.slug, product.slug)
            elif buyer.account_balance < product.price:
                messages.success(request, ("Insufficient funds"))
                return redirect('marketplace:product_page',product.seller.slug, product.slug)
                
            elif product.is_sold:
                messages.success(request, ("Product is not avaliable anymore"))
                return redirect('marketplace:product_page',product.seller.slug, product.slug)
            else:
                #proccess payment
                buyer.account_balance -= product.price
                seller.account_balance += product.price
                buyer.save()
                seller.save()

                product.is_sold = True
                product.buyer = buyer
                product.purchase_date = timezone.now()
                product.save()

                messages.success(request, ("Successful transaction"))

                return redirect('marketplace:review_page', seller_username_slug=product.seller.slug, product_name_slug=product.slug)

        else: #if user isnt logged in, take them to login page
            messages.success(request, ("You have to be logged in"))
            return redirect('marketplace:login')
    else:
        return redirect('marketplace:home')





