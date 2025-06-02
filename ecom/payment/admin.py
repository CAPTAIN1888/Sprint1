from django.contrib import admin
from .models import ShippingAddress ,Order,OrderItem
from django.contrib.auth.models import User

admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0


#extend order model

class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = ["user","full_name","email","shipping_address","amount_paid","date_ordered" ,"shipped","date_shipped"]
    inlines = [OrderItemInline]


# unregsiter to register all change
admin.site.unregister(Order)

#register page
admin.site.register(Order, OrderAdmin)


