# shop/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User 
from .models import Product # ต้อง import Product มาใช้

# 1. ฟอร์มสำหรับการจัดการสินค้า (สำหรับ Admin)
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # ใช้ทุกฟิลด์ยกเว้น created_at
        fields = ['name', 'description', 'price', 'stock', 'image', 'is_active'] 
        # เพิ่ม widgets เพื่อให้มีสไตล์ที่ดีขึ้น
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

# 2. ฟอร์มสำหรับการแก้ไขโปรไฟล์ (สำหรับผู้ใช้งานทั่วไป)
class UserProfileForm(forms.ModelForm):
    """ฟอร์มสำหรับการแก้ไขชื่อและนามสกุลของผู้ใช้งาน"""
    
    first_name = forms.CharField(max_length=150, required=False, label='ชื่อ', widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg rounded-3', 'placeholder': 'ชื่อจริง'}
    ))
    last_name = forms.CharField(max_length=150, required=False, label='นามสกุล', widget=forms.TextInput(
        attrs={'class': 'form-control form-control-lg rounded-3', 'placeholder': 'นามสกุล'}
    ))

    class Meta:
        model = User
        fields = ['first_name', 'last_name']
