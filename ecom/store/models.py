from django.db import models
import datetime 
from django.contrib.auth.models import User
from django.db.models.signals import post_save



# Profile model for database to store data
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User,auto_now=True)
    phone = models.CharField(max_length=30, blank = True)
    address1 = models.CharField(max_length=200, blank = True)
    address2 = models.CharField(max_length=200, blank = True)
    city = models.CharField(max_length=100, blank = True)
    state = models.CharField(max_length=100, blank = True)
    zipcode = models.CharField(max_length=100, blank = True)
    country = models.CharField(max_length=100, blank = True)
    old_cart = models.CharField(max_length=100, blank = True, null=True)

    def __str__(self):
        return self.user.username
    
# Signal to automatically create a Profile whenever a new User is created
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()

post_save.connect(create_profile,sender=User)







# Category model to group products


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

# Customer model to store customer information    

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.phone} {self.email} {self.password}"


# Product model to store product information
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0,decimal_places=2,max_digits=10)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,default=1)
    description = models.CharField(max_length=500,default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')


    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0,decimal_places=2,max_digits=10)

    def __str__(self):
        return f"{self.name}"


# Order model to handle customer orders

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100 ,default='',blank=True)
    phone = models.CharField(max_length=100 , default='' ,blank=True)
    date = models.DateField(default=datetime.datetime.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.product

