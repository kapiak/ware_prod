from django.shortcuts import render


def test(request):
    return render(request, "weblink_channel_checkout.html", {})

