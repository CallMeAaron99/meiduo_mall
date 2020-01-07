from django.core.files.storage import Storage


class FastDFSStorage(Storage):
    #  自定义存储类

    def _open(self, name, mode='rb'):
        """
        当要打开某个文件时就会来调用此方法
        :param name: 要打开的文件
        :param mode: 打开文件模式
        :return: 文件对象
        """
        pass

    def _save(self, name, content):
        """
        当要上传图片时就会来调用此方法
        :param name: 要上传的文件名
        :param content: 要上传文件的bytes类型
        :return: file_id
        """
        pass

    def exists(self, name):
        """
        当上传图片时就会来调用此方法判断图片是否存在,只有不存在才会上传
        :param name: 要上传的图片名
        :return: False: 文件不存在  True: 文件存在
        """
        pass

    def url(self, name):
        """
        当image.url就会来调用此方法以获取图片文件的完整路径
        :param name: file_id
        :return: 'http://127.0.0.1:8888/' + file_id
        """
        return 'http://image.meiduo.site:8888/' + name
