from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
import json
from django.http import JsonResponse, HttpResponse

import csv
import xlwt
import datetime

from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile
from django.db.models import Sum
# Create your views here.

 
@login_required(login_url='/authentication/login')
def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user) 
        data = income.values()
        return JsonResponse(list(data), safe=False)

@login_required(login_url='/authentication/login')
def index(request):
    sources = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 3)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    currency = UserPreference.objects.get(user=request.user).currency
    context = { 
        'income':income,
        'page_obj':page_obj,
        'currency':currency,
    }

    return render(request, 'income/index.html', context)
    
@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST,
    }
    



    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not amount:
            messages.error(request, 'Amount is requiered') 
            return render(request, 'income/add_income.html', context)
        
        if not description:
            messages.error(request, 'Description is requiered') 
            return render(request, 'income/add_income.html', context)
        
        UserIncome.objects.create(owner=request.user, amount=amount, date=date, description=description, source=source)

        messages.success(request, 'Record saved successfully')

        return redirect('income')

    return render(request, 'income/add_income.html', context)



    
@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income':income,
        'values':income,
        'sources':sources,
    }
    if request.method == 'GET':
        return render(request, 'income/edit-income.html', context)
    
    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not amount:
            messages.error(request, 'Amount is requiered') 
            return render(request, 'income/edit-income.html', context)
        
        if not description:
            messages.error(request, 'Description is requiered') 
            return render(request, 'income/edit-income.html', context)
        

        income.amount=amount
        income.date=date 
        income.description=description
        income.source=source
        income.save()

        messages.success(request, 'Record updated successfully')





        return render(request, 'income/edit-income.html', context)


@login_required(login_url='/authentication/login')
def income_delete(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()

    messages.success(request, 'Record Removed')
    return redirect('income')


def income_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date-datetime.timedelta(days=30*6)
    income = UserIncome.objects.filter(
        owner=request.user,
        date__gte=six_months_ago, 
        date__lte=todays_date
    )
    
    finalrep = {}

    def get_category(income):
        return income.source

    category_list = list(set(map(get_category, income)))


    def get_expense_category_amount(source):
        amount = 0
        filtered_by_category = income.filter(source=source)

        for item in filtered_by_category:
            amount += item.amount

   
        return amount


    for x in income:
        for y in category_list:
            finalrep[y] = get_expense_category_amount(y)

    # import pdb
    # pdb.set_trace()


    return JsonResponse({'income_category_data':finalrep}, safe=False)




def stats_view(request):
    return render(request, 'income/statsIncome.html')
    





def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Income'+str(datetime.datetime.now())+'.csv'

    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Source', 'Date'])

    incomes = UserIncome.objects.filter(owner=request.user)

    for income in incomes:
        writer.writerow([income.amount, income.description, income.source, income.date])


    return response


def export_excel(request):
    response = HttpResponse(content_type='aplication/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Income'+str(datetime.datetime.now())+'.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('incomes')

    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True 

    columns = ['Amount', 'Description', 'Source', 'Date']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    font_style = xlwt.XFStyle()
    
    rows = UserIncome.objects.filter(owner=request.user).values_list(
        'amount', 'description', 'source', 'date')
    
    for row in rows:
        row_num += 1

        for col_num in range(len(row)):
            ws.write(row_num, col_num, str(row[col_num]), font_style)

    wb.save(response)

    return response


def export_pdf(request):
    response = HttpResponse(content_type='aplication/pdf')
    response['Content-Disposition'] = 'inline; attachment; filename=Income'+str(datetime.datetime.now())+'.pdf'

    response['Content-Transfer-Encoding'] = 'binary'

    incomes = UserIncome.objects.filter(owner=request.user)

    sum = incomes.aggregate(Sum('amount'))

    html_string = render_to_string(
        'income/pdf-output-income.html', {'incomes':incomes, 'total':sum['amount__sum']})

    html = HTML(string=html_string)

    result = html.write_pdf()

    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()

        output = open(output.name, 'rb')
        response.write(output.read())

    return response
