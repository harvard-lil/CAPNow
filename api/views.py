import re

from django.core.files.base import ContentFile
from rest_framework import viewsets
from rest_framework import serializers
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from firmament.models import Volume, Case, Series, Proof
from scripts.convert import convert
from .serializers import VolumeSerializer, CaseSerializer


class VolumeViewSet(viewsets.ModelViewSet):
    queryset = Volume.objects.all()
    serializer_class = VolumeSerializer


class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    parser_classes = (MultiPartParser, FormParser,)

