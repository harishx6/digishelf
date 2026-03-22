from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Review, Member, GENRE_CHOICES # GENRE_CHOICES import pannu!
from .models import Member, GENRE_CHOICES # Member model and genres import pannikko
from django import forms # 👈 இந்த லைன் இல்லனா தான் "forms is not defined" எரர் வரும்!
from .models import Member, Review, LostAndFound # 👈 LostAndFound-ஐ import பண்ணிக்கோ
from .models import LostAndFound

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    phone_number = forms.CharField(
        max_length=10, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter mobile number'})
    )
    address = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter full address'})
    )
    
    # 👇 MACHA, IDHU DHAAN PUDHU DROPDOWN 👇
    favorite_genre = forms.ChoiceField(
        choices=GENRE_CHOICES,
        required=True,
        label="Favorite Book Category",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'address', 'favorite_genre']

    # UNIQUE CHECKS
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("⚠️ Username not available!")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("⚠️ Email already registered! Please login.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        # Note: Unnoda Member model field name 'phone_number' ah irukanum
        if Member.objects.filter(phone_number=phone).exists(): 
            raise forms.ValidationError("⚠️ Phone number already in use!")
        return phone

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control', 'placeholder': 'Rate 1-5'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review here...'})
        }

# library/forms.py

class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'phone_number', 'address', 'favorite_genre']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'favorite_genre': forms.Select(attrs={'class': 'form-select'}),
        }

# library/forms.py

class LostAndFoundForm(forms.ModelForm):
    class Meta:
        model = LostAndFound
        # status-a list-la irundhu thookitom!
        fields = ['item_name', 'description'] 
        widgets = {
            'item_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'E.g., Blue Water bottle'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Item details...?'}),
        }