import re

from django.core.files.base import ContentFile
from rest_framework import serializers

from firmament.models import Volume, Case, Proof, Series
from scripts.convert import convert


class ProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proof
        fields = ('docx', 'pdf', 'pdf_status')

class CaseSerializer(serializers.ModelSerializer):
    proof = ProofSerializer(required=False)

    class Meta:
        model = Case
        fields = ('id', 'page_number', 'short_name', 'year', 'manuscript', 'proof', 'citation')
        extra_kwargs = {
            "page_number": {"required": False,},
            "year": {"required": False,},
            "short_name": {"required": False,},
        }

    def validate(self, data):
        if not 'manuscript' in data:
            raise serializers.ValidationError("Manuscript is required")

        manuscript = data['manuscript']

        # get case info from file name
        m = re.match(r'(.+?), (\d+) (.*?) (\d+) \((\d{4})\).docx', manuscript.name)
        if not m:
            raise serializers.ValidationError("File name must match this pattern: 123 Mass. 456 (2015).docx")
        short_name, volume_number, series_name, page_number, year = m.groups()

        try:
            series = Series.objects.get(short_name=series_name)
        except Series.DoesNotExist:
            raise serializers.ValidationError("Unrecognized series name.")

        try:
            volume = series.volumes.get(volume_number=volume_number)
        except Volume.DoesNotExist:
            volume = Volume(volume_number=volume_number, series=series)

        proof_docx = ContentFile(b"")
        convert(manuscript, proof_docx, short_name, " ".join([volume_number, series_name, page_number]), year)

        return dict(data, volume=volume, short_name=short_name, page_number=page_number,
                        year=year, proof_docx=proof_docx)

    def create(self, validated_data):
        validated_data['volume'].save()
        validated_data['proof'] = Proof()
        validated_data['proof'].docx.save(
            validated_data['manuscript'].name.replace('.docx', '.proof.docx'),
            validated_data.pop('proof_docx'))
        return super(CaseSerializer, self).create(validated_data)

class VolumeSerializer(serializers.ModelSerializer):
    series = serializers.StringRelatedField()
    cases = CaseSerializer(many=True, read_only=True)
    front_matter = ProofSerializer()
    back_matter = ProofSerializer()

    class Meta:
        model = Volume
        fields = ('id', 'series', 'volume_number', 'front_matter', 'back_matter', 'cases')
