from .models import Cron
from django import forms
from utils.auth import NewModelForm

class CronForm(NewModelForm):
    # minute=forms.ChoiceField(label="分钟",choices=[(i,i) for i in range(60)])
    # hour=forms.ChoiceField(label="小时",choices=[(i,i) for i in range(24)])
    # day=forms.ChoiceField(label="天",choices=[(i,i) for i in range(1,32)])
    # month=forms.ChoiceField(label="月",choices=[(i,i) for i in range(1,13)])
    # weekday=forms.ChoiceField(label="周",choices=[(i,i) for i in range(0,7)])
    class Meta:
        model = Cron
        exclude=["create_user","time"]


