from django.shortcuts import render, redirect, reverse
from django.contrib import messages

from .forms import OrderForm


def checkout(request):
    bag = request.session.get('bag', {})
    # And if there's nothing in the bag just add a simple error message.
    # And redirect back to the products page.
    if not bag:
        messages.error(request, "There's nothing in your bag at the moment")
        return redirect(reverse('products'))

    # we just need to create an instance of our order form. Which will be empty for now.
    order_form = OrderForm()
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': 'pk_test_51Gyo5CD2Nwq6kkPKsnZBP6SkxhIMQNneGiEbKVtqw35AKgcAxjqyGAmJpPK4101FNt1Z79J8AN5nDJ53l3qIxwwV00oiGvzMGG',
        'client_secret': 'test client secret',
    }

    return render(request, template, context)