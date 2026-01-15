"""Views for the news app."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SearchTerm, NewsDigest, UserProfile
from .forms import SearchTermForm, UserProfileForm
from .tasks import _generate_user_digest
import pytz
from datetime import datetime, timedelta

@login_required
def dashboard(request):
    """User dashboard showing recent digests and search terms."""
    digests = NewsDigest.objects.filter(user=request.user).order_by('-created_at')[:10]
    search_terms = SearchTerm.objects.filter(user=request.user)

    # Calculate time until next digest
    try:
        user_tz = pytz.timezone(request.user.userprofile.timezone)
        user_timezone_str = request.user.userprofile.timezone
    except UserProfile.DoesNotExist:
        user_tz = pytz.UTC
        user_timezone_str = 'UTC'

    now_utc = datetime.now(pytz.UTC)
    now_user = now_utc.astimezone(user_tz)
    next_digest = now_user.replace(hour=8, minute=0, second=0, microsecond=0)
    if now_user.hour >= 8:
        next_digest += timedelta(days=1)
    time_remaining = next_digest - now_user

    hours, remainder = divmod(int(time_remaining.total_seconds()), 3600)
    minutes = remainder // 60

    return render(request, 'news/dashboard.html', {
        'digests': digests,
        'search_terms': search_terms,
        'hours_until_next': hours,
        'minutes_until_next': minutes,
        'user_timezone': user_timezone_str,
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
                # Check if this is the first digest for the user
                if not NewsDigest.objects.filter(user=request.user).exists():
                    _generate_user_digest(request.user)
                    messages.info(request, 'Generating your first news digest...')
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
        initial = {}
        if hasattr(request, 'timezone') and request.timezone:
            initial['timezone'] = str(request.timezone)
        form = UserProfileForm(instance=profile, initial=initial)
    return render(request, 'news/profile.html', {'form': form})
