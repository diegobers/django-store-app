from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, TemplateView, View, CreateView
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

        if self.request.user.is_anonymous:
            if self.request.session.session_key:
                return CartItem.objects.filter(cart__session_key=self.request.session.session_key)
        else:
            return redirect('store:view_cart') 

class AddToCartView(View):
    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        qty = int(request.POST.get('quantity', 1))
        product = Product.objects.get(id=product_id)

        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        
        if request.user.is_anonymous:
            if request.session.session_key:
                cart = Cart.objects.get(session_key=request.session.session_key)
            else:
                session_store = SessionStore()
                session_store.save()
                session_key = session_store.session_key
                
                request.session = session_store
                cart = Cart.objects.create(session_key=session_store.session_key) 
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, quantity=qty)
        cart_item.save()

        return redirect('store:view_cart')

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

class CheckoutView(TemplateView):
    template_name = 'checkout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = self.request.user.cart_items.all() if self.request.user.is_authenticated else []
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        context['cart_items'] = cart_items
        context['total_price'] = total_price
        context['shipping_form'] = ShippingForm()
        return context

    def post(self, request):
        shipping_form = ShippingForm(request.POST)

        if shipping_form.is_valid():
            cart_items = request.user.cart_items.all() if request.user.is_authenticated else []
            total_price = sum(item.product.price * item.quantity for item in cart_items)
            order = Order.objects.create(user=request.user if request.user.is_authenticated else None, total_amount=total_price)
            
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)

            request.user.cart_items.clear() if request.user.is_authenticated else Cart.objects.filter(session_key=request.session.session_key).delete()
            
            return redirect('store:order_confirmation')
        
        else:
            # Handle invalid forms
            return render(request, self.template_name, {'shipping_form': shipping_form})

class OrderConfirmationView(TemplateView):
    template_name = 'order_confirmation.html'