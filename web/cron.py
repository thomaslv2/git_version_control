from django.shortcuts import render
from django.http import JsonResponse
from .cron_form import CronForm
from .models import Cron
from utils.pagination import Pagination
from django.template.response import TemplateResponse
from utils.ansible2.runner import AdHocRunner
from utils.ansible2.inventory import Inventory


def cronall(request):
    search = request.GET.get("table_search", '')
    crons = Cron.objects.filter(name__contains=search)
    pager = Pagination(request.GET.get('page', '1'), crons.count(), request.GET.copy(), 10)
    return TemplateResponse(request, 'cronlist.html',
                            {"crons": crons[pager.start:pager.end], "page_title": "计划任务列表",
                             'page_html': pager.page_html})


def create_cron(request, pk=0):
    cron = Cron.objects.filter(pk=pk).first()
    form = CronForm(instance=cron)
    if request.method == "POST":
        time = request.POST.getlist("time")
        form = CronForm(request.POST, instance=cron)
        if form.is_valid():
            host_data = []
            form.instance.create_user = request.account
            form.instance.time = time
            for h in form.cleaned_data['hosts_list']:
                host_data.append({"hostname": h.hostip, "ip": h.hostip, "port": h.ssh_port})  # 主机列表
            print(host_data)
            inventory = Inventory(host_data)  # 动态生成主机配置信息
            runner = AdHocRunner(inventory)
            tasks = [
                {"action": {"module": 'cron',
                            "args": "minute={} hour={} day={} month={} weekday={} name={} job={} user={}".format(
                                time[0], time[1], time[2], time[3], time[4], form.cleaned_data['name'],
                                form.cleaned_data['job'], form.cleaned_data['user'])}}
            ]
            ret = runner.run(tasks)
            if not ret.results_raw["ok"]:
                return JsonResponse({"status": 1, "msg": "添加失败"})
            form.save()
            return JsonResponse({"status": 0, "msg": "添加成功"})
        else:
            return JsonResponse({"status": 1, "msg": "添加失败,失败的原因是{}".format(form.errors)})
    page_title = "新增计划任务" if not pk else "编辑计划任务"
    time = None if not pk else cron.time
    return TemplateResponse(request, "cron_create.html",
                            {"form": form, "pk": pk, "page_title": page_title, "time": time})


def del_cron(req, pk):
    cron = Cron.objects.filter(pk=pk).first()
    host_data = []
    for h in cron.hosts_list.all():
        host_data.append({"hostname": h.hostip, "ip": h.hostip, "port": h.ssh_port})  # 主机列表
    print(host_data)
    inventory = Inventory(host_data)  # 动态生成主机配置信息
    runner = AdHocRunner(inventory)
    tasks = [
        {"action": {"module": 'cron',
                    "args": "name={} user={} state=absent".format(cron.name, cron.user)
                    }}
    ]
    ret = runner.run(tasks)
    if not ret.results_raw["ok"]:
        return JsonResponse({"status": 1, "msg": "删除失败"})
    cron.delete()
    if cron:
        return JsonResponse({"status": 0, "msg": "删除成功"})
    else:
        return JsonResponse({"status": 1, "msg": "删除失败"})
