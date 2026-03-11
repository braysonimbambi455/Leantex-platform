from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import UserRegisterForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Authenticate the user first (this handles multiple backends properly)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            authenticated_user = authenticate(username=username, password=password)
            
            if authenticated_user is not None:
                # Login with the authenticated user
                login(request, authenticated_user)
                messages.success(request, f'Welcome to Leantex, {user.username}!')
                
                # Redirect based on role
                if hasattr(user, 'profile'):
                    if user.profile.role == 'admin':
                        return redirect('dashboard:admin')
                    elif user.profile.role == 'technician':
                        return redirect('dashboard:technician')
                return redirect('dashboard:customer')
            else:
                # If authentication fails, redirect to login page
                messages.success(request, 'Registration successful! Please log in.')
                return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                
                # Redirect based on role
                if hasattr(user, 'profile'):
                    if user.profile.role == 'admin':
                        return redirect('dashboard:admin')
                    elif user.profile.role == 'technician':
                        return redirect('dashboard:technician')
                    elif user.profile.role == 'customer':
                        return redirect('dashboard:customer')
                
                # Default fallback
                return redirect('dashboard:customer')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('index')

@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'user_role': request.user.profile.role if hasattr(request.user, 'profile') else 'customer'
    }
    return render(request, 'accounts/profile.html', context)

# Optional: Add a view for password change
@login_required
def change_password_view(request):
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})