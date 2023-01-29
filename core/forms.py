from django import forms
from captcha.fields import ReCaptchaField


class SignUpForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur"}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': "E-mail"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': "Mot de passe"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': "Confirmer le mot de passe"}))
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
