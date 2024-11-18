import re

from django.shortcuts import redirect
from django.urls import reverse


class SimpleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # print("SimpleMiddleware")
        # One-time configuration and initialization.

    def __call__(self, request):
        path = request.path
        """
            1.判断是否登录
            2.判断是否访问
        """
        # 允许后台不登录情况下访问的路径
        print('***:',request.user.is_authenticated)
        print('***:',request.path_info)

        open_urls = ['/admin/login/', '/admin/logout/', '/captchaHostQuery']
        if not request.user.is_authenticated and request.path_info not in open_urls:
            return redirect('/admin/login/')
        response = self.get_response(request)
        return response
