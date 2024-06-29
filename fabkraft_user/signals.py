from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from .models import cart, UserData, Products, product_choices
from django.contrib.auth.signals import user_logged_in


@receiver(user_logged_in)
def transfer_session_cart_to_user(sender, user, request, **kwargs):
    session_cart = request.session.get('cart', [])
    print("Signal triggered. Session cart:", session_cart)  # Debugging statement

    if session_cart:
        user_data = get_object_or_404(UserData, user=user)
        for item in session_cart:
            product = get_object_or_404(Products, id=item['product_id'])
            variant_id = item.get('verient_id')
            quantity = item.get('quantity')

            if quantity is not None:
                if variant_id:
                    variant = get_object_or_404(product_choices, id=variant_id)
                    cart_obj, created = cart.objects.get_or_create(
                        user=user_data, products_id=product.id, verients_id=variant_id, quantity=quantity)
                else:
                    cart_obj, created = cart.objects.get_or_create(
                        user=user_data, products_id=product.id, quantity=quantity)
            else:
                quantity=1
                if variant_id:
                    variant = get_object_or_404(product_choices, id=variant_id)
                    cart_obj, created = cart.objects.get_or_create(
                        user=user_data, products_id=product.id, verients_id=variant_id, quantity=quantity)
                else:
                    cart_obj, created = cart.objects.get_or_create(
                        user=user_data, products_id=product.id, quantity=quantity)

            # Adjust quantity handling based on your needs
            #cart_obj.quantity += 1  # Example adjustment, modify as needed
            cart_obj.save()

        request.session['cart'] = []  # Clear session cart after transferring
        print("Session cart transferred to user cart.")
    else:
        print("No items in session cart.")
