from django.shortcuts import render
from django.http import JsonResponse
from .project_form import ProjectForm
from .models import Team
from utils.pagination import Pagination
from django.template.response import TemplateResponse
from utils.gitfile import Gitclass
from utils.ansible2.runner import AdHocRunner
from utils.ansible2.inventory import Inventory


def projectall(request):
    search = request.GET.get("table_search", '')
    projects = Team.objects.filter(name__contains=search)
    pager = Pagination(request.GET.get('page', '1'), projects.count(), request.GET.copy(), 10)
    return TemplateResponse(request, 'projectlist.html',
                            {"projects": projects[pager.start:pager.end], "page_title": "项目列表",
                             'page_html': pager.page_html})


def create_project(request, pk=0):
    project = Team.objects.filter(pk=pk).first()
    form = ProjectForm(instance=project)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            print(request.POST)
            print(form.cleaned_data)
            host_data = [{"hostname": h.hostip, "ip": h.hostip, "port": h.ssh_port} for h in form.cleaned_data["host"]]
            inventory = Inventory(host_data)  # 动态生成主机配置信息
            runner = AdHocRunner(inventory)
            tasks = [{"action": {"module": 'file', "args": "path=/data/{} state=directory".format(form.cleaned_data['name'])}}]
            ret = runner.run(tasks)
            if not ret.results_raw["ok"]:
                return JsonResponse({"status": 1, "msg": "添加失败"})
            Gitclass(form.cleaned_data["name"], form.cleaned_data["git_path"])
            form.save()
            return JsonResponse({"status": 0, "msg": "添加成功"})
        else:
            return JsonResponse({"status": 1, "msg": "添加失败,失败的原因是{}".format(form.errors)})
    return render(request, "project_create.html", {"form": form, "pk": pk})


def del_project(req, pk):
    project = Team.objects.filter(pk=pk).delete()
    if project:
        return JsonResponse({"status": 0, "msg": "删除成功"})
    else:
        return JsonResponse({"status": 1, "msg": "删除失败"})


def detail_project(request, pk):
    project = Team.objects.filter(pk=pk).first()
    return render(request, "project_detail.html", {"project": project})
