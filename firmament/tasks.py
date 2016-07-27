import tempfile
from io import BufferedReader

from celery import shared_task
import cloudconvert
from django.conf import settings
from django.core.files import File

from firmament.models import Proof, Case


@shared_task
def generate_proof_pdf(proof_id):
    print("TASK CALLED")
    proof = Proof.objects.get(pk=proof_id)
    try:
        if not proof.docx:
            return

        print("Converting proof id=%s, file=%s to PDF." % (proof.id, proof.docx.name))

        api = cloudconvert.Api(settings.CLOUDCONVERT_API_KEY)

        raw_file = proof.docx.file.file
        # extra unwrapping for S3 storage backend
        if hasattr(raw_file, '_file'):
            raw_file = BufferedReader(raw_file._file)  # cloudconvert requires that file isinstance(BufferedReader)
            raw_file.name = proof.docx.name

        process = api.convert({
            "inputformat": "docx",
            "outputformat": "pdf",
            "input": "upload",
            "converteroptions": {
                "pdf_a": True,
            },
            "file": raw_file
        })
        process.wait()

        temp_file = tempfile.NamedTemporaryFile()
        process.download(temp_file.name)
        proof.pdf.save(proof.docx.name.replace('.docx', '.pdf'), File(temp_file))
        proof.pdf_status = "generated"
        proof.save()

        print("Converted! %s status = %s" % (proof.id, proof.pdf_status))

        for case in proof.cases.all():
            case.update_last_page_number(proof)

    except Exception as e:
        proof.pdf_status = "failed"
        proof.save()
        raise
