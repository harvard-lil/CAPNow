import os
import tempfile
from io import BufferedReader

from celery import shared_task
import cloudconvert
from django.conf import settings
from django.core.files import File

from firmament.models import Proof


@shared_task
def generate_proof_pdf(proof_id):
    print("TASK CALLED")
    proof = Proof.objects.get(pk=proof_id)
    try:
        if not proof.docx:
            return

        print("Converting proof id=%s, file=%s to PDF." % (proof.id, proof.docx.name))

        api = cloudconvert.Api(settings.CLOUDCONVERT_API_KEY)

        # convert proof.docx to a named BufferedReader by writing to temp dir -- required for cloudconvert
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = os.path.join(tmp_dir, proof.docx.name)
            open(tmp_path, 'wb').write(proof.docx.file.read())
            docx = BufferedReader(open(tmp_path, 'rb'))

            process = api.convert({
                "inputformat": "docx",
                "outputformat": "pdf",
                "input": "upload",
                "converteroptions": {
                    "pdf_a": True,
                },
                "file": docx
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
