from .models import Team, UserProfile
from django import forms
from utils.auth import NewModelForm


class ProjectForm(NewModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["dev_user"].choices = [(du.pk, du.name) for du in UserProfile.objects.filter(role="0")]
        self.fields["test_user"].choices = [(tu.pk, tu.name) for tu in UserProfile.objects.filter(role="1")]
        self.fields["ops_user"].choices = [(ou.pk, ou.name) for ou in UserProfile.objects.filter(role="2")]

    class Meta:
        model = Team
        fields = "__all__"

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance.pk:
            count = Team.objects.filter(name=name).count()
            if count == 0: return name  # 表示邮箱没有这个记录
            if name == self.instance.name and count == 1:
                return name
            raise forms.ValidationError("项目名已存在！")
        if Team.objects.filter(name=name):
            raise forms.ValidationError("项目名已存在！")
        return name
