from .models import UserProfile
from django import forms
from utils.auth import NewModelForm

class UserForm(NewModelForm):

    class Meta:
        model = UserProfile
        fields = "__all__"

    def clean_email(self):
        email = self.cleaned_data['email']
        if self.instance.pk:
            count=UserProfile.objects.filter(email=email).count()
            if count == 0 : return email  #表示邮箱没有这个记录
            if email == self.instance.email and count == 1 :
                return email
            raise forms.ValidationError("邮箱已存在！")
        if UserProfile.objects.filter(email=email):
            raise forms.ValidationError("邮箱已存在！")
        return email
