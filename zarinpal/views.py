# -*- coding: utf-8 -*-
# Github.com/Rasooll
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse, reverse_lazy
from zeep import Client

from accounts.models import User, Profile
from zarinpal.forms import TopUpForm
from zarinpal.models import Transaction

# client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
MERCHANT = '8f1d98e6-f9e5-11e8-868c-005056a205be'
# amount = 100  # Toman / Required
description = "افزایش اعتبار کیف پول وینگ(سامانه کرایه اسکوتر برقی)"  # Required
email = 'email@example.com'  # Optional
# mobile = '09123456789'  # Optional
# CallbackURL = reverse_lazy('verify') # Important: need to edit for realy server.
CallbackURL = 'http://5.253.27.84/zarinpal/verify/' # Important: need to edit for realy server.


def transaction_request(request):
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
    amount = request.GET.get('amount')
    phone = request.GET.get('phone')
    transaction = Transaction(
        user=get_object_or_404(User, phone=phone),
        amount=amount,
        state=0,
        description='درخواست افزایش اعتبار'
    )
    transaction.save()
    result = client.service.PaymentRequest(MERCHANT, amount, description, email, phone, CallbackURL)

    if result.Status == 100:
        transaction.state = 2
        transaction.authority = result.Authority
        # modify
        # transaction.ref_id = result.RefID
        transaction.save()
        return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
    else:
        transaction.state = 1
        transaction.save()
        return HttpResponse('Error code: ' + str(result.Status))


def transaction_verify(request):
    client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')
    authority = request.GET.get('Authority')
    transaction = get_object_or_404(Transaction, authority=authority)
    if request.GET.get('Status') == 'OK':
        transaction.state = 4
        transaction.save()
        result = client.service.PaymentVerification(MERCHANT, authority, transaction.amount)
        if result.Status == 100:
            transaction.ref_id = result.RefID
            transaction.state = 5
            transaction.save()
            transaction.recharge()
            # return redirect('return://zarinpalpayment/')
            # return HttpResponse('تراکنش موفق: ' + str(result.RefID))
            context = {
                'header': 'Wing',
                'title': 'افزایش اعتبار موفق',
                'state': transaction.ref_id,
                # 'form': output_form,
                'url': "wing://payment/",
            }
            return render(request, 'zarinpal/index.html', context)
        elif result.Status == 101:
            transaction.state = 6
            transaction.save()
            # return HttpResponse('تراکنش تکراری: ' + str(result.Status))
            context = {
                'header': 'Wing',
                'title': 'تراکنش تکراری',
                'state': result.Status,
                # 'form': output_form,
                'url': "wing://payment/",
            }
            return render(request, 'zarinpal/index.html', context)
        else:
            transaction.state = 7
            transaction.save()
            # return HttpResponse('تراکنش ناموفق: ' + str(result.Status))
            context = {
                'header': 'Wing',
                'title': 'تراکنش ناموفق',
                'state': result.Status,
                # 'form': output_form,
                'url': "wing://payment/",
            }
            return render(request, 'zarinpal/index.html', context)
    else:
        transaction.state = 3
        transaction.save()
        # return HttpResponse('تراکنش ناتمام')
        context = {
            'header': 'Wing',
            'title': 'تراکنش ناتمام',
            # 'state': result.Status,
            # 'form': output_form,
            'url': "wing://payment/",
        }
        return render(request, 'zarinpal/index.html', context)


@login_required
@permission_required('zarinpal.top_up', login_url="/admin")
def top_up(request, profile_id, phone):
    input_form = TopUpForm(initial={"profile": profile_id})
    # if not input_form.is_valid():
    #     context = {
    #         'header': 'Top up',
    #         'title': phone,
    #         # 'state': 'مرحله اول',
    #         'form': input_form,
    #         'url': '../../top_up/' + str(profile_id) + "/" + str(phone),
    #     }
    #     # print("imsi msisdn form is raw or not valid")
    #     return render(request, 'zarinpal/topup_index.html', context)
    input_form.instance.admin = request.user
    context = {
        'header': 'Top up',
        'title': phone,
        # 'state': 'مرحله اول',
        'form': input_form,
        'url': '../top_up_exe',
    }
    # print("imsi msisdn form is raw or not valid")
    return render(request, 'zarinpal/topup_index.html', context)
    # input_form.save()
    # return redirect('../../admin/zarinpal/topup')


@login_required
@permission_required('zarinpal.top_up')
def top_up_exe(request):
    input_form = TopUpForm(request.POST or None)
    if not input_form.is_valid():
        print()
        context = {
            'header': 'Top up',
            # 'title': phone,
            # 'state': 'مرحله اول',
            'form': input_form,
            'url': '../top_up',
        }
        # print("imsi msisdn form is raw or not valid")
        return render(request, 'zarinpal/topup_index.html', context)
    input_form.instance.admin = request.user
    input_form.save()
    return redirect('../../admin/zarinpal/topup')
