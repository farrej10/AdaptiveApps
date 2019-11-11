from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    return render(request,'index.html')

def suggestions(request):
    return render(request,'SubSuggest_Final.html')