# Generated by Django 2.2.5 on 2022-04-30 02:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OAuthWEIBOUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('access_token', models.CharField(db_index=True, max_length=64, verbose_name='access_token')),
            ],
            options={
                'verbose_name': '微博登录用户数据',
                'verbose_name_plural': '微博登录用户数据',
                'db_table': 'tb_oauth_weibo',
            },
        ),
    ]
