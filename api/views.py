from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from api.forms import Identity


@csrf_exempt
@api_view(["GET"])
# @api_view(["POST"])
@permission_classes((AllowAny,))
def boosh(request):
    input_form = Identity(request.POST or None)
    context = {
        # 'header': 'ورود',
        # 'title': 123,
        # 'state': 'مرحله اول',
        'form': input_form,
        'url': 'v1/v2',
    }
    # print("imsi msisdn form is raw or not valid")
    return render(request, 'api/topup_index.html', context)


@csrf_exempt
@api_view(["GET"])
# @api_view(["POST"])
@permission_classes((AllowAny,))
def boosham(request):
    # input_form = Identity(request.POST or None)
    # name = str(request.POST['name']) or None
    # if name.__eq__("زهرا") or name.__eq__("") or name.__eq__("") or name.__eq__("") or name.__eq__("") or name.__eq__(""):
    return render(request, 'api/boosh.html')


@csrf_exempt
@api_view(["GET"])
# @api_view(["POST"])
@permission_classes((AllowAny,))
def val(request):
    # input_form = Identity(request.POST or None)
    # name = str(request.POST['name']) or None
    # if name.__eq__("زهرا") or name.__eq__("") or name.__eq__("") or name.__eq__("") or name.__eq__("") or name.__eq__(""):
    return render(request, 'api/val.html')


@csrf_exempt
@api_view(["GET"])
# @api_view(["POST"])
@permission_classes((AllowAny,))
def boosh2(request):
    # input_form = Identity(request.POST or None)
    # name = str(request.POST['name']) or None
    # if name.__eq__("زهرا") or name.__eq__("") or name.__eq__("") or name.__eq__("") or name.__eq__("") or name.__eq__(""):
    return render(request, 'api/index.html')
    # return Response("اندکی صبر... نیمه شب نزدیک است!")
    # context = {
    #     # 'header': 'ورود',
    #     # 'title': 123,
    #     # 'state': 'مرحله اول',
    #     # 'form': input_form,
    #     'message': "hello",
    #     'url': 'v1/v2/',
    # }
    # print("imsi msisdn form is raw or not valid")
