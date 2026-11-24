from datetime import date

from .models import Enrollment, StudentDocument

REQUIRED_DOCS = ["Birth certificate", "Form 138 / Report card", "Good moral certificate"]


def create_pending_enrollment(student, program, year_level, academic_year, semester):
    extra = {}
    # Only set enrollment_date if your model has it
    if "enrollment_date" in {f.name for f in Enrollment._meta.get_fields()}:
        extra["enrollment_date"] = date.today()
    return Enrollment.objects.create(
        student=student,
        program=program,
        year_level=year_level,
        academic_year=academic_year,
        semester=semester,
        status="Pending",
        **extra,
    )


def create_required_documents(student):
    for doc in REQUIRED_DOCS:
        StudentDocument.objects.get_or_create(student=student, document_type=doc)