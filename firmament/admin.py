from django.contrib import admin

from firmament.models import Case, Series, Volume, Proof

admin.site.register(Series)
admin.site.register(Volume)
admin.site.register(Case)
admin.site.register(Proof)
