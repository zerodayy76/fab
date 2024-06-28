"""
URL configuration for fabkraft_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from fabkraft_user import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    #path('test',views.test,name='test'),
    path('',views.index,name='index'),

    path('login/',views.login_page,name='login'),

    path('register/',views.register,name='register'),
    path('verify-email/<str:uidb64>/<str:token>/', views.verify_email, name='verify_email'),
    path('logout/',views.accounts_logout,name='logout'),
    path('forgot_password/',views.forgot_password_page,name="forgorpasswdpage"),
    path('forgot_password/password/<str:uidb64>/<str:token>/',views.forgot_password,name="forgorpasswd"),
    path('resend_verifymail',views.resend_verify_email,name='resendverifymail'),
    #---------------------[ cart ]--------------------------
    path('cart/',views.user_cart,name='cart'),
    path('add_to_cart/<int:prod_id>',views.add_to_cart,name='add_to_cart'),
    path('remove_from_cart/<int:prod_id>',views.remove_from_cart,name='remove_from_cart'),
    #---------------------[ wishist ]--------------------------
    path('wishlist/',views.wish_list,name='wishlist'),
    path('update_wishlist/',views.update_wishlist,name='update_wishlist'),
    path('add_to_wishlist/<int:prod_id>',views.add_to_wishlist,name='add_to_wishlist'),
    path('remove_from_wishlist/<int:prod_id>',views.remove_from_wishlist,name='remove_from_wishlist'),
    
    path('product_details/<int:prod_id>',views.show_product,name='product_details'),
    path('edit_review/<int:prod_id>',views.edit_review,name='edit_review'),
    
    path('checkout/cart/',views.cart_checkout_page,name='checkout_cart'),
    path('checkout/<int:product_id>',views.product_checkout_page,name='checkout_product'),
    
    path('order/',views.save_checkouts,name="order"),
    
    path('order_details/<int:order_id>',views.order_details,name='order_details'),
    path('orders/',views.order_list,name='orders'),
    path('cancelorder/<int:order_id>',views.cancel_order,name='cancel_order'),
    
    path('profile/',views.profile,name='profile'),

    path('subcategory/<str:cat_name>',views.category_page,name='subcategory'),
    path('category/<str:cat_name>',views.sub_category_page,name='category'),

    path('FAQ/',views.FAQ_page,name='FAQ'),
    path('Refunds/',views.Refunds,name='Refunds'),
    path('About/',views.About,name='About'),
    path('Shipping/',views.Shipping,name='Shipping'),
    path('Privacy/',views.Privacy,name='Privacy'),
    path('Terms/',views.Terms,name='Terms'),
    
    path('contact/',views.contact,name='contact'),
    path('pincode_details/', views.pincode_details ,name='pincode_details'),
    path('shipping_cost/', views.shipping_cost ,name='shipping_cost'),

    #======================search==============================
    path('search/', views.search_products, name='search_products'),
    path('get_keyword_suggestions/',views.get_keyword_suggestions,name='get_keyword_suggestions'),
    

    #===================ajax=====================================
    path('test-rzp/',views.rzp_test,name='test_rzp'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
