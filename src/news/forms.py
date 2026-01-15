"""Forms for the news app."""

from django import forms
from .models import SearchTerm, UserProfile

class SearchTermForm(forms.ModelForm):
    """Form for adding search terms."""
    class Meta:
        model = SearchTerm
        fields = ['term']

class UserProfileForm(forms.ModelForm):
    """Form for user profile."""
    class Meta:
        model = UserProfile
        fields = ['timezone']