from celery_tasks.main import celery_app
from utils.smsutils import SmsUtil


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, code):
    SmsUtil().send_message(mobile=mobile, code=code)