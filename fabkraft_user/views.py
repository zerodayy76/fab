from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User
from .models import *
from django.db.models import Q
from django.utils import timezone
from pandas import *
from fuzzywuzzy import fuzz
from itertools import cycle
from django.core.signing import TimestampSigner
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from .token_gen import *
from django.contrib.auth.hashers import make_password
pincode_df = read_csv('datasets/pincode.csv',low_memory=False)

import random
def test(request):
    return render(request,'admin/base.html')


def cart_and_wishlist_count(request):
    cart_count = 0
    wishlist_count = 0
    category = index_top_categories.objects.all().order_by('order')
    if request.user.is_authenticated and request.user.is_superuser == 0:
        cart_count = cart.objects.filter(user=UserData.objects.get(user=request.user)).count()
        wishlist_count = wishlist.objects.filter(user=UserData.objects.get(user=request.user)).count()
    else:
        session_cart = request.session.get('cart', [])
        cart_count = len(session_cart)    
    return {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'category':category,
        'subcategory':sub_Category.objects.all() 
        
    }
def index(request):
    request.session.set_test_cookie()
    index_prod = Products.objects.all()
    index_cat = index_categories.objects.all().order_by('?')[:5]

    carousel = index_carousel.objects.all()
    if 'recently_viewed' not in request.session:
        recent_prod = request.session['recently_viewed']=[]
    else:
        recent_prod = sorted(Products.objects.filter(id__in = request.session['recently_viewed']),
                             key=lambda x: request.session['recently_viewed'].index(x.id))
    print(recent_prod)
    if request.user.is_superuser:
        return redirect('/admin/admin/')
    if request.user.is_authenticated:
        
        context = {
                   'index_prod':index_prod,
                   'index_cat':index_cat,
                   'carousel':carousel,
                    "recent_prod": recent_prod,
                   }
        return render(request,'index1.html',context)
    
    return render(request,'index1.html',{'index_prod':index_prod,'index_cat':index_cat,'carousel':carousel,"recent_prod": recent_prod})
'''
def index(request):
    personal_viewed_cate = []

    # Check if 'category_views' exists in the session
    if 'category_views' not in request.session:
        category_views = request.session['category_views'] = {}
        request.session.modified = True
    else:
        sesson_data = request.session['category_views']
        print(sesson_data)
        sorted_products = dict(sorted(sesson_data.items(), key=lambda item: item[1], reverse=True))
        print(sorted_products)
        for i in sorted_products:
            personal_viewed_cate.append(i)

    print(personal_viewed_cate)

    # Get all categories
    all_categories = sub_Category.objects.all()

    # Order categories based on personal_viewed_cate
    ordered_categories = sorted(all_categories, key=lambda x: personal_viewed_cate.index(x.sub_category) if x.sub_category in personal_viewed_cate else len(personal_viewed_cate))[:5]

    carousel = index_carousel.objects.all()
    category = Category.objects.all()
    offers = index_offers.objects.all()

    print('asd', ordered_categories)

    if 'recently_viewed' not in request.session:
        recent_prod = request.session['recently_viewed'] = []
    else:
        recent_prod = sorted(Products.objects.filter(id__in=request.session['recently_viewed']),
                             key=lambda x: request.session['recently_viewed'].index(x.id))

    if request.user.is_superuser:
        return redirect('admin_index')
    userdata = None
    if request.user.is_authenticated:
        try:
            userdata = UserData.objects.get(user=request.user)
        except:
            return render(request, 'index1.html')
    categories = Category.objects.all()
    category_data = []
    for _ in categories:
        subcategories = _.sub_category_set.all()[:6]  # Get the first 6 subcategories
        subcategory_data = []
        for subcategory in subcategories:
            products = Products.objects.filter(subcategory=subcategory)[:6]  # Get the first 6 products for each subcategory
            subcategory_data.append({'subcategory': subcategory, 'products': products})
        category_data.append({'category': _, 'subcategories': subcategory_data})
    
    # Fetching and shuffling offers
    offers = list(index_offers.objects.all())
    random.shuffle(offers)
    offers = offers[:2]  # Get the first 2 shuffled offers
    


    context = {
        'userdata': userdata,
        'index_cat': ordered_categories,
        'index_prod': Products.objects.all(),
        'carousel': carousel,
        'category': category,
        'category_data': category_data, 
        "recent_prod": recent_prod,
        'offers': offers,
        'vendors': companies.objects.all()
    }

    return render(request, 'index1.html', context)

'''

#-------------------------login and register-------------------------------------------------    

def login_page(request):
    if request.method == 'POST':
        email_ = request.POST.get('email')
        password = request.POST.get('password')
        if password is None:
            if User.objects.filter(email = email_).exists():
                return render(request, 'login/login2.html',{'email':email_})
            else:
                username_ = email_.split("@")[0].split('.')[0]
                return render(request, 'login/register.html',{"email":email_,'username':username_})
        else:
            try:
                username = User.objects.get(email=email_).username 
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    previous_page = request.session.pop('previous_page', '/')
                    return HttpResponseRedirect(previous_page)
 
            except:
                messages.error(request, 'Login failed. Please check your credentials.')
                
            else:
                messages.error(request, 'Login failed. Please check your credentials.')
    
    if request.user.is_authenticated:
        return redirect('profile')
    return render(request, 'login/login.html')


def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        username = request.POST["username"]

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'username is already taken.')
            return redirect('register')
        if len(password) < 8:
            messages.error(request, 'password is weak.')
            return redirect('register')
        # if len(str(phone_number)) != 10:
        #     messages.error(request, 'phone number is not valid')
        #     return redirect('register')
        
        registeruser = User.objects.create_user(username, email, password)
        userdata = UserData.objects.create(user=registeruser)
        # # Generate custom token
        # token = generate_token(registeruser.pk)
        # uid = urlsafe_base64_encode(force_bytes(registeruser.pk))
        # verification_link = request.build_absolute_uri(
        #     reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
        # )
        # print(verification_link)

        # # Sending email verification
        link = request.build_absolute_uri(
             reverse('index')
         )
        subject = 'FabKraft : Thankyou for register in FabKraft'
        message = render_to_string('login/registermail.html', {
            'user': registeruser,
            'link': link,
        })
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = email

        send_mail(subject, message, from_email, [to_email],fail_silently=True)
        user = authenticate(request, username=username, password=password)
        login(request, user)
        messages.success(request, 'Registration successful. Please check your email for verification.')
        previous_page = request.session.pop('previous_page', '/')
        return HttpResponseRedirect(previous_page)
    return render(request, 'login/register.html')

def verify_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user_id = verify_token(token)
        if user_id == int(uid):
            user = User.objects.get(pk=uid)
            userdata_ = UserData.objects.get(user=user)
            userdata_.email_verified = True
            userdata_.save()
            messages.success(request, 'Your email has been verified successfully. You can now log in.')
        else:
            messages.error(request, 'Invalid verification link.')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid verification link.')
    
    return render(request, 'verify.html', {'messages': messages.get_messages(request)})

def forgot_password_page(request):
    if request.user.is_authenticated == 0:
        if request.method == "POST":
            email = request.POST.get("email")
            email_in = User.objects.filter(email=email)
            if email_in.exists():
                # Generate custom token
                token = generate_token(email_in[0].pk)
                uid = urlsafe_base64_encode(force_bytes(email_in[0].pk))
                verification_link = request.build_absolute_uri(
                    reverse('forgorpasswd', kwargs={'uidb64': uid, 'token': token})
                )
                # Sending email verification
                subject = 'Forgot password link'
                message = render_to_string('forgotpasswor.html', {
                    'user': email_in[0].username,
                    'verification_link': verification_link,
                })
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = email
                send_mail(subject, message, from_email, [to_email])
                mess = "reset link is sent to your mail"
                return render(request, "login/forgotpassword1.html",{'messages':mess})
            else:
                messages.error(request, "!! email is not registered")
        return render(request, "login/forgotpassword.html",)
    return redirect('profile')
def forgot_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user_id = verify_token(token)
        print(user_id)
        if user_id == int(uid):
            user = User.objects.get(pk=uid)
            if request.method == "POST":
                user.password = make_password(request.POST.get("password"))
                user.save()
                messages.success(request, "password changed")
                return redirect('login')
            return render(request, 'login/forgotpasswordreal.html', {'messages': messages.get_messages(request)})            
        else:
            messages.error(request, 'Invalid verification link.')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, 'Invalid verification link.')
    
    return render(request, 'login/forgotpasswordreal.html', {'messages': messages.get_messages(request)})
def accounts_logout(request):
    lo=logout(request)
    return redirect('index')

def resend_verify_email(request):
    # Generate custom token
    if request.user.is_authenticated:
        token = generate_token(request.user.pk)
        uid = urlsafe_base64_encode(force_bytes(request.user.pk))
        verification_link = request.build_absolute_uri(
            reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
        )
        # Sending email verification
        subject = 'Verify your email address'
        message = render_to_string('email_verification.html', {
            'user': request.user.username,
            'verification_link': verification_link,
        })
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = request.user.email

        send_mail(subject, message, from_email, [to_email,from_email])
        previous_page = request.session.pop('previous_page', '/')
        return HttpResponseRedirect(previous_page)
    previous_page = request.session.pop('previous_page', '/')
    return HttpResponseRedirect(previous_page)
#-------------------------[ profile ]-------------------------------------------------    

def profile(request):
    if request.method == "POST"  and request.user.is_authenticated:
        userdata_ = UserData.objects.get(user=request.user)
        userdata_.user.first_name = request.POST.get('first_name')
        userdata_.user.last_name = request.POST.get('last_name')
        userdata_.user.username = request.POST.get('username')
        userdata_.user.save()
        return redirect('profile')
    if request.user.is_authenticated:
        return render(request,'profile.html')
    return redirect('index')

#-------------------------[ cart] ---------------------------------------------------------------    
def calculate_shipping_charge(order_price):
    base_charge = setting_values.objects.get(name='shipping').value['base_charge']
    threshold = setting_values.objects.get(name='shipping').value['threshold']
    print(base_charge,type(base_charge),threshold,type(threshold),order_price,type(order_price))
    order_price = float(order_price)



    print('Order Price:', order_price)

    if order_price > 0:
        num_thresholds_exceeded = (order_price - 1) // threshold  # Subtract 1 to handle the case when order_price exactly matches a threshold
        charges = base_charge * (num_thresholds_exceeded + 1)  # Adding 1 to include the first threshold
        print('Charges:', charges)
    else:
        charges = 0
        print('Charges:', charges)
    return charges

def user_cart(request):
    request.session['previous_page'] = request.META.get('HTTP_REFERER', '/')
    cart_items = []

    if request.user.is_authenticated:
        user_data = get_object_or_404(UserData, user=request.user)
        cart_items = cart.objects.filter(user=user_data)
    else:
        session_cart = request.session.get('cart', [])
        prod_id_list = []
        for item in session_cart:
            if item['verient_id'] != None:
                cart_items.append({'id':item['product_id'],'user':None, "products":Products.objects.get(id=item['product_id']),'verients':product_choices.objects.get(id=item['verient_id'])})
            else:
                cart_items.append({'id':item['product_id'],'user':None, "products":Products.objects.get(id=item['product_id']),'verients':None})
    context = {
        'cart': cart_items
    }

    return render(request, 'cart.html', context)

def add_to_cart(request, prod_id):
    request.session['previous_page'] = request.META.get('HTTP_REFERER', '/')
    
    if request.method == 'POST':
        verid = request.POST.get('verient')
        
        # If the user is authenticated, use the database cart
        if request.user.is_authenticated:
            user_data = get_object_or_404(UserData, user=request.user)
            if product_choices.objects.filter(product__id=prod_id).exists() and verid:
                verid = int(verid)
                if not cart.objects.filter(user=user_data, products_id=prod_id, verients_id=verid).exists():
                    cart.objects.create(user=user_data, products_id=prod_id, verients_id=verid)
            else:
                if not cart.objects.filter(user=user_data, products_id=prod_id).exists():
                    cart.objects.create(user=user_data, products_id=prod_id)
            return redirect('cart')
        
        # If the user is not authenticated, use the session cart
        else:
            session_cart = request.session.get('cart', [])
            if product_choices.objects.filter(product__id=prod_id).exists() and verid:
                verid = int(verid)
                item = {'product_id': prod_id, 'verient_id': verid}
                if item not in session_cart:
                    session_cart.append(item)
            else:
                item = {'product_id': prod_id, 'verient_id': None}
                if item not in session_cart:
                    session_cart.append(item)
            request.session['cart'] = session_cart
            return redirect('cart')
    
    return redirect('login')

def remove_from_cart(request, prod_id):
    if request.user.is_authenticated:
        user_data = UserData.objects.get(user=request.user)
        cart_item = cart.objects.filter(user=user_data,products=cart.objects.get(id=prod_id).products)
        cart_item.delete()
    else:
        session_cart = request.session.get('cart', [])
        session_cart = [item for item in session_cart if item['product_id'] != prod_id]
        request.session['cart'] = session_cart
    
    return redirect('cart')

#-------------------------[ wishlist ]-----------------------------------------------------------    

def wish_list(request):
    request.session['previous_page'] = request.META.get('HTTP_REFERER', '/')
    if request.user.is_authenticated:
        context = {
            'cart':wishlist.objects.filter(user=UserData.objects.get(user=request.user))
        }
        return render(request,'wishlist.html',context)
    return redirect('login')

def add_to_wishlist(request,prod_id):
    request.session['previous_page'] = request.META.get('HTTP_REFERER', '/')
    if request.user.is_authenticated:
        if wishlist.objects.filter(user=UserData.objects.get(user=request.user),products = Products.objects.get(id=prod_id)).exists():
            pass
        else:
            wishlist.objects.create(user=UserData.objects.get(user=request.user),products = Products.objects.get(id=prod_id))
            
        return redirect('wishlist')
    return redirect('login')

def update_wishlist(request):
    item_id = request.POST.get('item_id')

    try:
        # Check if the item is already in the wishlist
        wishlist_item = wishlist.objects.get(user=request.user, products=Products.objects.get(id=item_id))
        wishlist_item.delete()
        added = False
    except wishlist.DoesNotExist:
        # If the item is not in the wishlist, add it
        wishlist.objects.create(user=request.user, products=Products.objects.get(id=item_id))
        added = True

    return JsonResponse({"status": 'success'}, safe=False)
        
def remove_from_wishlist(request,prod_id):
    if request.user.is_authenticated:
        
        wishlist.objects.get(user=UserData.objects.filter(user=request.user),id=prod_id).delete()
    return redirect('wishlist')

#-------------------------[ checkout ]-----------------------------------------------------------    

def show_product(request, prod_id):
    is_reviewed = []
    request.session['previous_page'] = request.META.get('HTTP_REFERER', '/')

    review = 'None'
    if request.method == 'POST':
        if request.user.is_authenticated:
            Rating.objects.create(
                user=UserData.objects.get(user=request.user),
                product=Products.objects.get(id=prod_id),
                commands=request.POST.get("review"),
                rate=request.POST.get("rate"),
                review_choice=request.POST.get('review_options'),
            )
        else:
            return redirect('login')
    try:
        product_details = Products.objects.get(id=prod_id)
        reviews = Rating.objects.filter(product=product_details)
        prod_image = images.objects.filter(product = product_details)
        
        if 'recently_viewed' in request.session:
            print('yeah there')
            if prod_id not in request.session['recently_viewed']:
                print('viewd')
                product_details.views +=1
                product_details.save()        
        
                today_date = timezone.now().date()

                product_view, created = product_views.objects.get_or_create(date=today_date, product=product_details)

                if not created:
                    product_view.views += 1
                else:
                    product_view.views = 1

                product_view.save()

        if 'recently_viewed' in request.session:
            if prod_id in request.session['recently_viewed']:
                request.session['recently_viewed'].remove(prod_id)
            
            request.session['recently_viewed'].insert(0,prod_id)

        else:
            request.session['recently_viewed'] = [prod_id]

        request.session.modified = True
        recomendations = Products.objects.filter(
            (Q(subcategory__in=product_details.subcategory.all())) &
            ~Q(id=product_details.id)
        )[:10]
        review_right = False
        if request.user.is_authenticated:
            try:
                review_right = order_products.objects.filter(order__user=UserData.objects.get(user=request.user), products=product_details,order__status = 'Delivered')
                
                review_right = review_right[0].order.status  == 'Delivered'
                print(review_right)
            except IndexError:
                review_right = False

            is_reviewed = Rating.objects.filter(user=UserData.objects.get(user=request.user), product=product_details)
        if len(is_reviewed):
            review = Rating.objects.get(user=UserData.objects.get(user=request.user), product=product_details)
        over_All_rating = 0
        for i in reviews:
            over_All_rating += i.rate
        try:
            over_All_rating = over_All_rating//len(reviews)
        except:
            over_All_rating=0
        print(over_All_rating)
        
        context = {
            "product_details": product_details,
            "review": reviews,
            "base_rate":[1,2,3,4,5],
            "review_count":reviews.count(),
            "is_reviewed": len(is_reviewed),
            "edit_review": review,
            "review_right": review_right,
            "recent_prod": Products.objects.filter(id__in = request.session['recently_viewed']),
            "prod_image":prod_image,
            "recomend":recomendations,
            "overall_ratiing":over_All_rating,
            'review_options':['good','bad','not ok']
        }
    except Products.DoesNotExist:
        return render(request, '404_error.html')

    return render(request, 'detail.html', context)

def edit_review(request,prod_id):
    if request.method == 'POST' and request.user.is_authenticated:
        review = Rating.objects.get(user=UserData.objects.get(user=request.user),product=Products.objects.get(id=prod_id))
        review.review_choice = request.POST.get('review_options')
        review.rate = request.POST.get('rate')
        review.commands = request.POST.get('review')
        review.save()
        return redirect('product_details',prod_id=prod_id)

def product_checkout_page(request,product_id):
    if request.method == 'POST':
        verient = request.POST.get('verient')
        request.session['sng_verient_id'] = verient

    if request.method == 'POST' and request.user.is_authenticated:
        product_ = Products.objects.get(id=product_id)
        print(len(product_choices.objects.filter(product__id=product_id))!=0)
        if len(product_choices.objects.filter(product__id=product_id))!=0:
            verient = request.POST.get('verient')
            if verient is None:
                verient = product_choices.objects.get(id=request.session.get("sng_verient_id"))
            else:                
                verient = product_choices.objects.get(id=verient)

        user_data = UserData.objects.get(user=request.user)
        order_data = orders.objects.filter(user=user_data).last()
        context = {
            'product' : product_,
            'is_single_product_checkout':1,
            'verient':verient,
            'userdata':user_data,
            'orderdata':order_data,
        }
        return render(request,'checkout.html',context)
    
    elif not request.user.is_authenticated:
        request.session['previous_page'] = request.build_absolute_uri()
        return render(request, 'login/login.html')
    
    product_ = Products.objects.get(id=product_id)
    verient = None
    if len(product_choices.objects.filter(product__id=product_id))!=0:
            verient = request.POST.get('verient')
            if verient is None:
                verient = product_choices.objects.get(id=request.session.get("sng_verient_id"))
            else:                
                verient = product_choices.objects.get(id=verient)

    user_data = UserData.objects.get(user=request.user)
    order_data = orders.objects.filter(user=user_data).last()

    context = {
        'product' : product_,
        'is_single_product_checkout':1,
        'verient':verient,
        'userdata':user_data,
        'orderdata':order_data,
    }
    request.session['previous_page'] = request.build_absolute_uri()
    return render(request,'checkout.html',context)

def cart_checkout_page(request):
    if request.method == 'POST' and not request.user.is_authenticated:
        qun_list = request.POST.getlist("quantity")
        print('1st cart',request.session.get('cart',[]))
        request.session['cart_qunity'] = []
        if len(qun_list) != 0:
            for i in qun_list:
                request.session['cart_qunity'].append(i)
        session_cart = request.session.get('cart',[])
        for i in session_cart:
            print(Products.objects.get(id=i['product_id']).product_choices_set.all())
            if Products.objects.get(id=i['product_id']).product_choices_set.all().exists():
                verients = request.POST.get("verients"+str(i['product_id']))
                i['verient_id']  = int(verients)
        request.session['cart'] = session_cart
        print('2nd cart',request.session.get('cart',[]))

    if request.method == 'POST' and request.user.is_authenticated:
        qun_list = request.POST.getlist("quantity")
        cart_ = cart.objects.filter(user=UserData.objects.get(user=request.user))
        if len(cart_) == 0:
            return redirect('cart')
        request.session['cart_qunity'] = []
        
        for i in cart_:
            if i.products.product_choices_set.all().exists():
                verients = request.POST.get("verients"+str(i.id))
                print(i.id)
                i.verients = product_choices.objects.get(id=int(verients))
                i.save()
        if len(qun_list) != 0:
            for i in qun_list:
                request.session['cart_qunity'].append(i)
        else:
            for i in cart_:
                request.session['cart_qunity'].append(i)
        user_data = UserData.objects.get(user=request.user)
        order_data = orders.objects.filter(user=user_data).last()
        
        # zip_ = zip(cart_,request.session['cart_qunity'])
        # print(zip_)
        '''       for i in zip_:
            print(i[0]['products'],i[1])'''
        
        context = {
            'cartdata' : cart_,
            'userdata' : user_data,
            'qun_':qun_list,
            'orderdata':order_data,
            
        }
        request.session['previous_page'] = request.build_absolute_uri()
        return render(request,'checkout.html',context)
    if request.user.is_authenticated:
        cart_ = cart.objects.filter(user=UserData.objects.get(user=request.user))

        if 'cart_qunity' not in request.session:
            request.session['cart_qunity'] = []
            for i in cart_:
                request.session['cart_qunity'].append(1)
        user_data = UserData.objects.get(user=request.user)
        order_data = orders.objects.filter(user=user_data).last()


        
        context = {
            'cartdata' : cart_,
            'userdata' : user_data,
            'orderdata':order_data,
        }
        request.session['previous_page'] = request.build_absolute_uri()
        return render(request,'checkout.html',context)
    request.session['previous_page'] = request.build_absolute_uri()
    return render(request, 'login/login.html')   
def save_checkouts(request):
    if request.method == 'POST' and request.user.is_authenticated:
        name = request.POST.get('user_name')
        email = request.POST.get('email')
        phono = request.POST.get('phone')
        address = request.POST.get('address')
        products = request.POST.getlist('product_id')
        quantity = request.POST.getlist('quantity')
        pincode = request.POST.get('pincode')
        city = request.POST.get('city')
        payment = 'razerpay'
        area = request.POST.get("area")
        payid = request.POST.get('payid')
        
        if not payid or orders.objects.filter(pay_id=payid).exists():
            previous_page = request.session.pop('previous_page', '/')
            return HttpResponseRedirect(previous_page)

        user_ =  User.objects.get(id=request.user.id)
        print('fst lst name',user_.first_name,user_.last_name)
        if user_.first_name is '' and user_.last_name is '':
            user_.first_name = request.POST.get('first_name')
            user_.last_name = request.POST.get('last_name')
            user_.username = request.POST.get("user_name")
            user_.save()
            ud = UserData.objects.get(user=user_)
            ud.phone_number = phono
            ud.save()
        pincode_details = pincode_df[(pincode_df['Pincode'] == int(pincode)) & (pincode_df['OfficeType'] == 'PO')]        
        district = str(pincode_details.iloc[0]['District'])
        state = str(pincode_details.iloc[0]['StateName'])
        total_cost = 0
        print('products',products)
        for prod_id in list(set(products)):
            print('prod id',prod_id)
            product = Products.objects.get(id=prod_id)
            print('exists',prod_id,product_choices.objects.filter(product__id=prod_id).exists())
            if product_choices.objects.filter(product__id=prod_id).exists():
                verids = request.POST.getlist(str(prod_id)+'verient')
                print(verids)
                for verid in verids:
                    quantity_ = int(request.POST.get('quantity'+str(verid)))
                    total_cost += int(product_choices.objects.get(id=verid).options_cost) * quantity_
            else:
                print('justprod',prod_id)
                quantity_ = int(request.POST.get('quantity'+str(prod_id)))
                total_cost +=product.price*quantity_    
                
        
        order = orders.objects.create(
                user=UserData.objects.get(user=request.user),

                name = request.user.username,
                pincode= pincode,
                district = district,
                city = city,
                state = state,
                address=address,
                phno = phono,
                email=email,
                payment_method = payment,    
                pay_id=payid,
                shipping_cost = calculate_shipping_charge(total_cost),
                tax_cost = 00,
                total_cost =  total_cost,   
                is_paid= 1                     
            )
        
        for prod_id in list(set(products)):
            product = Products.objects.get(id=prod_id)
            if product_choices.objects.filter(product__id=prod_id).exists():
                verids = request.POST.getlist(str(prod_id)+'verient')
                print(verids)
                for verid in verids:
                    quantity_ = int(request.POST.get('quantity'+str(verid)))
                    order_products.objects.create(
                        order = order,
                        products = Products.objects.get(id=prod_id),
                        product_price = product_choices.objects.get(id=verid).options_cost,
                        verient = product_choices.objects.get(id=verid),
                        quantity = quantity_,
                    )
            else:
                quantity_ = int(request.POST.get('quantity'+str(prod_id)))
                order_products.objects.create(
                            order = order,
                            products = Products.objects.get(id=prod_id),
                            product_price = Products.objects.get(id=prod_id).price,
                            quantity = quantity_,
                        )
        # Sending email verification
        urlasd = request.build_absolute_uri(
            reverse('order_details', kwargs={'order_id': order.id})
        )
        subject = 'FABKRAFT order placed'
        message = render_to_string('orderplacedmail.html', {
            'user': request.user,
            'orderid': order ,
            'url':urlasd,
        })
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = email

        send_mail(subject, message, from_email, [to_email])
        '''except:
            messages.error(request, 'Error while checkout')'''
        
        
        return redirect('/order_details/'+str(order.id))
    
def order_list(request):
    if request.user.is_authenticated:
        context = {
            'userdata':UserData.objects.get(user=request.user),
            'orders':reversed(orders.objects.filter(user=UserData.objects.get(user=request.user))),
        }
        return render(request,'my order.html',context)
    return redirect('login')

def order_details(request,order_id):
    if request.user.is_authenticated:
        order = orders.objects.get(id=order_id)
        order_product = order_products.objects.filter(order=order)

        context = {
            'order':order,
            'orderproducts':order_product
        }
        request.session['previous_page'] = request.META.get('HTTP_REFERER', '/')
        return render(request,'order_derails.html',context)
    request.session['previous_page'] = request.build_absolute_uri()
    return redirect('login')

def cancel_order(request,order_id):
    if request.method == 'POST' and request.user.is_authenticated:
        order = orders.objects.get(id=order_id)
        canel_Reson = request.POST.get('cancelReason')
        if order.is_canceled==0:
            order.is_canceled  = 1
            order.status = "Cancelled"
            if canel_Reson == 'other':
                order.cancel_reason = request.POST.get('cancelReasontxt')
            else:
                order.cancel_reason = request.POST.get('cancelReason')

        order.save()
        context = {
            'order':order
        }
        return render(request,'order_derails.html',context)
    
    if request.user.is_authenticated:
        order = orders.objects.get(id=order_id)
        context = {
            'order':order
        }
        return render(request,'order_derails.html',context)
    return redirect('login')
#=================================[category page]=========================================

def category_page(request,cat_name):
    if request.method == 'POST':
        selected_subcategories = request.POST.getlist('subcategories')
        print(selected_subcategories)
        # Perform the filtering based on selected_subcategories
        Category_ = Category.objects.get(name=cat_name)
        
        sub_cate = sub_Category.objects.filter(category=Category_)
        
        cat_products = Products.objects.filter(subcategory__sub_category__in=selected_subcategories)
    
        return render(request,'category.html',{'products':cat_products,'cat_name':cat_name,'sub_cate':sub_cate,'selected_cate':selected_subcategories})

    #try:
    Category_ = sub_Category.objects.get(sub_category=cat_name)
    cat_products = Products.objects.filter(subcategory=Category_)
    #sub_cate = sub_Category.objects.filter(category=Category_)
    '''  except:
        cat_products = None
        return render(request,'404_error.html')'''
       
    return render(request,'category.html',{'products':cat_products,'cat_name':cat_name,})

def sub_category_page(request,cat_name):
    if request.method == 'POST':
        selected_subcategories = request.POST.getlist('subcategories')
        print(selected_subcategories)
        # Perform the filtering based on selected_subcategories
        Category_ = Category.objects.get(name=cat_name)
        
        sub_cate = sub_Category.objects.filter(category=Category_)
        
        cat_products = Products.objects.filter(subcategory__sub_category__in=selected_subcategories)
    
        return render(request,'category.html',{'products':cat_products,'cat_name':cat_name,'sub_cate':sub_cate,'selected_cate':selected_subcategories})

    #try:
    Category_ = Category.objects.get(name=cat_name)
    cat_products = Products.objects.filter(category=Category_)
    #sub_cate = sub_Category.objects.filter(category=Category_)
    '''  except:
        cat_products = None
        return render(request,'404_error.html')'''
       
    return render(request,'category.html',{'products':cat_products,'cat_name':cat_name,})
#=============================[search products]===========================================

def search_products(request):
    query = request.GET.get('q', '').strip()
    sorting = request.GET.get('sorting')  # Get the sorting parameter

    if query:
        query_lower = query.lower()

        try:
            keyword = SearchKeyword.objects.get(keyword=query_lower)
            keyword.search_count += 1
            keyword.save()
        except SearchKeyword.DoesNotExist:
            keyword = SearchKeyword.objects.create(keyword=query_lower, search_count=1)
        except Exception as e:
            print(f"Error handling search keyword: {e}")

        # Get all products from the database
        all_products = Products.objects.all()

        # Filter products based on similarity with the query
        results = []
        for product in all_products:
            # Calculate similarity between the query and product name
            name_similarity = fuzz.ratio(query_lower, product.product_name.lower())
            
            # Calculate similarity between the query and product description
            description_similarity = fuzz.ratio(query_lower, product.description.lower())

            # Consider the product if either name or description similarity is above a threshold
            if name_similarity > 20 or description_similarity > 20:
                results.append(product)

        if sorting == 'low_to_high':
            results = sorted(results, key=lambda x: x.price)
        elif sorting == 'high_to_low':
            results = sorted(results, key=lambda x: x.price, reverse=True)

        return render(request, 'shop.html', {'results': results, 'query': query, 'filter': sorting})

    return render(request, 'shop.html', {'results': [], 'query': query})


def get_keyword_suggestions(request):
    query = request.GET.get('q', '').strip().lower()

    if query:
        # Get keyword suggestions from the database
        suggestions = SearchKeyword.objects.filter(keyword__icontains=query)[:5].values_list('keyword', flat=True)
        suggestions = list(suggestions)
    else:
        suggestions = []

    return JsonResponse({'suggestions': suggestions})


#======================myorder=================================================

def FAQ_page(request):
    faq = FAQ.objects.all()
    return render(request,'aboutus/FAQ.html',{'faq':faq})  

def Refunds(request):
    return render(request,'aboutus/Refunds.html')    


def About(request):
    return render(request,'aboutus/About.html')  

def Shipping(request):
    return render(request,'aboutus/Shipping.html')    

def Privacy(request):
    return render(request,'aboutus/privacy.html')  

def Terms(request):
    return render(request,'aboutus/terms.html')      


#=======================================[ CODE ]=======================================

def pincode_details(request):
    if request.method == 'POST':
        pincode = request.POST.get('pincode')
        pincode_details = pincode_df[(pincode_df['Pincode'] == int(pincode)) & (pincode_df['OfficeType'] == 'PO')]        
        dist = str(pincode_details.iloc[0]['District'])
        state = str(pincode_details.iloc[0]['StateName'])
        response_data = {'state': state,'dist':dist}
        
        return JsonResponse(response_data)


def shipping_cost(request):
    if request.method == 'POST':
        total = request.POST.get('total')
        Shipping  = calculate_shipping_charge(total)
        response_data = {'shipping': Shipping}
        
        return JsonResponse(response_data)

def checkmail(request):
    if request.method == 'POST':
        mail = request.POST.get("email")
        response_data = {"has": 0}
        if User.objects.filter(email=mail).exists():
            response_data = {"has": 1}
    return JsonResponse(response_data)
