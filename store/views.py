from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, TemplateView, View, CreateView
from django.shortcuts import get_object_or_404, redirect
from .models import Product, Cart, CartItem, Order, OrderItem
from .forms import ShippingForm


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
        
        if self.request.user.is_authenticated:
            cart_items = CartItem.objects.filter(cart__user=self.request.user)
        else:
            session_key = self.request.session.session_key
            cart_items = CartItem.objects.filter(cart__session_key=session_key)
        context['cart_items'] = cart_items
        
        return context

class AddToCartView(View):
    def post(self, request, pk):
        product = Product.objects.get(pk=pk)
        quantity = int(request.POST.get('quantity', 1))
        user = request.user
        session_key = request.session.session_key

        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
        else:
            cart, created = Cart.objects.get_or_create(session_key=session_key)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return redirect('store:index')

class RemoveFromCartView(View):
    def post(self, request):
        cart_item_id = request.POST.get('cart_item_id')
        CartItem.objects.filter(id=cart_item_id).delete()
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