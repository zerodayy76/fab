from django.contrib import admin
from fabkraft_user.models import *
from django.contrib.admin import AdminSite
# Register your models here.
admin.site.site_header = 'FABKRAFT ADMINSITE'
admin.site.site_title = 'FABKRAFT ADMINSITE'
admin.site.index_title = 'ADMIN'
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import transaction
from django.contrib import messages

admin.site.unregister(Group)

class UserDataInline(admin.TabularInline):
    model = UserData
    extra = 1  # Number of extra forms to display, can be set to 0 if not needed
    fields = ['phone_number']  # Fields to display in the inline form

class UserAdmin(BaseUserAdmin):
    inlines = (UserDataInline,)

# Unregister the original User admin and register the new User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


#===============[products]========================
@transaction.atomic
def duplicate_selected_products(modeladmin, request, queryset):
    for product in queryset:
        original_id = product.id
        product.pk = None  # This resets the primary key field, creating a new object
        product.save()
        
        # Duplicate related images
        original_images = images.objects.filter(product_id=original_id)
        for image in original_images:
            image.pk = None
            image.product = product
            image.save()

        # Duplicate related product choices
        original_choices = product_choices.objects.filter(product_id=original_id)
        for choice in original_choices:
            choice.pk = None
            choice.product = product
            choice.save()

    modeladmin.message_user(request, "Selected products have been duplicated.", messages.SUCCESS)

    duplicate_selected_products.short_description = "Duplicate selected products and their related data"

class ImageInline(admin.TabularInline):
    model = images
    extra = 1
    readonly_fields = ['display_image']

    def display_image(self, obj):
        if obj.images:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.images.url)
        else:
            return None

    display_image.short_description = 'Image Preview'

class ProductChoicesInline(admin.TabularInline):
    model = product_choices
    extra = 1

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_first_image', 'product_name']
    readonly_fields = ['views']
    search_fields = ['product_name', 'description', 'subcategory__name', 'category__name']
    list_filter = ['category', 'subcategory', 'is_active'] 
    inlines = [ImageInline, ProductChoicesInline]
    actions = [duplicate_selected_products]

#===============[orders]==============================
class OrderProductsInline(admin.TabularInline):
    model = order_products
    extra = 1
    readonly_fields = ['order', 'get_first_image','products','product_price','verient','quantity']
    def has_delete_permission(self, request, obj=None):
        return False
@admin.register(orders)
class OrdersAdmin(admin.ModelAdmin):
    readonly_fields = ['user', 'date','address','pincode','city','state','phno','email','area','district','shipping_cost','tax_cost','total_cost','pay_id','payment_method','is_paid','is_canceled','cancel_reason']
    inlines = [OrderProductsInline]
    list_display = ["id","get_first_image","name","status",'pay_id']
    search_fields = ['id', 'name', 'status', 'pay_id']  # Add fields you want to search

class SubCategoryInline(admin.TabularInline):
    model = sub_Category
    extra = 1

class productsInline(admin.TabularInline):
    model = Products
    readonly_fields = ["id","get_first_image","product_name"]
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [SubCategoryInline,productsInline]

#=============[index page]============================



class index_page_customization(AdminSite):
    site_header = 'index page customisation'

indexpage = index_page_customization(name='index page')

class IndexCarouselAdmin(admin.ModelAdmin):
    list_display = ['name','get_first_image']

    # Customize further as needed
    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 200px; max-width: 200px;" />', obj.image.url)
        else:
            return None

    display_image.short_description = 'Image Preview'
    readonly_fields = ['display_image']

class IndexTopCategoriesAdmin(admin.ModelAdmin):
    list_display = ['category', 'order']
    # Customize further as needed

class IndexCategoriesAdmin(admin.ModelAdmin):
    list_display = ['category']
    # Customize further as needed
class adminFAQ(admin.ModelAdmin):
    list_display = ['questions','models']

class index_page_ProductratingChoicesInline(admin.ModelAdmin):
    list_display = ['date','user','stars','review','country']

class index_page_settings(admin.ModelAdmin):
    list_display = ['name','value']


indexpage.register(index_carousel, IndexCarouselAdmin)
indexpage.register(index_top_categories, IndexTopCategoriesAdmin)
indexpage.register(index_categories, IndexCategoriesAdmin)
indexpage.register(FAQ, adminFAQ)
indexpage.register(Rating, index_page_ProductratingChoicesInline)
indexpage.register(setting_values, index_page_settings)
