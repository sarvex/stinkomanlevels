from django import forms

from main.models import *

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=50, widget=forms.widgets.PasswordInput())
    next_url = forms.CharField(max_length=256, widget=forms.HiddenInput)

class NewCommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'cols':'55','rows':'8'}))

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=24)
    email = forms.EmailField(max_length=32)
    password = forms.CharField(max_length=50, widget=forms.widgets.PasswordInput())
    confirm_password = forms.CharField(max_length=50, widget=forms.widgets.PasswordInput())
    
    def clean_confirm_password(self):
        password1 = self.cleaned_data['password']
        password2 = self.cleaned_data['confirm_password']
        if password1 != password2:
            raise forms.ValidationError("Your passwords do not match.")

        return password2

    def clean_username(self):
        username = self.cleaned_data['username']

        if User.objects.filter(username=username).count() > 0:
            raise forms.ValidationError("The user '%s' already exists." % username)

        return username
   
    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError("This email address already exists.")

        return email
   
class UploadLevelForm(forms.Form):
    STAGE_CHOICES = (
        ('Level 1: Go Home!', (
                ('1.1', 'Stage 1.1'),
                ('1.2', 'Stage 1.2'),
            ),
        ),
        ('Level 2: Pick a Bone!', (
                ('2.1', 'Stage 2.1'),
                ('2.2', 'Stage 2.2'),
            ),
        ),
        ('Level 3: Dumb Wall!', (
                ('3.3', 'Stage 3.3'),
            ),
        ),
        ('Level 4: Fisticuff!', (
                ('4.1', 'Stage 4.1'),
                ('4.2', 'Stage 4.2'),
                ('4.3', 'Stage 4.3'),
            ),
        ),
        ('Level 5: Oh, the Moon!', (
                ('5.1', 'Stage 5.1'),
                ('5.2', 'Stage 5.2'),
                ('5.3', 'Stage 5.3'),
            ),
        ),
        ('Level 6: Stratosfear!', (
                ('6.1', 'Stage 6.1'),
                ('6.2', 'Stage 6.2'),
                ('6.3', 'Stage 6.3'),
            ),
        ),
        ('Level 7: Ice 2 Meet U!', (
                ('7.1', 'Stage 7.1'),
                ('7.2', 'Stage 7.2'),
                ('7.3', 'Stage 7.3'),
            ),
        ),
        ('Level 8: Negatory!', (
                ('8.1', 'Stage 8.1'),
                ('8.2', 'Stage 8.2'),
                ('8.3', 'Stage 8.3'),
            ),
        ),
        ('Level 9: Turbolence!', (
                ('9.1', 'Stage 9.1'),
                ('9.2', 'Stage 9.2'),
                ('9.3', 'Stage 9.3'),
            ),
        ),
    )
    title = forms.CharField(max_length=32)
    stage = forms.ChoiceField(choices=STAGE_CHOICES)
    difficulty = forms.ChoiceField(choices=Level.DIFFICULTY_CHOICES)
    length = forms.ChoiceField(choices=Level.LENGTH_CHOICES)
    description = forms.CharField(required=False, max_length=2048, widget=forms.Textarea(attrs={'cols':'32','rows':'6'}))
    xml_code = forms.CharField(required=False, widget=forms.Textarea(attrs={'cols':'30', 'rows':'12'}))
    xml_file = forms.FileField(required=False)

    def clean_title(self):
        title = self.cleaned_data['title']

        if Level.objects.filter(title=title).count() > 0:
            raise forms.ValidationError("The level title '%s' already exists." % title)

        return title

    def clean_xml_file(self):
        xml_code = self.cleaned_data['xml_code']
        xml_file = self.cleaned_data['xml_file']

        if len(xml_code) == 0 and xml_file is None:
            raise forms.ValidationError("You must supply either xml pasted in the box or a file to upload.")

        return xml_file
