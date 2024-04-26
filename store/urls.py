from django.urls import path
from . import views

app_name = 'store'


urlpatterns = [
  path('', views.StoreIndexView.as_view(), name='index'),
  path('cart/', views.CartView.as_view(), name='view_cart'),
  path('add-to-cart/', views.AddToCartView.as_view(), name='add_cart'),
  #path('remove-from-cart/', RemoveFromCartView.as_view(), name='remove_from_cart'),
  #path('update-cart-item/', UpdateCartItemView.as_view(), name='update_cart_item'),
  path('cart_confirmation/', views.CartConfirmationView.as_view(), name='confirm_cart'),
  path('order_confirmation/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
  path('order_list/', views.OrderListView.as_view(), name='order_list'),
]