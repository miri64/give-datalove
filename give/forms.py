from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, \
        UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from give.models import *

class DataloveAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = kwargs.get('prefix','login')
        super(DataloveAuthenticationForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'login_input'

class DataloveUserChangeForm(UserChangeForm):
    def __init__(self, *args, **kwargs):
        super(DataloveUserChangeForm, self).__init__(*args,**kwargs)
        self.fields['username'].help_text = ''

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.instance.username.lower() != username.lower() and \
                len(User.objects.filter(username__iexact=username)) > 0:
            raise forms.ValidationError(
                    "A user with that username already exists."
                )
        return username

    class Meta(UserChangeForm.Meta):
        fields = ('username','email',)

class DataloveUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(DataloveUserCreationForm, self).__init__(*args,**kwargs)
        self.fields['username'].help_text = ''
        self.fields['username'].label += '*'
        self.fields['password1'].label += '*'
        self.fields['password2'].help_text = ''
        self.fields['password2'].label += '*'
    
    def clean_username(self):
        username = super(DataloveUserCreationForm, self).clean_username()
        if len(User.objects.filter(username__iexact=username)) > 0:
            raise forms.ValidationError(
                    self.error_messages['duplicate_username']
                )
        return username

    class Meta(UserCreationForm.Meta):
        fields = ('username','email',)

class BaseUserWebsiteFormSet(forms.models.BaseModelFormSet):
    def __init__(self, user, *args, **kwargs):
        super(BaseUserWebsiteFormSet, self).__init__(*args, **kwargs)
        self.user = user
        self.queryset = user.get_profile().websites.all()
        for form in self:
            form.fields['url'].widget.attrs['class'] = 'url_input'

    def save(self, *args, **kwargs):
        websites = super(BaseUserWebsiteFormSet,self).save(commit=False)
        for website in websites:
            if website.user_id == None:
                website.user = self.user.get_profile()
            website.save()

UserWebsiteFormSet = forms.models.modelformset_factory(
        UserWebsite,
        formset=BaseUserWebsiteFormSet,
        fields=('url',)
    )
