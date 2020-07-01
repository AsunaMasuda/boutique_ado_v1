from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from bag.contexts import bag_contents

import stripe


def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        # put the form data into a dictionary.
        # I'm doing this manually in order to skip the save infobox
        # which doesn't have a field on the order model.
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'country': request.POST['country'],
            'postcode': request.POST['postcode'],
            'town_or_city': request.POST['town_or_city'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'county': request.POST['county'],
        }
        # instance of the form using the form data
        order_form = OrderForm(form_data)

        if order_form.is_valid():
            order = order_form.save()
            for item_id, item_data in bag.items():
                try:
                    # get product id
                    product = Product.objects.get(id=item_id)
                    # if the item does not have size
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        # if the item has sizes
                        for size, quantity in item_data['items_by_size'].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                # if the product was not found
                except Product.DoesNotExist:
                    messages.error(request, (
                        "One of the products in your bag wasn't found in our database. "
                        "Please call us for assistance!")
                    )
                    order.delete()
                    return redirect(reverse('view_bag'))

            # whether or not the user wanted to save their profile information to the session.
            # Save the info to the user's profile if all is well
            request.session['save_info'] = 'save-info' in request.POST
            # url at the end of this python code pass order number as argument
            return redirect(reverse('checkout_success', args=[order.order_number]))

        else: # if order_form is not valid
            messages.error(request, ('There was an error with your form. '
                                     'Please double check your information.'))
    else:
        bag = request.session.get('bag', {})
        # And if there's nothing in the bag just add a simple error message.
        # And redirect back to the products page.
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse('products'))

        # We can pass it the request and get the same dictionary here in the view.
        # I'll store that in a variable called current bag.
        # Making sure not to overwrite the bag variable that already exists
        current_bag = bag_contents(request)
        total = current_bag['grand_total']
        stripe_total = round(total * 100) # Since stripe will require the amount to charge as an integer.
        # set the secret key on stripe and create payment intent 
        # the payment intent is like a dictionary that came back from stripe with a whole bunch of keys.
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )
        order_form = OrderForm()

    # a convenient message here that alerts you if you forget to set your public key.
    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. Did you forget to set it in your environment?')

    # we just need to create an instance of our order form. Which will be empty for now.
    
    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    # In this view we'll want to first check whether the user wanted to save
    # their information by getting that from the session just like we get
    # the shopping bag.
    save_info = request.session.get('save_info')
    order = get_object_or_404(Order, order_number=order_number)

    # a success message letting the user know what their order number is.
    # And that will be sending an email to the email they put in the form.
    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    # delete the user shopping bag from the session since it'll no longer be needed for this session.
    if 'bag' in request.session:
        del request.session['bag']

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)