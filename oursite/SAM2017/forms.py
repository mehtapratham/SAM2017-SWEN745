from django import forms
from SAM2017.models import Paper

class PaperForm(forms.ModelForm):
    class Meta:
        model = Paper
        fields = ('title','description','file')