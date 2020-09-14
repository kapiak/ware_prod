from typing import List

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from assistant.orders.models import Order
from assistant.products.models import Product


class DashboardViewMixin(LoginRequiredMixin):
    title: str = None
    breadcrumbs: List = []

    def get_title(self):
        return self.title

    def get_context_data(self):
        context = super().get_context_data()
        context.update({'title': self.get_title()})
        return context


class DashboardTemplateView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'orders': Order.objects.all(),
            'products': Product.objects.all()
        })
        return context
