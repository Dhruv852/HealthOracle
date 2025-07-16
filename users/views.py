from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import PatientProfile
from HealthOracle.models import PredictionHistory

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Check if profile already exists before creating one
            if not hasattr(user, 'patientprofile'):
                PatientProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.patientprofile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.patientprofile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'profile': request.user.patientprofile
    }
    return render(request, 'users/profile.html', context)

@login_required
def patient_history(request):
    # Get the patient's prediction history
    prediction_history = PredictionHistory.objects.filter(user=request.user)
    print(f"Found {prediction_history.count()} predictions for user {request.user.username}")
    return render(request, 'users/history.html', {'prediction_history': prediction_history})