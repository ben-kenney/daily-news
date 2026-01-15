"""Views for the news app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SearchTerm, NewsDigest, UserProfile
from .forms import SearchTermForm, UserProfileForm

@login_required
def dashboard(request):
    """User dashboard showing recent digests and search terms."""
    digests = NewsDigest.objects.filter(user=request.user).order_by('-created_at')[:10]
    search_terms = SearchTerm.objects.filter(user=request.user)
    return render(request, 'news/dashboard.html', {
        'digests': digests,
        'search_terms': search_terms,
    })

@login_required
def add_search_term(request):
    """Add a new search term."""
    if request.method == 'POST':
        form = SearchTermForm(request.POST)
        if form.is_valid():
            term = form.save(commit=False)
            term.user = request.user
            try:
                term.save()
                messages.success(request, 'Search term added successfully.')
                return redirect('dashboard')
            except Exception:
                messages.error(request, 'This search term already exists.')
    else:
        form = SearchTermForm()
    return render(request, 'news/add_search_term.html', {'form': form})

@login_required
def delete_search_term(request, pk):
    """Delete a search term."""
    term = get_object_or_404(SearchTerm, pk=pk, user=request.user)
    if request.method == 'POST':
        term.delete()
        messages.success(request, 'Search term deleted.')
        return redirect('dashboard')
    return render(request, 'news/delete_search_term.html', {'term': term})

@login_required
def digest_detail(request, pk):
    """View details of a specific digest."""
    digest = get_object_or_404(NewsDigest, pk=pk, user=request.user)
    return render(request, 'news/digest_detail.html', {'digest': digest})

@login_required
def profile(request):
    """User profile settings."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'news/profile.html', {'form': form})
