from tempfile import SpooledTemporaryFile

from PyPDF2 import PdfFileMerger
from django.http import HttpResponse
from wsgiref.util import FileWrapper
from rest_framework import viewsets, renderers
from rest_framework.decorators import detail_route
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response

from firmament.models import Volume, Case, Proof
from .serializers import VolumeSerializer, CaseSerializer, ProofSerializer

from scripts.convert_db_xml_html import parse_elements
from scripts.utils import write_file


class VolumeViewSet(viewsets.ModelViewSet):
    queryset = Volume.objects.all()
    serializer_class = VolumeSerializer


    @detail_route(renderer_classes=[renderers.StaticHTMLRenderer])
    def export(self, request, *args, **kwargs):
        volume = self.get_object()
        pdf = PdfFileMerger()
        if volume.front_matter_proofs.exists():
            pdf.append(volume.front_matter_proofs.first().pdf)
        for case in volume.cases.all():
            if case.proofs.exists():
                pdf.append(case.proofs.first().pdf)

        out = SpooledTemporaryFile()
        pdf.write(out)
        out.seek(0)

        response = HttpResponse(FileWrapper(out), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="%s.pdf"' % str(volume).rstrip('.')
        return response


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def partial_update(self, request, *args, **kwargs):
        if 'proof' in request.data:
            instance = self.get_object()
            proof = Proof(docx=request.data['proof'])
            proof.save()
            instance.proofs.add(proof)
            return Response(self.get_serializer(instance).data)

        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.safe_delete()
        instance.save()

class NestedProofViewSet(viewsets.ModelViewSet):
    queryset = Proof.objects.all()
    serializer_class = ProofSerializer

    related_name = None
    parent_pk = None

    def list(self, request, parent_pk=None):
        self.parent_pk = parent_pk
        return super(NestedProofViewSet, self).list(request)

    def create(self, request, *args, **kwargs):
        self.parent_pk = kwargs.pop('parent_pk')
        return super(NestedProofViewSet, self).create(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not serializer.validated_data.get('docx'):
            self.add_blank_instance()
            # TODO: if doesn't exist, throw docx-required validation error
        else:
            serializer.save()
            self.add_instance_to_parent(serializer.instance)

    def get_queryset(self):
        return self.queryset.filter(**{self.related_name+"__id":self.parent_pk})

    def add_instance_to_parent(self, instance):
        getattr(instance, self.related_name).add(self.parent_pk)

class FrontMatterViewSet(NestedProofViewSet):
    related_name = 'front_matter_volumes'

    def add_blank_instance(self):
        self.instance = Volume.objects.get(pk=self.parent_pk).generate_front_matter()

class BackMatterViewSet(NestedProofViewSet):
    related_name = 'back_matter_volumes'

class CaseProofViewSet(NestedProofViewSet):
    related_name = 'cases'

    def create(self, request, *args, **kwargs):
        docx = request.data.get('docx')
        elems = parse_elements(proof=docx, source_path=docx.name)
        case_instance = Case.objects.get(pk=kwargs.get('parent_pk'))
        case_instance.name_abbreviation = elems['casename'].db_name_abbreviation
        case_instance.name = elems['casename'].db_name
        case_instance.decision_date = elems['date'].db_obj
        case_instance.save()

        proof_xml = write_file(docx.name.replace('.docx', '.xml'), case_instance, elems, filetype='xml')
        proof_html = write_file(docx.name.replace('.docx', '.html'), case_instance, elems, filetype='html')

        request.data.update({'xml':proof_xml, 'html':proof_html})

        return super(CaseProofViewSet, self).create(request, *args, **kwargs)
