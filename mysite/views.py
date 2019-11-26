from django.http import HttpResponse
from django.http import HttpRequest  
from django.shortcuts import render
from django.shortcuts import redirect
from django.template import Context, Template
from django.template import loader
from django.shortcuts import render_to_response
from utils import new_user,authenticate_user,get_authenticated_user_data
import sys
#from django.contrib.gis.geoip import GeoIP
import requests

def index(request):
    return render(request,'index.html')

def suggestions(request):

    code = request.GET.get('code','')


    token = authenticate_user(code)

    
    client_address = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = client_address.split(',')[0]
    print(ip)


    #client_address = request.META.get('HTTP_X_REAL_IP')
    url = 'https://api.ipdata.co/' + ip

    sublist = get_authenticated_user_data(token)

    payload = {"api-key": "54a69eabf71ca58daea3ca176740cedda9c99acd0c6ebe5e239b1696"}
    response = requests.get(url, params=payload)
    response_json = response.json()
    context = {}
    if response.status_code == 200:
        city = response_json["city"]
        country = response_json["country_name"]
        context["country"] = country
        context["city"] = city
        print(response_json)


    context["sublist"] = sublist

    

    return render_to_response('SubSuggest_Final.html',context)
    



def redirect_utils(request):

    url = new_user()
    response = redirect(url)
    return response