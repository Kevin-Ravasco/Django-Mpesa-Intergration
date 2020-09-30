# Django-Mpesa-Intergration
Intergrating mpesa into django. Incorporates Mpesa's STK push, C2B, B2C and Lipa na Mpesa Online into django

make sure you download ngork and use its secure endpoint (https) in testing. Local server
runs on http and this will not work as safaricom expects a secure connection.

after running your development server on lets say port 8000, open ngrok and run this command:

ngrok http 8000

then copy and paste the https generated endpoint into the project's
ngrok.py file and settings.py file in ALLOWED_HOSTS

NOTE:
make sure you register an account and create an app in https://developer.safaricom.co.ke/
use your phone number in views.py to get STK push

feel free to enquire or ask for clarifications
