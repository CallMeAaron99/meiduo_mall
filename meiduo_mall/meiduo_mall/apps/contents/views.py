from django.shortcuts import render
from django.views import View
from django import http


def index(request):
    """ 主页 """
    if request.method == 'GET':

        return render(request, 'index.html')
    else:
        return http.HttpResponseForbidden()
