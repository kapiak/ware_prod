from typing import List

from django.contrib.auth.mixins import PermissionRequiredMixin


class DashboardViewMixin(PermissionRequiredMixin):
    title: str = None
    breadcrumbs: List = []

    def get_title(self):
        return self.title

    def get_context_data(self):
        context = super().get_context_data()
        context.update({'title': self.get_title()})
        return context