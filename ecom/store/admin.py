from django.contrib import admin
from .models import Category,Product,Customer,Order ,Profile
from django.contrib.auth.models import User

#regiser all models to database for admin access and manipulation
admin.site.register(Category)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Profile)

class ProfileInline(admin.StackedInline):
    model = Profile


# used for profile overwrite to admin panal 
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ["username","first_name","last_name","email"]
    inlines = [ProfileInline]

# unregister the model
admin.site.unregister(User)

# registering the model like refreshing it
admin.site.register(User, UserAdmin)

