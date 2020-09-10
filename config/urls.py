from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token

from wagtail.core import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("assistant.users.urls", namespace="users")),
    path("ht/", include("health_check.urls")),
    path("accounts/", include("allauth.urls")),
    # Wagtail Admin
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # Your stuff: custom urls includes go here
    path("pages/", include("assistant.pages.urls", namespace="pages")),
    path("products/", include("assistant.products.urls", namespace="products")),
    path("purchases/", include("assistant.purchases.urls", namespace="purchases")),
    path("orders/", include("assistant.orders.urls", namespace="orders")),
    path("warehouse/", include("assistant.warehouse.urls", namespace="warehouse")),
    path("shipping/", include("assistant.shipping.urls", namespace="shipping")),
    path(
        "weblink-channel/",
        include("assistant.weblink_channel.urls", namespace="weblink_channel"),
    ),
    path("shopify/", include("assistant.shopify_sync.urls"), name="shopify_sync"),
    path("api/", include("config.api_router")),
    path("auth-token/", obtain_auth_token),
    # Wagtail CMS
    path("", include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

# API URLS
# urlpatterns += [
#     # API base url
#     path("api/", include("config.api_router")),
#     # DRF auth token
#     path("auth-token/", obtain_auth_token),
#     # Wagtail CMS
#     path('', include(wagtail_urls)),
# ]

if settings.USE_SILK:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
