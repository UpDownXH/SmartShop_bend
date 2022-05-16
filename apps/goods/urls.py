from django.urls import path, re_path

from apps.goods.views import IndexView, ListView, HotGoodsView, MySearchView, DetailView, DetailVisitView, UserBrowseHistory
    # , HotGoodsView, MySearchView, DetailView, DetailVisitView

urlpatterns = [
    path('index/', IndexView.as_view()),
    # 列表页
    path('list/<category_id>/skus/', ListView.as_view()),
    # re_path('hot/(?P<category_id>\d+)/', ListView.as_view()),
    path('hot/<category_id>/', HotGoodsView.as_view()),
#     # 搜索页
    path('search/', MySearchView()),
#     # 商品详情页
    path('detail/<sku_id>/', DetailView.as_view()),
#     # 商品类型访问量
    path('detail/visit/<category_id>/', DetailVisitView.as_view()),
    path('browse_histories/', UserBrowseHistory.as_view()),

]