from django.shortcuts import render

from firmament.models import Volume


def public(request):
    return render(request, "public.html", {
        "volumes": Volume.objects.all()
    })
