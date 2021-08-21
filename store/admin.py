from django.contrib import admin
from store import models

# Register your models here.
admin.site.register([
	models.Customer,
	models.Product,
	models.Order,
	models.OrderItem,
	models.ShippingAddress,
	models.Category,
])