from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, TemplateView, View

from .models import Product, Cart, CartItem


class StoreIndexView(TemplateView):
    template_name = 'store/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context

class CartView(TemplateView):
    template_name = 'store/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session_key = self.request.session.session_key
        if self.request.user.is_authenticated:
            cart_items = CartItem.objects.filter(cart__user=self.request.user)
        else:
            cart_items = CartItem.objects.filter(cart__session_key=session_key)
        context['cart_items'] = cart_items
        
        return context

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        product = Product.objects.get(pk=product_id)
        session_key = request.session.session_key

        if request.user.is_authenticated:
            cart_item, _ = CartItem.objects.get_or_create(cart__user=request.user, product=product)
        else:
            cart_item, _ = CartItem.objects.get_or_create(cart__session_key=session_key, product=product)
        cart_item.quantity += quantity
        cart_item.save()
        
        return redirect('cart')

class AddToCartView(View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        product = Product.objects.get(pk=product_id)

        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            session_key = request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({'success': True})

class RemoveFromCartView(View):
    def post(self, request):
        cart_item_id = request.POST.get('cart_item_id')
        CartItem.objects.filter(id=cart_item_id).delete()
        return JsonResponse({'success': True})

