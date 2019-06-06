from git import Repo
from git import Git
import os


class Gitclass():
    def __init__(self, name, url):

        self.path = os.path.join("/update/git/", name)
        self.is_dir(url)

    def is_dir(self, url):
        """
        判断是否是git目录，如果不是则clone
        :param url:
        :return:
        """
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        path = os.path.join(self.path, ".git")
        if os.path.isdir(path):
            return True
        else:
            Repo.clone_from(url, self.path)

    def get_bra(self):
        """
        获取分支信息
        :return:
        """
        return  [str(bra).split("/")[1] for bra in Repo(self.path).remote().refs if str(bra)!="origin/HEAD"]

    def get_commit(self,bra):
        Repo(self.path).remote().pull()
        try:
            ab=Repo(self.path).active_branch # 如果通过tag更新则获取不到当前的分支信息
        except Exception as e:
            ab="master"
        Repo(self.path).index.reset(commit="origin/{}".format(ab),head=True) #强制回退至远程仓库的位置
        Git(self.path).checkout(bra) #即使本地没有分支信息，只要远程仓库有就可以
        return [{"id":c.hexsha,"message":c.message} for c in Repo(self.path).iter_commits()]

    def get_tag(self):
        """
        获取tag标签
        :return:
        """
        return [str(tag) for tag in Repo(self.path).tags]


    def update(self,bra,commit=None,type="bra"):
        """
        更新
        如果是tag更新的话 ，就不需要commit信息
        如果是分支更新的话，就需要分支+commit信息
        :param bra:
        :param commit:
        :param type:
        :return:
        """
        Git(self.path).checkout(bra)
        if type =="bra":
            Repo(self.path).index.reset(commit=commit,head=True)

