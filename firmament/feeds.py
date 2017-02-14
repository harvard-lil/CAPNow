from firmament.models import Case, Proof

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

from docx import Document

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
        return item.name_abbreviation

    def item_subtitle(self, item):
        return "%s | %s | %s" % (item.name_abbreviation, item.year, item.publication_status)

    def item_link(self, item):
        return item.proofs.first().docx.url

    def item_case_content(self, item):
        query_obj = Case.objects.get(pk=item.id)

        docs = ''
        all = all_entries = Case.objects.all()
        for case in all:
            # TODO: below, if there are one2m, we should probably pick the best one? or send all of them?
            for proof in case.proofs.all():

                doc = Document(proof.docx)
                fullText = []
                for para in doc.paragraphs:
                    fullText.append(para.text)
            
                docs += '\n'.join(fullText)

        return docs