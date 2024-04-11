from django.urls import path
from . import views

app_name = 'store'


urlpatterns = [
  path('', views.StoreIndexView.as_view(), name='index'),
  path('carrinho/', views.CartView.as_view(), name='view_cart'),
  path('add-to-cart/<int:pk>/', views.AddToCartView.as_view(), name='add_cart'),
  #path('remove-from-cart/', RemoveFromCartView.as_view(), name='remove_from_cart'),
  #path('update-cart-item/', UpdateCartItemView.as_view(), name='update_cart_item'),
  path('checkout/', views.CheckoutView.as_view(), name='checkout_cart'),
  path('order_confirmation/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
]