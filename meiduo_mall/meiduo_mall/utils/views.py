from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


# 作为需要登录类试图的基类
class LoginRequiredView(LoginRequiredMixin, View):
    pass
