import asyncio

from django.utils.decorators import sync_and_async_middleware

from ipware import get_client_ip
from assistant.utils.helpers import get_country_by_ip


@sync_and_async_middleware
def ip_address_middleware(get_response):
    """A Middleware to attach the IP Address and if its Routable to the request
    object.
    """
    if asyncio.iscoroutinefunction(get_response):

        async def middleware(request):
            client_ip, is_routable = get_client_ip(request)
            request.client_ip = client_ip
            request.is_client_ip_routable = is_routable
            country = get_country_by_ip(client_ip)
            request.country = country

            response = await get_response(request)
            return response

    else:

        def middleware(request):
            client_ip, is_routable = get_client_ip(request)
            request.client_ip = client_ip
            request.is_client_ip_routable = is_routable
            country = get_country_by_ip(client_ip)
            request.country = country
            response = get_response(request)
            return response

    return middleware
