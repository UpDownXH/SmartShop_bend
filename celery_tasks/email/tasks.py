from celery_tasks.main import celery_app
from django.core.mail import send_mail


@celery_app.task(name='send_email_active')
def send_email_active(email_addr,message):
    print('发送异步1')
    subject = '我是大标题'
    # message = 'hahhahhahahahhahahahahhahah您已经成功注册'
    from_email = 'updownxh@126.com'
    recipient_list = [email_addr]
    send_mail(subject=subject, message='', from_email=from_email, recipient_list=recipient_list, html_message=message)
    print('发送异步ok')