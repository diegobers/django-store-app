from django import forms

class ShippingForm(forms.Form):
    address = forms.CharField(label='Address', max_length=100)
    city = forms.CharField(label='City', max_length=50)