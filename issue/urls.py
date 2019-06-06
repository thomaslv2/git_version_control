"""issue URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from web.views import *
from web.user import *
from web.host import *
from web.cron import *
from web.comm import *
from web.init import *
from web.initlog import *
from web.project import *
from web.issue import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'login/$', login, name="login"),
    url(r'logout/$', logout_view, name="logout"),
    url(r'^createuser/$', create_user, name="createuser"),
    url(r'^edituser/(?P<pk>\d+)$', create_user, name="edituser"),
    url(r'^deluser/(\d+)$', del_user, name="deluser"),
    url(r'^userall/$', userall, name="userall"),
    url(r'^createhost/$', create_host, name="createhost"),
    url(r'^edithost/(?P<pk>\d+)$', create_host, name="edithost"),
    url(r'^delhost/(\d+)$', del_host, name="delhost"),
    url(r'^hostall/$', hostall, name="hostall"),
    url(r'^createcron/$', create_cron, name="createcron"),
    url(r'^editcron/(?P<pk>\d+)$', create_cron, name="editcron"),
    url(r'^delcron/(\d+)$', del_cron, name="delcron"),
    url(r'^cronall/$', cronall, name="cronall"),
    url(r'^createcomm/$', create_comm, name="createcomm"),
    url(r'^commall/$', commall, name="commall"),
    url(r'^createinit/$', create_init, name="createinit"),
    url(r'^editinit/(?P<pk>\d+)$', create_init, name="editinit"),
    url(r'^detailinit/(?P<pk>\d+)$', detail_init, name="detailinit"),
    url(r'^delinit/(\d+)$', del_init, name="delinit"),
    url(r'^initall/$', initall, name="initall"),
    url(r'^createlog/$', create_initlog, name="createlog"),
    url(r'^createproject/$', create_project, name="createproject"),
    url(r'^editproject/(?P<pk>\d+)$', create_project, name="editproject"),
    url(r'^detailproject/(?P<pk>\d+)$', detail_project, name="detailproject"),
    url(r'^delproject/(\d+)$', del_project, name="delproject"),
    url(r'^projectall/$', projectall, name="projectall"),
    url(r'^updateall/$', updateall, name="updateall"),
    url(r'^rollbackall/$', rollbackall, name="rollbackall"),
    url(r'^creategit/$', create_git, name="creategit"),
    url(r'^getbra/(?P<pk>\d+)$', check_bra, name='getbra'),
    url(r'^gettag/(?P<pk>\d+)$', get_tags, name='gettag'),
    url(r'^getcommit/(?P<pk>\d+)/(?P<bra>\w+)$', get_commit, name='getcommit'),
    url(r'^createfile/$', create_file, name="createfile"),
    url(r'^detailissue/(?P<pk>\d+)$', detail_issue, name="detailissue"),
    url(r'^update/(?P<pk>\d+)$', update, name="update"),
    url(r'^successfull/(?P<pk>\d+)$', successfull, name="successfull"),
    url(r'^again/(?P<pk>\d+)$', again_update, name="again"),
    url(r'^rollback/(?P<pk>\d+)$', rollback, name="rollback"),
]
