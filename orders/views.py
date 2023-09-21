from django.shortcuts import render

from cart.cart import Cart

from .forms import OrderCreationForm
from .models import OrderItem
from .tasks import order_created


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreationForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            # Запуск ассинхронного задания отпраки сообщения
            order_created.delay(order.id)
            return render(request,
                          'orders/order/created.html',
                          {'order': order})
    else:
        form = OrderCreationForm()
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})
