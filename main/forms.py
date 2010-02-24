from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=50, widget=forms.widgets.PasswordInput())

class NewCommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'cols':'55','rows':'8'}))
    id = forms.IntegerField(widget=forms.HiddenInput)
