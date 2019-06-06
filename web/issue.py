from django.shortcuts import render
from django.http import JsonResponse
from .issue_form import GitForm, FileForm
from .models import Issue, Team, Host_Issue
from utils.pagination import Pagination
from django.template.response import TemplateResponse
from utils.gitfile import Gitclass
import time
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import os
import random
from utils.ansible2.runner import AdHocRunner
from utils.ansible2.inventory import Inventory
import openpyxl


def updateall(request):
    search = request.GET.get("table_search", '')
    updateall = Issue.objects.filter(Q(user=request.account) | Q(team__test_user=request.account),
                                     team__name__contains=search)
    pager = Pagination(request.GET.get('page', '1'), updateall.count(), request.GET.copy(), 10)
    return TemplateResponse(request, 'updatelist.html',
                            {"updateall": updateall[pager.start:pager.end], "page_title": "更新列表",
                             'page_html': pager.page_html})


def rollbackall(request):
    search = request.GET.get("table_search", '')
    updateall = Issue.objects.filter(Q(user=request.account) | Q(team__test_user=request.account),
                                     team__name__contains=search, status="6")
    pager = Pagination(request.GET.get('page', '1'), updateall.count(), request.GET.copy(), 10)
    return TemplateResponse(request, 'updatelist.html',
                            {"updateall": updateall[pager.start:pager.end], "page_title": "回滚列表",
                             'page_html': pager.page_html})


def create_git(request, pk=0):
    """
    git更新
    可以基于分支+提交记录更新
    可以基于tag标签更新
    :param request:
    :param pk:
    :return:
    """
    user = Issue.objects.filter(pk=pk).first()
    form = GitForm(instance=user)
    print(request.POST)
    if request.method == "POST":
        form = GitForm(request.POST, instance=user)
        if form.is_valid():
            form.instance.user = request.account
            form.instance.type = "1"
            form.instance.backup_path = str(int(time.time()))
            if request.POST.get('radio', "bra") == "bra":
                Gitclass(form.cleaned_data["team"].name, form.cleaned_data['team'].git_path).update(
                    request.POST.get('bra_select', "master"), request.POST.get("commit_select", "HEAD"), "bra")
            else:
                Gitclass(form.cleaned_data["team"].name, form.cleaned_data['team'].git_path).update(
                    request.POST.get('tag_select', ""), type="tag")
            issue = form.save()
            host_list = form.cleaned_data["team"].host.all()
            # 新增到host——issue表
            for h in host_list:
                Host_Issue.objects.create(issue=issue, team=form.cleaned_data['team'], host=h)
            return JsonResponse({"status": 0, "msg": "添加成功"})
        else:
            return JsonResponse({"status": 1, "msg": "添加失败,失败的原因是{}".format(form.errors)})
    return render(request, "git_create.html", {"form": form, "pk": pk})


def check_bra(request, pk):
    team = Team.objects.filter(pk=pk).first()
    bras = Gitclass(team.name, team.git_path).get_bra()
    return JsonResponse({"status": 0, "data": bras})


def get_commit(request, pk, bra):
    team = Team.objects.filter(pk=pk).first()
    commits = Gitclass(team.name, team.git_path).get_commit(bra)
    return JsonResponse({"status": 0, "data": commits})


def get_tags(request, pk):
    team = Team.objects.filter(pk=pk).first()
    tags = Gitclass(team.name, team.git_path).get_tag()
    return JsonResponse({"status": 0, "data": tags})


def handle_uploaded_file(f, teanmame, t):
    filelist = []
    for file in f:
        filelist.append(file.name)
    if "readme.xlsx" not in filelist:
        return False
    path = "/updata/file/{}/{}".format(teanmame, t)
    if not os.path.exists(path):
        os.makedirs(path)
    for file in f:
        with open(os.path.join(path, file.name), 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
    return True


@csrf_exempt  # 不让csrf做校验
def create_file(request):
    form = FileForm()
    if request.method == "POST":
        print(request.FILES)
        print(request.POST)
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            t = str(int(time.time()))
            form.instance.user = request.account
            form.instance.type = "0"
            form.instance.backup_path = t
            form.instance.update_path = t
            status = handle_uploaded_file(request.FILES.getlist('file_field'), form.cleaned_data["team"].name, t)
            if not status:
                return JsonResponse({"status": 1, "msg": "上传失败，没有readme.xlsx文件"})
            issue = form.save()
            host_list = form.cleaned_data["team"].host.all()
            # 新增到host——issue表
            for h in host_list:
                Host_Issue.objects.create(issue=issue, team=form.cleaned_data['team'], host=h)
            return JsonResponse({"status": 0, "msg": "添加成功"})
        else:
            return JsonResponse({"status": 1, "msg": "添加失败,失败的原因是{}".format(form.errors)})
    return render(request, "file_create.html", {"form": form})


def detail_issue(request, pk):
    issue = Issue.objects.filter(pk=pk).first()
    return render(request, "update_detail.html", {"issue": issue})


def update(request, pk):
    """
    实现更新
    先找其中一台机器
    nginx下线
    更新服务
    等待测试
    位移
    位于  & 只要有0 结果就是0
    位或  | 只要有1  结果就是1
    异或  ^ 相同为0， 不同为1
    <<  左移
    >>  右移
    :param request:
    :param pk:
    :return:
    """
    issue = Issue.objects.filter(pk=pk).first()
    host_issue_all = issue.host_issue_set.all()
    wait_isue_host = random.choice(host_issue_all)
    issue.status = "1"
    issue.save()
    wait_isue_host.status = "1"
    wait_isue_host.save()
    # nginx_status = nginx_server(issue.team.nginxhost.all(), issue.team, [wait_isue_host], 1)
    # server_status = upstarem_server([wait_isue_host], issue.team, issue.backup_path, issue.type)
    nginx_status = True
    server_status = True
    if nginx_status & server_status:
        issue.status = "2"
        issue.save()
        wait_isue_host.status = "2"
        wait_isue_host.save()
        return JsonResponse({"status": 0, "msg": "更新成功"})
    else:
        return JsonResponse({"status": 1, "msg": "更新失败"})


def nginx_server(nginx_list, team, issue_list, type=1):
    """
    :param nginx_list 运行nginx的主机
    :param host_list 运行server的主机
    :param type 1 下线 0 上线
    从nginx的配置文件上下线机器
    找到地址，注释或者去掉注释，并重启nginx 平滑
    :return:
    """
    host_data = [{"hostname": h.hostip, "ip": h.hostip, "port": h.ssh_port} for h in nginx_list]
    inventory = Inventory(host_data)  # 动态生成主机配置信息
    runner = AdHocRunner(inventory)
    task = []
    for il in issue_list:
        if type:
            # 下线
            task.append({"action": {"module": "replace",
                                    "args": "path={} regexp=({}.*) replace=#\\1".format(team.nginxconf,
                                                                                        il.host.hostip)}})
        else:
            # 上线
            task.append({"action": {"module": "replace",
                                    "args": "path={} regexp=(#{}.*) replace=\\1".format(team.nginxconf,
                                                                                        il.host.hostip)}})
    task.append({"action": {"module": "service", "args": "name=nginx state=reloaded"}})
    print("nginx")
    print(task)
    ret = runner.run(task)
    print(ret.results_raw)
    if not ret.results_raw["ok"]:
        return False
    return True


def upstarem_server(host_list, team, t, type):
    """
    先做备份
    文件操作
    :param host_list:后端主机列表
    :param team 项目
    :param t 时间
    :param type 1 git 0 文件
    :return:
    """
    print(host_list)
    host_data = [{"hostname": h.host.hostip, "ip": h.host.hostip, "port": h.host.ssh_port} for h in host_list]
    inventory = Inventory(host_data)  # 动态生成主机配置信息
    runner = AdHocRunner(inventory)
    tasks = [{"action": {"module": "file", "args": "path=/backup/{} state=directory".format(t)}}]
    tasks.append({"action": {"module": "shell", "args": "cp -rf {} /backup/{}/{}".format(team.path, t, team.name)}})
    if type == "1":
        tasks.append({"action": {"module": "copy", "args": "dest={} src=/update/git/{}/".format(team.path, team.name)}})
    else:
        wb = openpyxl.load_workbook("readme.xlsx")
        wb1 = wb["update"]
        for r in wb1.rows():
            tasks.append({"action": {"module": "copy",
                                     "args": "dest={}{} src=/update/file/{}/{}/{}".format(team.path, r[1].value,
                                                                                          team.name, t, r[0].value)}})
    print("server")
    print(tasks)
    ret = runner.run(tasks)
    print(ret.results_raw)
    if not ret.results_raw["ok"]:
        return False
    return True


def successfull(request, pk):
    """
    上线机器
    修改状态
    :param request:
    :param pk:
    :return:
    """
    issue = Issue.objects.filter(pk=pk).first()
    wait_issue_host = issue.host_issue_set.filter(status="2")
    # nginx_status = nginx_server(issue.team.nginxhost.all(), issue.team, wait_issue_host, 0)

    nginx_status = True
    server_status = True
    if nginx_status:

        if issue.host_issue_set.filter(status="0"):  # 判断是否还有没更新的机器
            issue.status = "3"  # 如果有的话，则issue表的status是测试通过， 接着更新
        else:
            issue.status = "4"  # 如果没有的话，则代表所有的更新已经完成，那么issue表的状态则为更新完成
        issue.save()
        wait_issue_host.update(status="3")
        return JsonResponse({"status": 0, "msg": "更新成功"})
    else:
        return JsonResponse({"status": 1, "msg": "更新失败"})


def again_update(request, pk):
    """
    更新剩余的所有机器
    nginx下线
    服务更新
    等待测试
    :param request:
    :param pk:
    :return:
    """
    issue = Issue.objects.filter(pk=pk).first()
    host_issue_all = issue.host_issue_set.filter(status="0")
    issue.status = "1"
    issue.save()
    # for h in host_issue_all:
    #     h.status = "1"
    #     h.save()
    # nginx_status = nginx_server(issue.team.nginxhost.all(), issue.team, host_issue_all, 1)
    # server_status = upstarem_server(host_issue_all, issue.team, issue.backup_path, issue.type)

    nginx_status = True
    server_status = True
    if nginx_status & server_status:
        host_issue_all.update(status="2")
        issue.status = "2"
        issue.save()

        return JsonResponse({"status": 0, "msg": "更新成功"})
    else:
        return JsonResponse({"status": 1, "msg": "更新失败"})


def rollback_server(host_list, team, t, type):
    host_data = [{"hostname": h.host.hostip, "ip": h.host.hostip, "port": h.host.ssh_port} for h in host_list]
    inventory = Inventory(host_data)  # 动态生成主机配置信息
    runner = AdHocRunner(inventory)
    tasks=[{"action": {"module": "shell", "args": "cp -rf  /backup/{}/{}  {}".format(t, team.name,team.path)}}]
    ret = runner.run(tasks)
    if not ret.results_raw["ok"]:
        return False
    return True


def rollback(request, pk):
    issue = Issue.objects.filter(pk=pk).first()
    host_issue_all = issue.host_issue_set.filter(Q(status="2") | Q(status="3"))
    # server_status = upstarem_server(host_issue_all, issue.team, issue.backup_path, issue.type)
    server_status=True
    if server_status:
        issue.status="6"
        issue.save()
        host_issue_all.update(status="6")
        return JsonResponse({"status": 0, "msg": "回滚成功"})
    else:
        return JsonResponse({"status": 1, "msg": "回滚失败"})
