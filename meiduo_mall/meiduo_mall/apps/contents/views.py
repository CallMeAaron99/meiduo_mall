from django.shortcuts import render
from django.views import View
from django import http


class IndexView(View):
    """ 主页 """

    def get(self, request):
        return render(request, 'index.html')
