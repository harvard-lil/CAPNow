from django.contrib.syndication.views import Feed
#from django.urls import reverse
from firmament.models import Case

class LatestEntriesFeed(Feed):
    title = "Feed of CAPNow cases"
    link = "/cases/"
    description = "a stream of cases"

    def items(self):
        return Case.objects.order_by('-year')[:5]

    def item_title(self, item):
        return item.short_name

    def item_description(self, item):
        return "%s | %s | %s" % (item.short_name, item.year, item.publication_status)

    def item_link(self, item):
        return "http://anastaisas-link-to-the-xml-version" #reverse('news-item', args=[item.pk])
