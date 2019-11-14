from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.template import Context, Template
from django.template import loader
from django.shortcuts import render_to_response
from utils import new_user,authenticate_user,get_authenticated_user_data

def index(request):
    return render(request,'index.html')

def suggestions(request):

    code = request.GET.get('code','')
    #breakpoint()
    token = authenticate_user(code)
    sublist = get_authenticated_user_data(token)
    context = {}
    context["sublist"] = sublist

    return render_to_response('SubSuggest_Final.html',context)
    #return render(request,'SubSuggest_Final.html',context)

#def utils(request):
#
#    new_user()
#    return render(request,'SubSuggest_Final.html')

def redirect_utils(request):

    url = new_user()
    response = redirect(url)
    return response