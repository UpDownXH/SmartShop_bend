# celery启动文件
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django.settings')

# 1创建celery实例
celery_app = Celery('celery_tasks')
# 2加载celery配置
celery_app.config_from_object('celery_tasks.config')
# 3自动注册celery任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])