import os
import PyPDF2

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from docx import RT
from model_utils import FieldTracker
from django.db import models

from scripts.convert import load_doc, load_part, save_part


### HELPERS ###

class DeletableManager(models.Manager):
    """
        Manager that excludes results where user_deleted=True by default.
    """
    def get_queryset(self):
        # exclude deleted entries by default
        return super(DeletableManager, self).get_queryset().filter(user_deleted=False)

    def all_with_deleted(self):
        return super(DeletableManager, self).get_queryset()


class DeletableModel(models.Model):
    """
        Abstract base class that lets a model track deletion.
    """
    user_deleted = models.BooleanField(default=False, verbose_name="Deleted by user")
    user_deleted_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def safe_delete(self):
        self.user_deleted = True
        self.user_deleted_timestamp = timezone.now()


### MODELS ###

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
    name_abbreviation = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'Series'

    def __str__(self):
        return self.name_abbreviation

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

class Court(models.Model):
    name = models.CharField(max_length=128, null=True)
    name_abbreviation = models.CharField(max_length=64, null=True)
    jurisdiction = models.CharField(max_length=24, null=True)

class Judge(models.Model):
    name = models.CharField(max_length=128)

class Case(DeletableModel):
    volume = models.ForeignKey(Volume, related_name='cases')
    court = models.ForeignKey(Court, related_name='cases', blank=True, null=True)
    headnotes = models.TextField(null=True)
    name = models.CharField(max_length=1024, null=True)
    name_abbreviation = models.CharField(max_length=256, null=True)
    year = models.IntegerField()
    docket_number = models.CharField(max_length=24, null=True)
    decision_date = models.DateTimeField(null=True)
    first_page = models.IntegerField()
    last_page = models.IntegerField(blank=True, null=True)
    manuscript = models.FileField()
    proofs = models.ManyToManyField(Proof, related_name='cases')
    publication_status = models.CharField(max_length=12,
                              default='draft',
                              choices=(('draft', 'draft'), ('published', 'published'), ('withdrawn', 'withdrawn')),
                              blank=True, null=True)

    tracker = FieldTracker()
    objects = DeletableManager()

    def citation(self):
        return "%s, %s %s-%s (%s)" % (self.name_abbreviation, self.volume, self.first_page, self.last_page or "?", self.year)

    def __str__(self):
        return self.citation()

    def update_last_page_number(self, proof):
        reader = PyPDF2.PdfFileReader(proof.pdf.file)
        self.last_page = self.first_page + reader.getNumPages() - 1
        self.save()
