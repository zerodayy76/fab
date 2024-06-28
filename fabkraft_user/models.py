from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import Group, Permission
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.core.validators import MaxValueValidator, MinValueValidator

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
    class Meta:
        verbose_name = "Sub Category"
        verbose_name_plural = "Sub Category"
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
    class Meta:
        verbose_name = "Products"
        verbose_name_plural = "Products"
    def __str__(self):
        return str(self.product_name)
    def get_images(self):
        return images.objects.filter(product=self)
    def get_first_image(self):
        first_image = self.images_set.first()
        if first_image:
            return mark_safe(f'<img src="{first_image.images.url}" width="80" height="80" />')
        return "No Image"

    get_first_image.short_description = 'Image'

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
    options_max_cost = models.DecimalField(max_digits=10, decimal_places=2)  #custom_edit
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
    payment_sts = models.CharField(max_length=225,default='')
    rzp_order_id = models.CharField(max_length=225,default='')
    is_paid = models.BooleanField(default=False)
    is_canceled = models.BooleanField(default=False)    
    cancel_reason = models.TextField(null=True)
    class Meta:
        verbose_name = "Orders"
        verbose_name_plural = "Orders"
    def __str__(self):
        return str(self.id)
    def get_first_image(self):
        first_image = self.order_products_set.first().products.images_set.first()
        if first_image:
            return mark_safe(f'<img src="{first_image.images.url}" width="80" height="80" />')
        return "No Image"

    get_first_image.short_description = 'Image'
class order_products(models.Model):
    order = models.ForeignKey(orders,on_delete=models.CASCADE)
    products = models.ForeignKey(Products,on_delete=models.CASCADE)
    product_price = models.DecimalField(max_digits=10,decimal_places=2)
    verient =  models.ForeignKey(product_choices,on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField()
    def get_first_image(self):
        first_image = self.products.images_set.first()
        if first_image:
            return mark_safe(f'<img src="{first_image.images.url}" width="80" height="80" />')
        return "No Image"
    class Meta:
        verbose_name = "Products"
        verbose_name_plural = "Products"
    get_first_image.short_description = 'Image'

#------------------------------------index page-------------------------------------------

class index_carousel(models.Model):
    image = models.ImageField(upload_to='carousel_image/')
    name = models.CharField(max_length=225)
    redirect = models.TextField()
    class Meta:
        verbose_name = "Carousel"
        verbose_name_plural = "Carousel"
    def get_first_image(self):
        first_image = self.image
        if first_image:
            return mark_safe(f'<img src="{first_image.url}" width="80" height="80" />')
        return "No Image"

    get_first_image.short_description = 'Image'
class index_top_categories(models.Model):
    category = models.ForeignKey(Category,models.CASCADE)
    order = models.IntegerField(unique=True)
    class Meta:
        verbose_name = "top category"
        verbose_name_plural = "top category"
class index_categories(models.Model):
    category = models.ForeignKey(Category,models.CASCADE)
    class Meta:
        verbose_name = "index page category"
        verbose_name_plural = "index page category"

class Rating(models.Model):
    date = models.DateField()
    user = models.CharField(max_length=100)
    stars = models.IntegerField(default=1,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(1)
        ])
    review = models.TextField(null=1)
    country =  models.CharField(max_length=100)

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
    class Meta:
        verbose_name = "settings"
        verbose_name_plural = "settings"

class FAQ(models.Model):
    questions = models.TextField()
    models = models.TextField()
