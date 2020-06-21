from django.contrib import admin
from .models import Product, Category


# list_display is a tuple that will tell the admin
# which fields to display.

# if you want to change the order of the columns in
# the admin you can just adjust the order here in
# the list display attribute.
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'price',
        'rating',
        'image',
    )
# Since it's possible to sort on multiple columns
# note that this does have to be a tuple even
# though it's only one field.
    ordering = ('sku',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'friendly_name',
        'name',
    )


# register our new classes alongside their respective models.
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)