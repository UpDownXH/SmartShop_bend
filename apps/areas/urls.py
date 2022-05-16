from django.urls import path

from apps.areas.views import AreasView, SubAreasView, AddressView,UpdateDestroyAddressView

urlpatterns = [
    # 获取所有的省份
    path('areas/', AreasView.as_view()),
    path('areas/<area_id>/', SubAreasView.as_view()),
    path('addresses/create/', AddressView.as_view()),
    path('addresses/', AddressView.as_view()),
    path('addresses/<address_id>/', UpdateDestroyAddressView.as_view()),

]
