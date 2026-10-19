from django import forms
from django.conf import settings

from .models import Section


class TextbookForm(forms.Form):
    title = forms.CharField(max_length=200)


class AddContentForm(forms.Form):
    append_to = forms.ModelChoiceField(
        queryset=Section.objects.none(),
        required=False,
        empty_label="A new section",
        label="Add to",
    )
    title = forms.CharField(
        max_length=200, required=False, label="Section title",
        help_text="Used for a new section. Defaults to the file name, or \u201cUntitled\u201d.",
    )
    text = forms.CharField(
        required=False,
        label="Text",
        widget=forms.Textarea(attrs={"rows": 14, "placeholder": "Write or paste Markdown. Mermaid diagrams go in ```mermaid fences."}),
    )
    pptx = forms.FileField(required=False, label="Or upload a PowerPoint (.pptx) for the AI to turn into text")

    def __init__(self, *args, textbook=None, **kwargs):
        super().__init__(*args, **kwargs)
        if textbook is not None:
            self.fields["append_to"].queryset = textbook.sections.all()

    def clean_pptx(self):
        f = self.cleaned_data.get("pptx")
        if f:
            if not f.name.lower().endswith(".pptx"):
                raise forms.ValidationError("Please upload a .pptx file.")
            if f.size > settings.MAX_PPTX_BYTES:
                raise forms.ValidationError("That file is too large (25 MB max).")
        return f

    def clean(self):
        data = super().clean()
        text = (data.get("text") or "").strip()
        data["text"] = text
        has_file = bool(data.get("pptx"))
        if text and has_file:
            raise forms.ValidationError("Provide either text or a .pptx file, not both.")
        if not text and not has_file and not self.errors:
            raise forms.ValidationError("Enter some text or upload a .pptx file.")
        return data


class PreferencesForm(forms.Form):
    api_key = forms.CharField(
        label="AI API key",
        required=False,
        strip=True,
        widget=forms.PasswordInput(render_value=False, attrs={"autocomplete": "off"}),
        help_text="Leave blank to keep the current key.",
    )
    clear_key = forms.BooleanField(required=False, label="Remove my saved key")
    ai_model = forms.ChoiceField(
        label="AI model",
        choices=[("", "Site default")] + list(settings.AI_MODEL_CHOICES),
        required=False,
        help_text="Use the cheapest model while testing to keep costs down.",
    )
