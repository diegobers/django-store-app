from django.shortcuts import render

from django.views.generic import TemplateView


class StoreIndexView(TemplateView):
    template_name = 'store/index.html'