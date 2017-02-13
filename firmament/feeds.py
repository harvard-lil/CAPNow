from django.contrib.syndication.views import Feed
from firmament.models import Case

from django.utils.feedgenerator import Rss201rev2Feed

class ExtendedRSSFeed(Rss201rev2Feed):
    # we need to jam things into our rss feed that are not found
    # in the common rss elements. we're adding our case data to
    # the our custom, content:encoded, element

    def root_attributes(self):
        attrs = super(ExtendedRSSFeed, self).root_attributes()
        attrs['xmlns:content'] = 'http://purl.org/rss/1.0/modules/content/'
        return attrs
    
    def add_item_elements(self, handler, item):
        super(ExtendedRSSFeed, self).add_item_elements(handler, item)

        if item['content_encoded'] is not None:
            handler.startElement(u"content:encoded", {})
            handler.characters(item['content_encoded'])
            handler.endElement(u"content:encoded")


class CaseFeed(Feed):
    feed_type = ExtendedRSSFeed
    title = "Feed of CAPNow cases"
    link = "/cases/"
    description = "a blowing wind of cases, grab some"

    def item_extra_kwargs(self, item):
        extra = super(CaseFeed, self).item_extra_kwargs(item)
        extra.update({'content_encoded': self.item_case_content(item)})
        extra.update({'media': self.item_case_content(item)})
        return extra
    
    def items(self):
        return Case.objects.order_by('-year')[:500] 

    def item_title(self, item):
        return item.short_name

    def item_subtitle(self, item):
        return "%s | %s | %s" % (item.short_name, item.year, item.status)

    def item_link(self, item):
        return "http://anastaisas-link-to-the-xml-version" #TODO: reverse to this item!!

    def item_case_content(self, item):
        query_obj = Case.objects.get(pk=item.id)
        full_text = "here we build whatever xml CAPDB needs. here's a title for now, %s" % query_obj.short_name

        # TODO: we might need to escape our xml
        #return escape(full_text)

        return full_text
