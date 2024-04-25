from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import LayerFolder
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)




class LayerFolderForm(forms.ModelForm):
    class Meta:
        model = LayerFolder
        fields = ['id']  # This will not actually render a field because we'll override it below

    layer_folder = forms.ModelChoiceField(
        queryset=LayerFolder.objects.none(),  # Default empty, set in __init__
        label="Select a folder",
        empty_label="Select..."
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user is not None:
            # Set the queryset for 'layer_folder' field, only showing LayerFolders owned by the user
            self.fields['layer_folder'].queryset = LayerFolder.objects.filter(user=user)