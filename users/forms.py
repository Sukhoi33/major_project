from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(max_length=150, required=True, label="Username")
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=30, required=True)
    surname = forms.CharField(max_length=30, required=True, label="Last name")
    nickname = forms.CharField(max_length=30, required=True)
    balance = forms.DecimalField(max_digits=10, decimal_places=2, required=False, initial=100.00)

    class Meta:

        model = User
        # include username so a separate username field appears in the form
        fields = ['username', 'email', 'password1', 'password2', 'first_name']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        # ensure email is unique (username is now separate)
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_nickname(self):
        nick = self.cleaned_data.get("nickname", "").strip()
        if not nick:
            raise forms.ValidationError("Nickname is required.")
        from .models import Profile
        if Profile.objects.filter(nickname__iexact=nick).exists():
            raise forms.ValidationError("This nickname is already taken.")
        return nick

    def save(self, commit=True):
        user = super().save(commit=False)
        username = self.cleaned_data['username'].strip()
        email = self.cleaned_data['email'].strip().lower()
        user.username = username           # use the provided username for login
        user.email = email
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['surname']
        user.balance = self.cleaned_data.get('balance', 100.00)

        if commit:
            user.save()
            # ensure profile & nickname
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.nickname = self.cleaned_data['nickname']
            profile.save(update_fields=['nickname'])
        return user


class AuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Email or Username",
        widget=forms.TextInput(attrs={"autofocus": True})
    )
    
    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip().lower()
        return username
    
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        # Additional checks can be added here if needed

class TopUpForm(forms.Form):
    amount = forms.DecimalField(min_value=0.01, decimal_places=2, max_digits=5, label="Amount to Top-Up",
    error_messages={
    'min_value': "Please enter an amount greater than $0.00.",
    'invalid': "Enter a valid amount in dollars and cents.",
})