from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('', views.index, name='income'),
    path('add-income/', views.add_income, name='add-income'),
    path('edit-income/<int:id>', views.income_edit, name='income-edit'),
    path('income-delete/<int:id>', views.income_delete, name='income_delete'),
    path('search-income/', csrf_exempt(views.search_income), name='search_income'),
    path('income_category_summary', views.income_category_summary, name='income_category_summary'),
    path('statsIncome', views.stats_view, name='statsIncome'),
    path('export_csv', views.export_csv, name='export-csv-income'),
    path('export_excel', views.export_excel, name='export-excel-income'),
    path('export-pdf', views.export_pdf, name='export-pdf-income')
]
