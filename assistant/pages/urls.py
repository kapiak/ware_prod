from django.urls import path

from .views import test

app_name = "pages"

urlpatterns = [path("test/", test, name="test")]
