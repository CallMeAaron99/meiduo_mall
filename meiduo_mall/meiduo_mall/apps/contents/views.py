from django.shortcuts import render
from django import http


def index(request):
    """ 手机号重复 """
    if request.method == 'GET':
        return render(request, 'index.html')

    return http.HttpResponseForbidden()
