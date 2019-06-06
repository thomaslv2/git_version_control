from .models import Host
from django import forms
from utils.auth import NewModelForm

class HostForm(NewModelForm):

    class Meta:
        model = Host
        fields = "__all__"

    def clean_hostip(self):
        hostip = self.cleaned_data['hostip']
        if self.instance.pk:
            count=Host.objects.filter(hostip=hostip).count()
            if count == 0 : return hostip  #表示邮箱没有这个记录
            if hostip == self.instance.hostip and count == 1 :
                return hostip
            raise forms.ValidationError("邮箱已存在！")
        if Host.objects.filter(hostip=hostip):
            raise forms.ValidationError("邮箱已存在！")
        return hostip
