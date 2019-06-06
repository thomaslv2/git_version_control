from .models import Init
from django import forms
from utils.auth import NewModelForm

class InitForm(NewModelForm):

    class Meta:
        model = Init
        exclude = ["create_user"]

    def clean_function(self):
        function = self.cleaned_data['function']
        if self.instance.pk:
            count=Init.objects.filter(function=function).count()
            if count == 0 : return function  #表示邮箱没有这个记录
            if function == self.instance.function and count == 1 :
                return function
            raise forms.ValidationError("邮箱已存在！")
        if Init.objects.filter(function=function):
            raise forms.ValidationError("邮箱已存在！")
        return function
