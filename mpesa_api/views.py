from django.http import HttpResponse, JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth
import json

from .models import MpesaPayment
from .mpesa_credentials import MpesaAccessToken, LipanaMpesaPassword
from .ngrok import NgrokAPIEndpoints


def getAccessToken(request):
    consumer_key = 'L2IlrWa9uRwSTxNhXHlu1ZVCizIEuU4M'   # consumer key of app created in safaricom daraja website. use yours
    consumer_secret = '9GrlforKLGRvAcpQ'    # the apps consumer secret, use yours
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    return HttpResponse(validated_mpesa_access_token)


def lipa_na_mpesa_online(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = {
        "BusinessShortCode": LipanaMpesaPassword.Business_short_code,
        "Password": LipanaMpesaPassword.decode_password,
        "Timestamp": LipanaMpesaPassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": 2547123456789,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPassword.Business_short_code,
        "PhoneNumber": 2547123456789,  # replace with your phone number to get stk push
        "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
        "AccountReference": "Kevin",
        "TransactionDesc": "Testing mpesa stk push"
    }
    response = requests.post(api_url, json=request, headers=headers)
    return HttpResponse('success')


@csrf_exempt
def register_urls(request):  # We use this method to register our confirmation and validation URL with Safaricom.
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"    # we pass the mpesa URL for registering the urls.
    headers = {"Authorization": "Bearer %s" % access_token}     # we pass our mpesa tokens to the header of the request.
    options = {"ShortCode": 600247,
               "ResponseType": "Completed",
               "ConfirmationURL": NgrokAPIEndpoints.ConfirmationUrl, # using secure ngrok endpoints, replace with your generated ngrok endpoint
               "ValidationURL": NgrokAPIEndpoints.ValidationUrl} # using secure ngrok endpoints, replace with your generated ngrok endpoint
    response = requests.post(api_url, json=options, headers=headers)
    return HttpResponse(response.text)


@csrf_exempt
def call_back(request): # you can use this method to capture the mpesa calls. At the moment, the method does nothing.
    pass


@csrf_exempt
def validation(request):
    context = {
        "ResultCode": 0,    # Note if change 0 to any other number, you reject the payment
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))  #  we turn our context to json format since Mpesa expects json format.


@csrf_exempt
def confirmation(request):      # we use this function to save successfully transaction in our database.
    mpesa_body = request.body.decode('utf-8')   #  we get the mpesa transaction from the body by decoding using utf-8
    mpesa_payment = json.loads(mpesa_body)    #  we use json.loads method which will assist us to access variables in our request.
    payment = MpesaPayment(
        first_name=mpesa_payment['FirstName'],
        last_name=mpesa_payment['LastName'],
        middle_name=mpesa_payment['MiddleName'],
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
        reference=mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type=mpesa_payment['TransactionType'],
    )
    payment.save()
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return JsonResponse(dict(context))
