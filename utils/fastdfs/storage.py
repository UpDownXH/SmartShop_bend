from django.core.files.storage import Storage

from Django.settings import FDFS_BASE_URL


class FastDFSStorage(Storage):

    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content, max_length=None):
        pass

    def exists(self, name):
        # 返回false  表示文件不存在 可以上传
        return False

    def url(self, name):
        print("获取图片",name)
        # 返回图片的完整路径
        return FDFS_BASE_URL + name
