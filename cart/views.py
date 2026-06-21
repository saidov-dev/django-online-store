from django.shortcuts import render, redirect

from store import settings
from .utils import get_cart_data, CartFormAuthenticatedUser, CartForAnonymousUser
from django.urls import reverse
from .forms import CustomerForm, ShippingAddressForm
import stripe


# Create your views here.


def cart_view(request):
    cart_info = get_cart_data(request)
    context = {
        "cart_total_quantity": cart_info["cart_total_quantity"],
        "cart_total_price": cart_info["cart_total_price"],
        "order": cart_info["order"],
        "products": cart_info["products"]
    }
    return render(request, "pages/cart.html", context)


def to_cart(request, product_id, action):
    if not request.user.is_authenticated:
        session_cart = CartForAnonymousUser(request, product_id, action)
    else:
        user_cart = CartFormAuthenticatedUser(request, product_id, action)

    return redirect("cart")



def checkout_view(request):
    cart_info = get_cart_data(request)
    context = {
        "customer_form": CustomerForm(),
        "shipping_form": ShippingAddressForm(),
        "order": cart_info["order"],
        "products": cart_info["products"]
    }
    return render(request, "pages/checkout.html", context)


def create_checkout_session(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if request.method == "POST":
        if not request.user.is_authenticated:
            user_cart = CartForAnonymousUser(request)
        else:
            user_cart = CartFormAuthenticatedUser(request)

        cart_info = user_cart.get_cart_info()
        total_price = cart_info["cart_total_price"]

        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": "Товары с сайта Boutique"
                        },
                        "unit_amount": int(total_price * 100)
                    },
                    "quantity": 1
                }
            ],
            mode="payment",
            success_url=request.build_absolute_uri(reverse("success_payment")),
            cancel_url=request.build_absolute_uri(reverse("success_payment")),
        )

        print(session.url)
        return redirect(session.url, 303)


def success_payment(request):
    if not request.user.is_authenticated:
        user_cart = CartForAnonymousUser(request)
    else:
        user_cart = CartFormAuthenticatedUser(request)

    user_cart.clear()
    return render(request, "pages/success.html")