from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile,Address
from django import forms

class UserProfileAdminForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'
        widgets = {
            'profile_photo': forms.ClearableFileInput(attrs={'accept': 'image/*'})
        }

class UserProfileAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number','wallet', 'is_blocked')
    list_filter = ('is_blocked',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'phone_number','profile_photo','wallet')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('Blocking', {'fields': ('is_blocked',)}),
    )
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('username',)

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Address)



