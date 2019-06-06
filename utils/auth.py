from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect, reverse
from web import models
from django.forms import ModelForm


class AuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path_info.startswith('/admin/'):
            return
        if request.path_info in [reverse('login')]:
            return
            # 获取用户ID
        pk = request.session.get('user_id')
        user = models.UserProfile.objects.filter(pk=pk).first()
        if user:
            request.account = user
        else:
            return redirect(reverse('login'))


class NewModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(NewModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


class Response(MiddlewareMixin):
    def process_template_response(self, request, response):
        response.context_data["user"] = request.account
        return response
