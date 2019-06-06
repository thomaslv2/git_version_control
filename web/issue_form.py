from .models import Issue
from  django import forms
from utils.auth import NewModelForm

class GitForm(NewModelForm):

    class Meta:
        model = Issue
        fields = ["team","backup"]




class FileForm(NewModelForm):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}),label="文件")
    class Meta:
        model = Issue
        fields = ["team","backup"]
