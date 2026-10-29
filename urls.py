from django.urls import path

from . import views

urlpatterns = [
    path("recommend-box/", views.recommend_box_view, name="recommend-box"),
    path("orders/", views.create_order_view, name="order-create"),
    path("orders/<int:order_id>/", views.order_detail_view, name="order-detail"),
]
