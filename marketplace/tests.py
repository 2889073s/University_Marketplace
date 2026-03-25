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


class ModelTests(TestCase):
    def setUp(self):
        self.user, self.profile = add_user_profiles("testuser", "test@test.com", "password123")
        self.tag = add_tag("Books")
        self.product = add_product("Django Guide", self.profile, self.tag)

    def test_user_profile_slug_generation(self):
        #Tests if the slug is automatically generated from the username on save.
        self.assertEqual(self.profile.slug, "testuser")

    def test_product_slug_generation(self):
        #Tests if the slug is automatically generated from the product name on save.
        self.assertEqual(self.product.slug, "django-guide")

    def test_tag_string_representation(self):
        #Tests the __str__ method of the Tag model.
        self.assertEqual(str(self.tag), "Books")


class SearchTests(TestCase):
    def setUp(self):
        self.seller_user, self.seller_profile = add_user_profiles("seller2", "seller2@test.com", "password123")
        self.tag = add_tag("Electronics")
        self.product1 = add_product("Python Textbook", self.seller_profile, self.tag)
        self.product2 = add_product("Desk Lamp", self.seller_profile, self.tag)

    def test_search_by_query_string(self):
        #Tests if filtering by query 'Python' returns the correct product.
        response = self.client.get(reverse('marketplace:search_page'), {'q': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.product1, response.context['products'])
        self.assertNotIn(self.product2, response.context['products'])

    def test_search_ajax_request(self):
        #Tests if the AJAX request returns only the partial search results template.
        response = self.client.get(
            reverse('marketplace:search_page'),
            {'q': 'Python'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest' # Simulates AJAX
        )
        self.assertEqual(response.status_code, 200)
        # Verify that it doesn't use the full search.html template
        self.assertNotContains(response, '<!DOCTYPE html>')


class TopUpTests(TestCase):
    def setUp(self):
        self.user, self.profile = add_user_profiles("buyer2", "buyer2@test.com", "password123", account_balance=10.00)

    def test_charge_balance_increases_funds(self):
        #Tests if topping up £30 increases the user's balance from £10 to £40.
        self.client.login(username="buyer2", password="password123")
        
        response = self.client.post(reverse('marketplace:charge_balance'), {'amount': '30.00'})
        
        #Should redirect back to profile page on success
        self.assertEqual(response.status_code, 302)

        self.profile.refresh_from_db()
        self.assertEqual(self.profile.account_balance, 40.00)

    def test_unauthenticated_user_cannot_top_up(self):
        #Tests if topping up requires a logged-in user (redirects to login).
        response = self.client.post(reverse('marketplace:charge_balance'), {'amount': '30.00'})
        self.assertEqual(response.status_code, 302)