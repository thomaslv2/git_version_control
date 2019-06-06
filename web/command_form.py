from .models import Command
from django import forms
from utils.auth import NewModelForm

class CommForm(NewModelForm):

    class Meta:
        model = Command
        fields=["command"]


