import tempfile

from celery import shared_task
import cloudconvert
from django.conf import settings
from django.core.files import File

from firmament.models import Proof


@shared_task
def generate_final(proof_id):
    proof = Proof.objects.get(pk=proof_id)
    if not proof.docx:
        return

    print("Converting proof to PDF.")

    api = cloudconvert.Api(settings.CLOUDCONVERT_API_KEY)

    process = api.convert({
        "inputformat": "docx",
        "outputformat": "pdf",
        "input": "upload",
        "converteroptions": {
            "pdf_a": True,
        },
        "file": proof.docx.file.file  # unwrap FieldFile -> File -> file
    })
    process.wait()

    temp_file = tempfile.NamedTemporaryFile()
    process.download(temp_file.name)
    proof.pdf.save(proof.docx.name.replace('.docx', '.pdf'), File(temp_file))
    proof.pdf_status = "generated"
    proof.save()

    print("Converted! %s status = %s" % (proof.id, proof.pdf_status))