from django.shortcuts import render, redirect
from django.db import connection
from mango.models import userAccount, Account, Transactions, Category
from mango.forms import registrationForm, loginForm, accountUpdateForm, addAccountForm, addTransactionForm, queryForm
from django.contrib.auth import login,logout, authenticate
from django.views import View
import datetime

# Create your views here.
def index_view(request):
    context = {}

    user = request.user


    if(request.POST):
        # DO Post Request
        form = queryForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data["startDate"]
            end = form.cleaned_data["endDate"]
            minAmount = form.cleaned_data["Min"]
            maxAmount = form.cleaned_data["Max"]

            # Transaction Query with parameters
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT transaction_name, account_name, transaction_amount, transaction_location, transaction_date, category_name 
                    FROM mango_transactions 
                    LEFT JOIN mango_category ON mango_transactions.category_ID = mango_category.category_ID
                    INNER JOIN mango_account ON mango_transactions.account_id = mango_account.account_ID
                    WHERE user_id = %s AND 
                    (transaction_date >= %s AND transaction_date <= %s) AND 
                    (transaction_amount >= %s AND transaction_amount <= %s)
                """, [user.user_id, start, end, minAmount, maxAmount])
                allTransactionsQuery = cursor.fetchall()
                allTransactions = []
                for item in allTransactionsQuery:
                    transactionsDict = {
                        'transaction_name' : item[0],
                        'account_name' : item[1],
                        'transaction_amount' : item[2],
                        'transaction_location' : item[3],
                        'transaction_date' : item[4],
                        'category_name' : item[5]
                    }
                    allTransactions.append(transactionsDict)
                context['allTransactions'] = allTransactions



            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(transaction_amount) 
                    FROM mango_transactions 
                    LEFT JOIN mango_category ON mango_transactions.category_ID = mango_category.category_ID
                    INNER JOIN mango_account ON mango_transactions.account_id = mango_account.account_ID
                    WHERE user_id = %s AND 
                    (transaction_date >= %s AND transaction_date <= %s) AND 
                    (transaction_amount >= %s AND transaction_amount <= %s)
                """, [user.user_id, start, end, minAmount, maxAmount])
                TransactionsQuery = cursor.fetchone()[0]
                context["number_transaction"] = TransactionsQuery

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT AVG(transaction_amount) 
                    FROM mango_transactions 
                    LEFT JOIN mango_category ON mango_transactions.category_ID = mango_category.category_ID
                    INNER JOIN mango_account ON mango_transactions.account_id = mango_account.account_ID
                    WHERE user_id = %s AND 
                    (transaction_date >= %s AND transaction_date <= %s) AND 
                    (transaction_amount >= %s AND transaction_amount <= %s)
                """, [user.user_id, start, end, minAmount, maxAmount])
                TransactionsQuery = round(cursor.fetchone()[0], 2)
                context["average_transaction"] = TransactionsQuery

            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT SUM(transaction_amount) 
                    FROM mango_transactions 
                    LEFT JOIN mango_category ON mango_transactions.category_ID = mango_category.category_ID
                    INNER JOIN mango_account ON mango_transactions.account_id = mango_account.account_ID
                    WHERE user_id = %s AND 
                    (transaction_date >= %s AND transaction_date <= %s) AND 
                    (transaction_amount >= %s AND transaction_amount <= %s)
                """, [user.user_id, start, end, minAmount, maxAmount])
                TransactionsQuery = cursor.fetchone()[0]
                context["sum_transaction"] = TransactionsQuery


                newForm = queryForm(    initial={'startDate': start, 'endDate': end, "Min" : minAmount, "Max" : maxAmount }) 
                
                context['query_form'] = newForm

        else:
            context['query_form'] = form
    else:
        # Regular transaction
        form = queryForm()
        context['query_form'] = form
        # Transaction Query
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT transaction_name, account_name, transaction_amount, transaction_location, transaction_date, category_name 
                FROM mango_transactions 
                LEFT JOIN mango_category ON mango_transactions.category_ID = mango_category.category_ID
                INNER JOIN mango_account ON mango_transactions.account_id = mango_account.account_ID
                WHERE user_id = %s
            """, [user.user_id])
            allTransactionsQuery = cursor.fetchall()
            allTransactions = []
            for item in allTransactionsQuery:
                transactionsDict = {
                    'transaction_name' : item[0],
                    'account_name' : item[1],
                    'transaction_amount' : item[2],
                    'transaction_location' : item[3],
                    'transaction_date' : item[4],
                    'category_name' : item[5]
                }
                allTransactions.append(transactionsDict)
            context['allTransactions'] = allTransactions
        


        # Get number of transactins
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(transaction_name)
                FROM mango_transactions 
                LEFT JOIN mango_category ON mango_transactions.category_ID = mango_category.category_ID
                INNER JOIN mango_account ON mango_transactions.account_id = mango_account.account_ID
                WHERE user_id = %s
            """, [user.user_id])
            TransactionsQuery = cursor.fetchone()[0]
            context["number_transaction"] = TransactionsQuery

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT AVG(transaction_amount)
                FROM mango_transactions 
                LEFT JOIN mango_category ON mango_transactions.category_ID = mango_category.category_ID
                INNER JOIN mango_account ON mango_transactions.account_id = mango_account.account_ID
                WHERE user_id = %s
            """, [user.user_id])
            TransactionsQuery = round( cursor.fetchone()[0], 2)
            context["average_transaction"] = TransactionsQuery    

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(transaction_amount)
                FROM mango_transactions 
                LEFT JOIN mango_category ON mango_transactions.category_ID = mango_category.category_ID
                INNER JOIN mango_account ON mango_transactions.account_id = mango_account.account_ID
                WHERE user_id = %s
            """, [user.user_id])
            TransactionsQuery = cursor.fetchone()[0]
            context["sum_transaction"] = TransactionsQuery       



    return render(request, 'mango/index.html', context=context)

def register_view(request):
    context = {}
    if request.POST:
        form = registrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)
            return redirect('mango:index')
        else:
            context['registration_form'] = form
    else:
        form = registrationForm()
        context['registration_form'] = form
    return render(request, 'mango/register.html', context=context)

def logout_view(request):
    logout(request)
    return redirect('mango:index')

def login_view(request):
    context = {}
    user = request.user
    if user.is_authenticated:
        return redirect('mango:index')

    # User tried to login
    if request.POST:
        form = loginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email=email, password=password)

            if user:
                login(request, user)
                return redirect('mango:index')
    else:
        form = loginForm()
    
    context['login_form'] = form
    return render(request, 'mango/login.html', context=context)

def account_view(request):
    if not request.user.is_authenticated:
        return redirect("mango:login")

    context = {}

    if request.POST:
        form = accountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.initial = {
                "email": request.POST['email'],
                "username": request.POST['username'],
            }
            form.save()
    else:
        form = accountUpdateForm(
            initial={
                "email" : request.user.email,
                "username" : request.user.username,
            }
        )
    context['account_form'] = form
    return render(request, 'mango/account.html', context=context)

def add_account_view(request):
    # Checks if user is signed in
    if not request.user.is_authenticated:
        return redirect("mango:login")

    context = {}

    if request.POST:
        form = addAccountForm(request.POST)
        if form.is_valid():
            # form.save()
            form.save(commit=False)
            form.instance.user = request.user
            form.save()
            return redirect("mango:account")
        else:
            context['add_account_form'] = form
    else:
        form = addAccountForm()
        context['add_account_form'] = form
    return render(request, 'mango/add_account.html', context=context)

def add_transaction_view(request):

    # Checks if user is signed in
    if not request.user.is_authenticated:
        return redirect("mango:login")

    context = {}

    if request.POST:
        form = addTransactionForm(request.POST)
        if form.is_valid():
            # form.save()
            form.save(commit=False)
            form.instance.user = request.user
            form.save()
            return redirect("mango:account")
        else:
            context['add_transaction_form'] = form
    else:
        form = addTransactionForm()
        context['add_transaction_form'] = form

    return render(request, 'mango/add_transaction.html', context=context)