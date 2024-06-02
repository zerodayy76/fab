from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django.utils.crypto import get_random_string

class UserData(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15,null=True)
    def __str__(self):
        return str(self.user.username)
    
#-----------------------Category-------------------------------------
class Category(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)

class sub_Category(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    sub_category = models.CharField(max_length=225)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return str(self.sub_category)
#----------------------Product-----------------------------------------

class Products(models.Model):
    category =  models.ForeignKey(Category,on_delete=models.CASCADE)
    subcategory =  models.ManyToManyField(sub_Category,null=True,blank=True)
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    product_information = models.TextField()
    max_price = models.DecimalField(max_digits=10,decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    stock = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    views =  models.IntegerField(default=0)  
    
    def __str__(self):
        return str(self.product_name)
    def get_images(self):
        return images.objects.filter(product=self)

class product_views(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    views = models.IntegerField(default=0)
    date = models.DateField(auto_created=True,auto_now=True)

class images(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    images = models.ImageField(upload_to='product_images/')

    def image(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.image.url))
    image.short_description = 'Image'
    image.allow_tags = True

class product_choices(models.Model):
    product = models.ForeignKey(Products,on_delete=models.CASCADE)
    product_options = models.CharField(max_length=225)
    options_cost = models.DecimalField(max_digits=10,decimal_places=2)
    def __str__(self):
        return str(self.product_options)
    
#-----------------------cart-------------------------------------------------------------

class cart(models.Model):
    user = models.ForeignKey(UserData,on_delete=models.CASCADE)
    products = models.ForeignKey(Products,on_delete=models.CASCADE)
    verients = models.ForeignKey(product_choices,on_delete=models.CASCADE,null=True,blank=True)

#-----------------------wishlist-------------------------------------------------------------

class wishlist(models.Model):
    user = models.ForeignKey(UserData,on_delete=models.CASCADE)
    products = models.ForeignKey(Products,on_delete=models.CASCADE)

#-----------------------orders-------------------------------------------------------------

class orders(models.Model):
    status_choice = (
        ('not_Confirmed','not Confirmed'),
        ('order_conformed', 'order conformed'),
        ('shipped', 'shipped'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled')
    )
    user = models.ForeignKey(UserData,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_created=True,auto_now=True)

    name = models.CharField(max_length=225)
    address = models.TextField()
    pincode = models.CharField(max_length=100)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    phno = models.CharField(max_length=15)
    email  = models.CharField(max_length=225)
    district = models.CharField(max_length=225)
    area = models.CharField(max_length=255)
    shipping_cost = models.DecimalField(max_digits=10,decimal_places=2)
    tax_cost = models.DecimalField(max_digits=10,decimal_places=2)
    total_cost = models.DecimalField(max_digits=10,decimal_places=2)
    pay_id = models.CharField(max_length=225)
    status = models.CharField(max_length=225,choices=status_choice,default='not_Confirmed')
    payment_method = models.CharField(max_length=225)
    is_paid = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)    
    cancel_reason = models.TextField(null=True)

    def __str__(self):
        return str(self.id)
class order_products(models.Model):
    order = models.ForeignKey(orders,on_delete=models.CASCADE)
    products = models.ForeignKey(Products,on_delete=models.CASCADE)
    product_price = models.DecimalField(max_digits=10,decimal_places=2)
    verient =  models.ForeignKey(product_choices,on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField()

#------------------------------------index page-------------------------------------------

class index_carousel(models.Model):
    image = models.ImageField(upload_to='carousel_image/')
    name = models.CharField(max_length=225)
    redirect = models.TextField()

class index_top_categories(models.Model):
    category = models.ForeignKey(Category,models.CASCADE)
    order = models.IntegerField(unique=True)

class index_categories(models.Model):
    category = models.ForeignKey(Category,models.CASCADE)
    
class Rating(models.Model):
    date = models.DateField(auto_created=True,auto_now=True)
    user = models.ForeignKey(UserData, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    commands = models.TextField(null=1)
    review_choice = models.CharField(max_length=225,null=True)
    rate = models.IntegerField()
    
#===================search keyword==========================================

class SearchKeyword(models.Model):
    keyword = models.CharField(max_length=255, unique=True)
    search_count = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.keyword
    
#===============================other values constrents===================

class setting_values(models.Model):
    name = models.CharField(max_length=100)
    value = models.JSONField()
    

class FAQ(models.Model):
    questions = models.TextField()
    models = models.TextField()