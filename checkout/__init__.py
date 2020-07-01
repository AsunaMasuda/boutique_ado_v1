# Without this line in the innit file, django wouldn't know about our
# custom ready method so our signals wouldn't work. (app.py)
default_app_config = 'checkout.apps.CheckoutConfig'