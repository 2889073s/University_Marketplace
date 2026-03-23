from django.test import TestCase
from django.urls import reverse
from marketplace.models import Product, Review, Tag, UserProfile
from django.contrib.auth.models import User

#these functions add data to the models to be used in testing
def add_user_profiles(username, email, password, account_balance= 100.00):
    user = User.objects.create_user(username=username, email=email, password=password)
    profile = UserProfile.objects.create(user=user, account_balance=account_balance)
    return user, profile

def add_tag(name):
    return Tag.objects.create(tag_name = name)

def add_product(name, seller, tag, price= 10.00, description="Testing",is_sold=False):
    return Product.objects.create(name=name, seller=seller, price=price,tag=tag, description= description, is_sold=is_sold)


class BasicTest(TestCase):
    def setUp(self):
        self.seller_user, self.seller_profile = add_user_profiles("seller1", "seller1@test.com", "test123456",)
        self.buyer_user, self.buyer_profile = add_user_profiles("buyer1", "buyer1@test.com", "test123456", account_balance=20.00 )
        self.tag = add_tag("Tech")
        self.product = add_product("Python book", self.seller_profile, self.tag)

    #testing pages are responding
    def test_home_page_loads(self):
        response = self.client.get(reverse('marketplace:home'))
        self.assertEqual(response.status_code, 200)

    def test_search_page(self):
        response = self.client.get(reverse('marketplace:search_page'))
        self.assertEqual(response.status_code, 200)

    def test_login_page(self):
        response = self.client.get(reverse('marketplace:login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get(reverse('marketplace:register'))
        self.assertEqual(response.status_code, 200)

    def test_seller_page(self):
        #tests that there is a seller page for seller1
        response = self.client.get(reverse('marketplace:seller_page', args=[self.seller_profile.slug]))
        self.assertEqual(response.status_code, 200)

    def test_product_page(self):
        response = self.client.get(reverse('marketplace:product_page', args=[self.seller_profile.slug, self.product.slug]))
        self.assertEqual(response.status_code, 200)

    # in these tests the pages should get redirected (code 302)
    def test_sell_page_requires_login(self):
        response = self.client.get(reverse('marketplace:sell_page'))
        self.assertEqual(response.status_code, 302)

    #this test has been failing
    def test_buy_page_requires_login(self):
        response = self.client.get(reverse('marketplace:buy_product', args=[self.seller_profile.slug, self.product.slug]))
        self.assertEqual(response.status_code, 302)

    def test_sell_page_requires_login(self):
        response = self.client.get(reverse('marketplace:sell_page'))
        self.assertEqual(response.status_code, 302)

    #test that you dont get redirected when logged in
    def test_profile_page_when_logged_in(self):
        self.client.login(username="buyer1", password = "test123456")
        response = self.client.get(reverse('marketplace:profile_page'))
        self.assertEqual(response.status_code, 200)


    def test_sell_page_when_logged_in(self):
        self.client.login(username="buyer1", password = "test123456")
        response = self.client.get(reverse('marketplace:sell_page'))
        self.assertEqual(response.status_code, 200)
  
    #buy product tests
    def test_seller_cannot_buy_own_products(self):
        inital__seller_balance = self.seller_profile.account_balance
        inital_buyer_balance = self.buyer_profile.account_balance
        self.client.login(username="seller1", password = "test123456")
        response = self.client.post(reverse('marketplace:buy_product', args=[self.seller_profile.slug, self.product.slug]))

        self.assertEqual(response.status_code, 302)

        self.product.save()
        self.seller_profile.save()
        
        self.assertFalse(self.product.is_sold)
        self.assertEqual(self.seller_profile.account_balance, inital__seller_balance)
        self.assertEqual(self.buyer_profile.account_balance, inital_buyer_balance)

    def test_buyer_with_insufficient_funds_cannot_buy(self):
        inital__seller_balance = self.seller_profile.account_balance
        self.buyer_profile.account_balance = 5.00
        self.buyer_profile.save()

        self.client.login(username="buyer1", password = "test123456")
        response = self.client.post(reverse('marketplace:buy_product', args=[self.seller_profile.slug, self.product.slug]))

        self.seller_profile.save()
        
        self.assertFalse(self.product.is_sold)
        self.assertEqual(self.seller_profile.account_balance, inital__seller_balance)
        self.assertEqual(self.buyer_profile.account_balance, 5.00)


        

