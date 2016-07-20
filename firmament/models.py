import os
import PyPDF2

from django.conf import settings
from django.core.files.base import ContentFile
from docx import RT
from model_utils import FieldTracker
from django.db import models

from scripts.convert import load_doc, load_part, save_part


class Proof(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    docx = models.FileField(blank=True, null=True)
    pdf = models.FileField(blank=True, null=True)
    pdf_status = models.CharField(max_length=10,
                                  default='pending',
                                    choices=(('pending', 'pending'), ('generated', 'generated'), ('failed', 'failed')),
                                    blank=True, null=True)

    class Meta:
        ordering = ('-timestamp',)

    def save(self, *args, **kwargs):
        new_record = not self.pk
        super(Proof, self).save(*args, **kwargs)
        if new_record:
            from .tasks import generate_proof_pdf
            print("CALLING TASK")
            generate_proof_pdf.apply_async([self.pk])
            if settings.CELERY_ALWAYS_EAGER:
                self.refresh_from_db()

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

    front_matter_proofs = models.ManyToManyField(Proof, related_name='front_matter_volumes')
    back_matter_proofs = models.ManyToManyField(Proof, related_name='back_matter_volumes')

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

        proof_docx = ContentFile(b"")
        doc.save(proof_docx)

        proof = Proof()
        proof.docx.save("%s Front Matter.docx" % self, proof_docx)
        proof.save()

        self.front_matter_proofs.add(proof)

    @property
    def published_cases(self):
        return self.cases.filter(status="published")


class Case(models.Model):
    volume = models.ForeignKey(Volume, related_name='cases')
    page_number = models.IntegerField()
    last_page_number = models.IntegerField(blank=True, null=True)
    short_name = models.CharField(max_length=1024)
    year = models.IntegerField()
    manuscript = models.FileField()
    proofs = models.ManyToManyField(Proof, related_name='cases')
    status = models.CharField(max_length=10,
                              default='draft',
                              choices=(('draft', 'draft'), ('published', 'published'), ('withdrawn', 'withdrawn')),
                              blank=True, null=True)

    tracker = FieldTracker()

    def citation(self):
        return "%s, %s %s-%s (%s)" % (self.short_name, self.volume, self.page_number, self.last_page_number or "?", self.year)

    def __str__(self):
        return self.citation()

    def update_last_page_number(self, proof):
        reader = PyPDF2.PdfFileReader(proof.pdf.file)
        self.last_page_number = self.page_number + reader.getNumPages() - 1
        self.save()

