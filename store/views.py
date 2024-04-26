from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, TemplateView, CreateView
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Cart, CartItem, Order, OrderItem
from .forms import ShippingForm
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.base import SessionBase
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


class StoreIndexView(ListView):
    model = Product
    template_name = 'store/index.html'
    context_object_name = 'products'

class CartView(ListView):
    model = CartItem
    template_name = 'store/cart.html'
    context_object_name = 'cart_items'
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return CartItem.objects.filter(cart__user=self.request.user)

        elif self.request.user.is_anonymous:
            return CartItem.objects.filter(cart__session_key=self.request.session.session_key)

class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)

        # Check if the user is authenticated
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            # If user is anonymous, create a new session and cart
            if not request.session.session_key:
                request.session.create()
            cart, created = Cart.objects.get_or_create(session_key=request.session.session_key, user=None)
        
        # Add the item to the cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity += 1
        cart_item.save()

        return redirect('store:view_cart')


class CartConfirmationView(LoginRequiredMixin, TemplateView):
    template_name = 'store/cart_confirmation.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get the user's cart items
        cart_items = CartItem.objects.filter(cart__user=self.request.user)
        context['cart_items'] = cart_items
        # Calculate total price
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        context['total_price'] = total_price

        return context
    
    def post(self, request, *args, **kwargs):
        # Create order from items in the shopping cart
        cart_items = CartItem.objects.filter(cart__user=self.request.user)
        total_amount = 0
        order_items = []

        # Create the order
        order = Order.objects.create(
            user=self.request.user,
            total_amount=total_amount,
        )

        for cart_item in cart_items:
            # Create order item for each cart item
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity
            )
            total_amount += cart_item.product.price * cart_item.quantity
            order_items.append(order_item)

        order.items.set(order_items)

        # Clear the shopping cart after creating the orders
        cart_items.delete()
        
        # Clear the user cart
        cart_queryset = Cart.objects.filter(user=self.request.user)
        cart_queryset.delete()

        return redirect('store:order_confirmation') 

class CheckoutView(LoginRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        user = request.user
        items = CartItem.objects.filter(cart__user=user)
        total_price = sum(item.product.price * item.quantity for item in items)

        # Create Order
        order = Order.objects.create(user=user, total_amount=total_price)

        # Move cart items to order items
        for item in items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

        # Clear the cart
        CartItem.objects.filter(cart__user=user).delete()

        return redirect('store:order_confirmation')  

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'store/orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).all()

class OrderConfirmationView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'store/order.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve items in the shopping cart for the logged-in user
        order_items = OrderItem.objects.filter(order__user=self.request.user)
        print (order_items)
        print('/////////////////////////////////')
        context['order_items'] = order_items
        return context


    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).last()


class RemoveFromCartView(View):
    def post(self, request):
        cart_item_id = request.POST.get('cart_item_id')
        CartItem.objects.filter(id=cart_item_id).delete()
        return JsonResponse({'success': True}) 

class UpdateQuantityView(View):
    def post(self, request):
        cart_item_id = request.POST.get('cart_item_id')
        quantity = int(request.POST.get('quantity'))
        cart_item = CartItem.objects.get(id=cart_item_id)
        cart_item.quantity = quantity
        cart_item.save()
        return JsonResponse({'success': True})