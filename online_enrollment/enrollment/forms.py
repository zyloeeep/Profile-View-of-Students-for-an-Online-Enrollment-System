from django import forms

from .models import Enrollment

TW = "w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-800"


class EnrollmentForm(forms.ModelForm):
    """Enroll an existing student for a new term."""

    class Meta:
        model = Enrollment
        fields = ["program", "year_level", "academic_year", "semester"]
        widgets = {"academic_year": forms.TextInput(attrs={"placeholder": "2026-2027"})}

    def __init__(self, *args, student=None, **kwargs):
        self.student = student
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", TW)

    def clean(self):
        data = super().clean()
        if self.student and data.get("academic_year") and data.get("semester"):
            if Enrollment.objects.filter(
                student=self.student,
                academic_year=data["academic_year"],
                semester=data["semester"],
            ).exists():
                raise forms.ValidationError("This student is already enrolled for that term.")
        return data