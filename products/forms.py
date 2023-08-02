from django import forms
from .models import Banner
from .models import Image

class BannerForm(forms.ModelForm):
    class Meta:
        model = Banner
        fields = ('title', 'image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['image'].widget.attrs.update({'class': 'form-control'}) 

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title.strip()=='':
            raise forms.ValidationError('Enter a title.') 
        return title      


