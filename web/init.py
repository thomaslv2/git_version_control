from django.shortcuts import render
from django.http import JsonResponse
from .init_form import InitForm
from .models import Init, InitLog
from utils.pagination import Pagination
from django.template.response import TemplateResponse


def initall(request):
    search = request.GET.get("table_search", '')
    inits = Init.objects.filter(name__contains=search)
    pager = Pagination(request.GET.get('page', '1'), inits.count(), request.GET.copy(), 10)
    return TemplateResponse(request, 'initlist.html',
                            {"inits": inits[pager.start:pager.end], "page_title": "初始化列表",
                             'page_html': pager.page_html})


def create_init(request, pk=0):
    init = Init.objects.filter(pk=pk).first()
    form = InitForm(instance=init)
    if request.method == "POST":
        form = InitForm(request.POST, instance=init)
        if form.is_valid():
            form.instance.create_user = request.account
            form.save()
            return JsonResponse({"status": 0, "msg": "添加成功"})
        else:
            return JsonResponse({"status": 1, "msg": "添加失败,失败的原因是{}".format(form.errors)})
    return render(request, "init_create.html", {"form": form, "pk": pk})


def del_init(req, pk):
    init = Init.objects.filter(pk=pk).delete()
    if init:
        return JsonResponse({"status": 0, "msg": "删除成功"})
    else:
        return JsonResponse({"status": 1, "msg": "删除失败"})


def detail_init(request, pk):
    init = Init.objects.filter(pk=pk).first()
    initall=init.initlog_set.all()
    # initall = InitLog.objects.filter(init=init)
    return render(request,"initlog.html",{"initlogs":initall})