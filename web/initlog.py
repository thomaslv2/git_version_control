from django.shortcuts import render
from django.http import JsonResponse
from .initlog_form import InitLogForm
from utils.ansible2.runner import PlayBookRunner
from utils.ansible2.inventory import Inventory


def create_initlog(request):
    form = InitLogForm()
    if request.method == "POST":
        form = InitLogForm(request.POST)
        if form.is_valid():
            form.instance.user=request.account
            host_data=[{"hostname":h.hostip,"ip":h.hostip,'port':h.ssh_port} for h in form.cleaned_data["hosts_list"]]
            inventory = Inventory(host_data)
            runner = PlayBookRunner(inventory).run(form.cleaned_data["init"].play_book)
            form.save()
            return JsonResponse({"status": 0, "msg": "添加成功"})
        else:
            return JsonResponse({"status": 1, "msg": "添加失败,失败的原因是{}".format(form.errors)})
    return render(request, "initlog_create.html", {"form": form})
