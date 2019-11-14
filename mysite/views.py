from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
import utils

def index(request):
    return render(request,'index.html')

def suggestions(request):

    code = request.Get.get('code')
    token = authenticate_user(code)
    get_authenticated_user_data(token)


    return render(request,'SubSuggest_Final.html')

#def utils(request):
#
#    new_user()
#    return render(request,'SubSuggest_Final.html')

def redirect_utils(request):

    url = new_user()
    response = redirect(url)
    return response