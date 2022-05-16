from datetime import date

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User

# 日活用户
class UserDailyActiveCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取活跃用户总数
        count = User.objects.filter(last_login__gte=now_date).count()
        return Response({
            'count': count,
            'date': now_date
        })

# 日下单用户
class UserDailyOrderCountView(APIView):
    # permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        # now_date = date.today()
        # 获取当日下单用户数量  orders__create_time 订单创建时间
        # count = User.objects.filter(orderinfo__create_time__gte=now_date).count()
        # return Response({
        #     "count": count,
        #     "date": now_date
        # })
        # 需将前台搭建后再修改
        return Response({
            "count": 1,
            "date": "2022-04-25"
        })

# 月新增用户
from datetime import timedelta


class UserMonthCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        # 获取一个月前日期
        start_date = now_date - timedelta(days=30)
        # 创建空列表保存每天的用户量
        date_list = []

        for i in range(30):
            # 循环遍历获取当天日期
            index_date = start_date + timedelta(days=i)
            # 指定下一天日期
            cur_date = start_date + timedelta(days=i + 1)

            # 查询条件是大于当前日期index_date，小于明天日期的用户cur_date，得到当天用户量
            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=cur_date).count()

            date_list.append({
                'count': count,
                'date': index_date
            })

        return Response(date_list)

# 日新增用户
class UserDayCountView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()

        # 查询条件是大于当前日期index_date，小于明天日期的用户cur_date，得到当天用户量
        count = User.objects.filter(date_joined__gte=now_date).count()

        return Response({
            "count": count,
            "date": now_date
        })
