from django.shortcuts import render
from django.http import JsonResponse
from .user_form import UserForm
from .models import UserProfile
from utils.pagination import Pagination
from django.template.response import TemplateResponse

def userall(request):
    search = request.GET.get("table_search", '')
    users = UserProfile.objects.filter(name__contains=search)
    pager = Pagination(request.GET.get('page', '1'), users.count(), request.GET.copy(), 10)
    return TemplateResponse(request, 'userlist.html',
                  {"users": users[pager.start:pager.end], "page_title": "用户列表", 'page_html': pager.page_html})


def create_user(request,pk=0):
    user=UserProfile.objects.filter(pk=pk).first()
    form = UserForm(instance=user)
    if request.method == "POST":
        form = UserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": 0, "msg": "添加成功"})
        else:
            return JsonResponse({"status": 1, "msg": "添加失败,失败的原因是{}".format(form.errors)})
    return render(request, "user_create.html", {"form": form,"pk":pk})


def del_user(req,pk):
    user=UserProfile.objects.filter(pk=pk).delete()
    if user:
        return JsonResponse({"status": 0, "msg": "删除成功"})
    else:
        return JsonResponse({"status": 1, "msg": "删除失败"})