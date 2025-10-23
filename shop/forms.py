# shop/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User 
from .models import Product # ต้อง import Product มาใช้

# กำหนดสไตล์ Bootstrap สำหรับฟิลด์
BOOTSTRAP_CLASSES = 'form-control'  # ✅ เอา form-control-lg ออก
BOOTSTRAP_CLASSES_LG = 'form-control form-control-lg rounded-3'  # สำหรับหน้าอื่นที่ต้องการ large
TEXTAREA_CLASSES = 'form-control rounded-3'

# ----------------------------------------------------------------------
# 1. ฟอร์มสำหรับการจัดการสินค้า (สำหรับ Admin)
# ----------------------------------------------------------------------
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # ใช้ทุกฟิลด์ยกเว้น created_at
        fields = ['name', 'description', 'price', 'stock', 'image', 'is_active'] 
        # เพิ่ม widgets เพื่อให้มีสไตล์ที่ดีขึ้น
        widgets = {
            'name': forms.TextInput(attrs={'class': BOOTSTRAP_CLASSES_LG, 'placeholder': 'ชื่อสินค้า'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': TEXTAREA_CLASSES, 'placeholder': 'รายละเอียดสินค้า'}),
            'price': forms.NumberInput(attrs={'class': BOOTSTRAP_CLASSES_LG, 'placeholder': 'ราคา (บาท)', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': BOOTSTRAP_CLASSES_LG, 'placeholder': 'จำนวนสต็อก'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}), # File Input ใช้แค่ form-control ก็พอ
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
# ----------------------------------------------------------------------
# 2. ฟอร์มสำหรับการแก้ไขโปรไฟล์ (สำหรับผู้ใช้งานทั่วไป)
# ----------------------------------------------------------------------
class UserProfileForm(forms.ModelForm):
    """ฟอร์มสำหรับการแก้ไขชื่อและนามสกุลของผู้ใช้งาน"""
    
    first_name = forms.CharField(max_length=150, required=False, label='ชื่อ', widget=forms.TextInput(
        attrs={'class': BOOTSTRAP_CLASSES_LG, 'placeholder': 'ชื่อจริง'}
    ))
    last_name = forms.CharField(max_length=150, required=False, label='นามสกุล', widget=forms.TextInput(
        attrs={'class': BOOTSTRAP_CLASSES_LG, 'placeholder': 'นามสกุล'}
    ))

    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        
# ----------------------------------------------------------------------
# 3. ฟอร์มสำหรับการสมัครสมาชิก (Custom User Creation Form)
# ----------------------------------------------------------------------
class CustomUserCreationForm(UserCreationForm):
    """
    ปรับปรุง UserCreationForm เพื่อเพิ่ม Class CSS ของ Bootstrap
    เพื่อให้ฟิลด์ทั้งหมดแสดงผลเต็มความกว้างและสวยงามใน register.html
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # วนลูปเพื่อเพิ่ม Class CSS ให้กับทุกฟิลด์ในฟอร์ม
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.PasswordInput)):
                field.widget.attrs.update({
                    'class': BOOTSTRAP_CLASSES,  # ✅ ใช้ form-control ธรรมดา
                    'placeholder': field.label if field.label else field_name
                })
                
        # ปรับแก้ Label ตามภาพใน register.html
        self.fields['username'].label = 'Username'
        self.fields['password1'].label = 'Password'
        self.fields['password2'].label = 'Password confirmation'

# ----------------------------------------------------------------------
# 4. ฟอร์มสำหรับ Login (Custom Authentication Form)
# ----------------------------------------------------------------------
class CustomAuthenticationForm(AuthenticationForm):
    """
    ปรับปรุง AuthenticationForm เพื่อเพิ่ม Class CSS ของ Bootstrap
    เพื่อให้ฟิลด์แสดงผลสวยงามใน login.html
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ ตั้งค่า Class ให้กับฟิลด์ username และ password (ใช้ form-control ธรรมดา)
        self.fields['username'].widget.attrs.update({
            'class': BOOTSTRAP_CLASSES,
            'placeholder': 'ชื่อผู้ใช้งาน'
        })
        self.fields['password'].widget.attrs.update({
            'class': BOOTSTRAP_CLASSES,
            'placeholder': 'รหัสผ่าน'
        })
        # ปรับ Label ให้สั้นลงและตรงกับภาพ
        self.fields['username'].label = 'Username'
        self.fields['password'].label = 'Password'
