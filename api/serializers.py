import re

from django.core.files.base import ContentFile
from rest_framework import serializers

from firmament.models import Volume, Case, Proof, Series
from scripts.convert import convert


class ProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proof
        fields = ('timestamp', 'docx', 'pdf', 'pdf_status')
        extra_kwargs = {
            "docx": {"required": False,},
            "timestamp": {"read_only": True},
            "pdf": {"read_only": True},
            "pdf_status": {"read_only": True},
        }

class CaseSerializer(serializers.ModelSerializer):
    proofs = ProofSerializer(required=False, many=True, read_only=True)

    class Meta:
        model = Case
        fields = ('id', 'first_page', 'last_page', 'name_abbreviation', 'year', 'manuscript', 'proofs', 'citation', 'publication_status')
        extra_kwargs = {
            "first_page": {"required": False,},
            "year": {"required": False,},
            "name_abbreviation": {"required": False,},
        }

    def validate(self, data):
        if not 'manuscript' in data:
            if self.partial:
                return data
            raise serializers.ValidationError("Manuscript is required")

        manuscript = data['manuscript']

        # get case info from file name
        m = re.match(r'(.+?), (\d+) (.*?) (\d+) \((\d{4})\).docx', manuscript.name)
        if not m:
            raise serializers.ValidationError("File name must match this pattern: 123 Mass. 456 (2015).docx")
        name_abbreviation, volume_number, series_name, first_page, year = m.groups()

        try:
            series = Series.objects.get(name_abbreviation=series_name)
        except Series.DoesNotExist:
            raise serializers.ValidationError("Unrecognized series name.")

        try:
            volume = series.volumes.get(volume_number=volume_number)
        except Volume.DoesNotExist:
            volume = Volume(volume_number=volume_number, series=series)

        proof_docx = ContentFile(b"")
        convert(manuscript, proof_docx, name_abbreviation, " ".join([volume_number, series_name, first_page]), year)

        return dict(data, volume=volume, name_abbreviation=name_abbreviation, first_page=first_page,
                        year=year, proof_docx=proof_docx)

    def create(self, validated_data):
        validated_data['volume'].save()
        proof_docx = validated_data.pop('proof_docx')
        instance = super(CaseSerializer, self).create(validated_data)
        proof = Proof()
        proof.docx.save(
            validated_data['manuscript'].name.replace('.docx', '.proof.docx'),
            proof_docx)
        proof.save()
        instance.proofs = [proof]
        return instance


class VolumeSerializer(serializers.ModelSerializer):
    series = serializers.StringRelatedField()
    cases = CaseSerializer(many=True, read_only=True)
    front_matter_proofs = ProofSerializer(many=True)
    back_matter_proofs = ProofSerializer(many=True)

    class Meta:
        model = Volume
        fields = ('id', 'series', 'volume_number', 'front_matter_proofs', 'back_matter_proofs', 'cases')
