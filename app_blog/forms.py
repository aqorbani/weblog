from django.forms import ModelForm
from django.forms import Textarea
from .models import Contactus


class ContactForm(ModelForm):
    class Meta:
        model = Contactus
        fields = ["name", "phone", "email", "message"]
        widgets = {
            "message": Textarea(
                attrs={
                    "placeholder": "Would love to talk about Blog?"
                }
            )
        }
