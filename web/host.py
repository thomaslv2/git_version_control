from django.shortcuts import render
from django.http import JsonResponse
from .host_form import HostForm
from .models import Host
from utils.pagination import Pagination
from django.template.response import TemplateResponse
from utils.ansible2.runner import AdHocRunner
from utils.ansible2.inventory import Inventory


def hostall(request):
    search = request.GET.get("table_search", '')
    hosts = Host.objects.filter(name__contains=search)
    pager = Pagination(request.GET.get('page', '1'), hosts.count(), request.GET.copy(), 10)
    return TemplateResponse(request, 'hostlist.html',
                  {"hosts": hosts[pager.start:pager.end], "page_title": "主机列表", 'page_html': pager.page_html})


def create_host(request,pk=0):
    host=Host.objects.filter(pk=pk).first()
    form = HostForm(instance=host)
    if request.method == "POST":
        form = HostForm(request.POST,instance=host)
        if form.is_valid():
            host_data = [
                {
                    "hostname": form.cleaned_data['hostip'],
                    "ip": form.cleaned_data['hostip'],
                    "port": form.cleaned_data['ssh_port']
                },
            ]  # 主机列表
            inventory = Inventory(host_data)  # 动态生成主机配置信息
            runner = AdHocRunner(inventory)
            tasks = [
                {"action":{"module":'ping'}}
            ]
            ret = runner.run(tasks)
            if not ret.results_raw["ok"]:
                return JsonResponse({"status": 1, "msg": "添加失败,失败的原因是主机不可达，请检查网络或者配置sshkey"})
            form.save()
            return JsonResponse({"status": 0, "msg": "添加成功"})
        else:
            return JsonResponse({"status": 1, "msg": "添加失败,失败的原因是{}".format(form.errors)})
    return render(request, "host_create.html", {"form": form,"pk":pk})


def del_host(req,pk):
    host=Host.objects.filter(pk=pk).delete()
    if host:
        return JsonResponse({"status": 0, "msg": "删除成功"})
    else:
        return JsonResponse({"status": 1, "msg": "删除失败"})