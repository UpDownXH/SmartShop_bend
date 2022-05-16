from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
#
from apps.goods.models import SKUImage, SKU
from apps.smartshop_admin.serializers.image_serializers import SKUImageSerializer, SKUSerializer
from apps.smartshop_admin.utils import PageNum
#
#
class SKUImageView(ModelViewSet):
    # 查询集
    queryset = SKUImage.objects.all()
    # 序列化器
    serializer_class = SKUImageSerializer
    # 直接使用之前写好的分页类
    pagination_class = PageNum

    def create(self, request, *args, **kwargs):
        # - 1 接收参数 校验
        sku_id = request.data.get('sku')
        image = request.FILES.get('image')

        # - 2 把图片上传到fastdfs里 返回一个图片地址
        from fdfs_client.client import Fdfs_client
        # 创建FastDFS连接对象
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 上传
        result = client.upload_by_buffer(image.read())
        # {'Group name': 'group1',
        # 'Remote file_id': 'group1/M00/00/02/wKgxgGI9DnWAcUSrAAFtALQzeT4382.jpg',
        # 'Status': 'Upload successed.',
        # 'Local file name': '/home/lon/Desktop/222.jpg',
        # 'Uploaded size': '91.00KB',
        # 'Storage IP': '192.168.49.128'}

        if result.get("Status") != 'Upload successed.':
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 取出在fastdfs里的地址  把这个地址 保存到数据库
        file_id = result.get("Remote file_id")
        print("file_id", file_id)

        # - 3 把图片的地址和sku_id一切用模型类SKUImage保存到数据库
        SKUImage.objects.create(sku_id=sku_id, image=file_id)

        # - 4 返回响应
        return Response(status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        # - 1 接收参数 校验
        sku_id = request.data.get('sku')
        image = request.FILES.get('image')
        # 获取要修改的模型类对象的id
        pk = kwargs.get('pk')
        print("kwargs", kwargs)

        # - 2 把图片上传到fastdfs里 返回一个图片地址
        from fdfs_client.client import Fdfs_client
        # 创建FastDFS连接对象
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 上传
        result = client.upload_by_buffer(image.read())
        if result.get("Status") != 'Upload successed.':
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 取出在fastdfs里的地址  把这个地址 保存到数据库
        file_id = result.get("Remote file_id")
        print("file_id", file_id)

        # 获取要修改的丢下
        sku_image = SKUImage.objects.get(id=pk)
        # 把图片的地址补充上
        sku_image.image = file_id
        #保存数据
        sku_image.save()

        # - 4 返回响应
        return Response(status=status.HTTP_201_CREATED)


    # 删除方法
    # def destroy(self, request, *args, **kwargs):
        # 获取要删除对象的id
        # 查询要删除的对象
        # 对象.image
        #
        # 从fastdfs里删除
        # from fdfs_client.client import Fdfs_client
        # # 创建FastDFS连接对象
        # client = Fdfs_client('utils/fastdfs/client.conf')
        # client.delete_file()
        # 对象.delete()



# 所有ｓｋｕ数据
class SKUView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        data = SKU.objects.all()
        ser = SKUSerializer(data, many=True)
        return Response(ser.data)
