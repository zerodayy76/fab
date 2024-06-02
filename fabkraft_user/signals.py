from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from .models import *

@receiver(user_logged_in)
def transfer_session_cart_to_user(sender, user, request, **kwargs):
    session_cart = request.session.get('cart', [])
    print("Signal triggered. Session cart:", session_cart)  # Debugging statement

    if session_cart:
        user_data = get_object_or_404(UserData, user=user)
        for item in session_cart:
            product = get_object_or_404(Products, id=item['product_id'])
            if item['verient_id']:
                variant = get_object_or_404(product_choices, id=item['verient_id'])
                cart_obj, created = cart.objects.get_or_create(
                    user=user_data, products=product, verients=variant)
            else:
                cart_obj, created = cart.objects.get_or_create(
                    user=user_data, products=product)
            if created:
                cart_obj.save()
        request.session['cart'] = []  # Clear session cart after transferring
        print("Session cart transferred to user cart.")
    else:
        print("No items in session cart.")
