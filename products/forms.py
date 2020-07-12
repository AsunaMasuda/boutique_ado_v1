from django import forms
from .widgets import CustomClearableFileInput
from .models import Product, Category


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        # dunder or double underscore string, which will include all the fields.
        fields = '__all__'

    image = forms.ImageField(label='image', required=False, widget=CustomClearableFileInput)

    # overwrite init method
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.all()
        friendly_names = [(c.id, c.get_friendly_name()) for c in categories]
        # that we have the friendly names, let's update the category field on the form
        # To use those for choices instead of using the id.
        self.fields['category'].choices = friendly_names
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'border-black rounded-0'