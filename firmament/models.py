import os

from django.conf import settings
from docx import RT
from model_utils import FieldTracker
from django.db import models

from scripts.convert import load_doc, load_part, save_part


class Proof(models.Model):
    docx = models.FileField(blank=True, null=True)
    pdf = models.FileField(blank=True, null=True)
    pdf_status = models.CharField(max_length=10,
                                  default='pending',
                                    choices=(('pending', 'pending'), ('generated', 'generated'), ('failed', 'failed')),
                                    blank=True, null=True)

    def save(self, *args, **kwargs):
        new_record = not self.pk
        super(Proof, self).save(*args, **kwargs)
        if new_record:
            from .tasks import generate_final
            generate_final.apply_async([self.pk])

    def __str__(self):
        return self.docx.name


class Series(models.Model):
    short_name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Series'

    def __str__(self):
        return self.short_name

class Volume(models.Model):
    series = models.ForeignKey(Series, related_name='volumes')
    volume_number = models.IntegerField()

    front_matter = models.ForeignKey(Proof, blank=True, null=True, related_name='front_matter_volumes')
    back_matter = models.ForeignKey(Proof, blank=True, null=True, related_name='back_matter_volumes')

    def __str__(self):
        return "%s %s" % (self.volume_number, self.series)

    def generate_front_matter(self):
        ### load document
        doc, pq = load_doc(os.path.join(settings.BASE_DIR, "sources/Front Matter Template.docx"))
        header_parts = [load_part(rel.target_part) for rel in doc.part.rels.values() if rel.reltype == RT.HEADER]

        queries = [pq] + [h[2] for h in header_parts]
        for query in queries:

            # set volume number
            query("w|rStyle[w|val='VolumeNumber']").closest('w|r')('w|t').text(str(self.volume_number))

        ### save document
        for header_part, header_el, header_pq in header_parts:
            save_part(header_el, header_part)
        doc.save(os.path.join(settings.BASE_DIR, "test.docx"))



class Case(models.Model):
    volume = models.ForeignKey(Volume, related_name='cases')
    page_number = models.IntegerField()
    short_name = models.CharField(max_length=1024)
    year = models.IntegerField()
    manuscript = models.FileField()
    proof = models.ForeignKey(Proof, blank=True, null=True)

    tracker = FieldTracker()

    def citation(self):
        return "%s, %s %s (%s)" % (self.short_name, self.volume, self.page_number, self.year)

    def __str__(self):
        return self.citation()