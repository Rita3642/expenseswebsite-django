from django.contrib import admin
from .models import Expenses, Category


# Register your models here.
class ExpensesAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'owner', 'category', 'date')


admin.site.register(Expenses, ExpensesAdmin)
admin.site.register(Category)
