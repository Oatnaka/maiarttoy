# shop/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.db.models import Sum, F 
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.db.models import Q 
from django.db import transaction 
from django.core.paginator import Paginator, EmptyPage
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.http import require_POST 
from django.contrib.auth import views as auth_views 
from django import forms # ต้อง import forms เพื่อใช้ ModelForm 

from .models import Product, Cart, CartItem, Order, OrderItem, Payment
from .forms import UserProfileForm 

# ----------------------------------------------------------------------
# 💡 ฟอร์มชั่วคราวสำหรับจัดการสินค้า (เนื่องจาก forms.py ของคุณไม่มี ProductForm)
# ----------------------------------------------------------------------
class ProductForm(forms.ModelForm):
    """ฟอร์มสำหรับเพิ่ม/แก้ไขสินค้า"""
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

# ----------------------------------------------------------------------
# 1. AUTHENTICATION & PROFILE
# ----------------------------------------------------------------------

def custom_login_redirect(request):
    """
    ตรวจสอบสิทธิ์ผู้ใช้หลังล็อกอินสำเร็จ และเปลี่ยนเส้นทาง
    - Staff/Admin ไปที่ /admin/
    - Customer/ผู้ใช้ทั่วไป ไปที่ /profile/
    """
    if request.user.is_authenticated:
        if request.user.is_staff:
            # 🔥 ผู้ใช้ที่เป็น Admin ไปที่ Django Admin Site ทันที
            return redirect('/admin/')
        else:
            # ผู้ใช้ทั่วไปไปที่หน้า Profile
            return redirect('shop:profile')
    
    return redirect('shop:index') # กรณีฉุกเฉินกลับไปหน้าหลัก

def register(request):
    """ลงทะเบียนผู้ใช้ใหม่"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # 💡 signal จะสร้าง Cart ให้ user อัตโนมัติ
            messages.success(request, 'สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ')
            return redirect('shop:login')
        else:
            # แสดงข้อผิดพลาดที่เกิดขึ้น
            for field in form:
                for error in field.errors:
                    messages.error(request, f'{field.label}: {error}')
            for error in form.non_field_errors():
                messages.error(request, error)

    else:
        form = UserCreationForm()
    
    context = {
        'form': form
    }
    return render(request, 'shop/register.html', context)

@login_required
def profile(request):
    """แสดงและแก้ไขข้อมูลโปรไฟล์ผู้ใช้"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'แก้ไขข้อมูลโปรไฟล์สำเร็จ')
            return redirect('shop:profile')
    else:
        form = UserProfileForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'shop/profile.html', context)

# View สำหรับหน้าออกจากระบบสำเร็จ
def logout_done_page(request):
    return render(request, 'shop/logout.html') 


# ----------------------------------------------------------------------
# 2. CUSTOMER FLOW (INDEX, SEARCH, PRODUCT DETAIL)
# ----------------------------------------------------------------------

def index(request):
    """แสดงรายการสินค้าทั้งหมด"""
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(products, 12) # 12 สินค้าต่อหน้า
    page_number = request.GET.get('page')
    
    # ✅ FIX: ป้องกัน ValueError เมื่อ page_number เป็นสตริงว่างเปล่า
    if page_number == '':
        page_number = 1 
    
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'shop/index.html', context)

def search_results(request):
    """แสดงผลการค้นหาสินค้า"""
    query = request.GET.get('q')
    products = Product.objects.filter(is_active=True)
    
    if query:
        # ค้นหาจากชื่อสินค้าหรือคำอธิบายสินค้า
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()

    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    
    # ✅ FIX: ป้องกัน ValueError เมื่อ page_number เป็นสตริงว่างเปล่า
    if page_number == '':
        page_number = 1 
    
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
    }
    return render(request, 'shop/search_results.html', context)

def product_detail(request, pk):
    """แสดงรายละเอียดสินค้า"""
    product = get_object_or_404(Product, pk=pk, is_active=True)
    
    context = {
        'product': product,
    }
    return render(request, 'shop/product_detail.html', context)

# ----------------------------------------------------------------------
# 3. CART FLOW
# ----------------------------------------------------------------------

@login_required
def view_cart(request):
    """แสดงตะกร้าสินค้า"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all().select_related('product')
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/view_cart.html', context)

@login_required
@require_POST
def add_to_cart(request, product_id):
    """เพิ่มสินค้าลงในตะกร้า"""
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    cart = get_object_or_404(Cart, user=request.user)
    quantity = 1 # เพิ่มทีละ 1 ชิ้น
    
    if product.stock < quantity:
        messages.error(request, f'สินค้า "{product.name}" มีสต็อกไม่เพียงพอ')
        return redirect('shop:product_detail', pk=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )

    if not created:
        # ถ้ามีอยู่แล้วให้เพิ่มจำนวน
        new_quantity = cart_item.quantity + quantity
        # ตรวจสอบสต็อกอีกครั้ง
        if product.stock >= new_quantity:
            cart_item.quantity = new_quantity
            cart_item.save()
            messages.success(request, f'เพิ่ม "{product.name}" ลงในตะกร้าแล้ว ({new_quantity} ชิ้น)')
        else:
            messages.error(request, f'ไม่สามารถเพิ่ม "{product.name}" ได้ สต็อกมีเพียง {product.stock} ชิ้น')
    else:
        messages.success(request, f'เพิ่ม "{product.name}" ลงในตะกร้าแล้ว')
    
    return redirect('shop:view_cart')

@login_required
def remove_from_cart(request, item_id):
    """ลบรายการสินค้าออกจากตะกร้า"""
    if request.method not in ['POST', 'GET']:
        messages.error(request, 'คำขอไม่ถูกต้อง')
        return redirect('shop:view_cart')
    
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    product_name = cart_item.product.name
    
    cart_item.delete()
    messages.warning(request, f'ลบ "{product_name}" ออกจากตะกร้าแล้ว')
    return redirect('shop:view_cart')

@login_required
@require_POST
def update_cart_quantity(request, product_id):
    """อัปเดตจำนวนสินค้าในตะกร้า (สำหรับ AJAX)"""
    new_quantity = request.POST.get('quantity')
    
    try:
        new_quantity = int(new_quantity)
        if new_quantity <= 0:
            return JsonResponse({'success': False, 'message': 'จำนวนสินค้าต้องมากกว่า 0'}, status=400)
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'message': 'จำนวนสินค้าไม่ถูกต้อง'}, status=400)

    try:
        cart = Cart.objects.get(user=request.user)
        product = Product.objects.get(pk=product_id)
        cart_item = CartItem.objects.get(cart=cart, product=product)

        if new_quantity > product.stock:
            return JsonResponse({'success': False, 'message': f'สต็อกมีเพียง {product.stock} ชิ้น'}, status=400)
        
        cart_item.quantity = new_quantity
        cart_item.save()
        
        subtotal = float(cart_item.subtotal())
        total_price = float(cart.total_price)

        return JsonResponse({
            'success': True, 
            'subtotal': f'{subtotal:,.2f}',
            'total_price': f'{total_price:,.2f}',
            'total_items': cart.total_items
        })

    except (Cart.DoesNotExist, Product.DoesNotExist, CartItem.DoesNotExist):
        return JsonResponse({'success': False, 'message': 'รายการสินค้าในตะกร้าไม่พบ'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

# ----------------------------------------------------------------------
# 4. CHECKOUT & ORDER FLOW
# ----------------------------------------------------------------------

@login_required
def checkout(request):
    """หน้าสำหรับดำเนินการสั่งซื้อ"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all().select_related('product')

    if not cart_items:
        messages.warning(request, 'ตะกร้าสินค้าว่างเปล่า ไม่สามารถดำเนินการสั่งซื้อได้')
        return redirect('shop:index')

    if request.method == 'POST':
        # ในโปรเจกต์จริงควรมีฟอร์มสำหรับที่อยู่จัดส่ง
        # 💡 กระบวนการสร้าง Order:
        try:
            with transaction.atomic():
                # 1. สร้าง Order
                order = Order.objects.create(
                    user=request.user,
                    total_amount=cart.total_price,
                    # status เป็น PENDING (รอการชำระเงิน)
                    # จำลองข้อมูลที่อยู่จัดส่ง
                    shipping_address="123 ถนนตัวอย่าง, เขตสมมติ, จังหวัดสมมติ, 10000"
                )

                # 2. ย้าย CartItem ไปเป็น OrderItem
                for item in cart_items:
                    if item.product.stock < item.quantity:
                        # Rollback ทั้งหมดหากสต็อกไม่พอ
                        messages.error(request, f'สินค้า "{item.product.name}" มีสต็อกไม่เพียงพอ ({item.product.stock} ชิ้น)')
                        raise Exception("Insufficient stock")

                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        price=item.product.price, # ใช้ราคาปัจจุบันของสินค้า
                        quantity=item.quantity
                    )

                # 3. ลบสินค้าออกจาก Cart
                cart_items.delete()
                
                messages.success(request, f'สร้างคำสั่งซื้อ #{order.id} สำเร็จ! กรุณาชำระเงิน')
                return redirect('shop:payment_process', order_id=order.id)

        except Exception as e:
            # ข้อผิดพลาดอื่นๆ เช่น สต็อกไม่พอ
            print(f"Checkout Error: {e}")
            messages.error(request, 'เกิดข้อผิดพลาดในการสร้างคำสั่งซื้อ กรุณาลองใหม่อีกครั้ง')
            return redirect('shop:view_cart')

    context = {
        'cart': cart,
        'cart_items': cart_items,
        # ข้อมูลที่อยู่/ค่าจัดส่ง (ถ้ามี)
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def payment_process(request, order_id):
    """หน้าจำลองการชำระเงิน"""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    
    # ถ้า Order ถูกชำระเงินแล้ว ให้แสดงผลลัพธ์
    if order.status != 'PENDING' or Payment.objects.filter(order=order, is_successful=True).exists():
        messages.info(request, f'คำสั่งซื้อ #{order.id} ได้ชำระเงินแล้วและอยู่ในสถานะ "{order.get_status_display()}"')
        return redirect('shop:order_detail', pk=order.id)

    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'payment_method': 'Simulated QR/Transfer',
            'amount_paid': order.total_amount,
        }
    )

    if request.method == 'POST':
        # 💡 กระบวนการจำลองการยืนยันชำระเงิน
        if not payment.is_successful:
            # อัปเดต Payment และ Order
            payment.is_successful = True
            payment.save()

            order.status = 'CONFIRMED' # เปลี่ยนสถานะเป็น CONFIRMED 
            order.save()
            
            # 💡 Signal จะทำงานที่นี่เพื่อตัดสต็อก
            messages.success(request, f'การชำระเงินสำหรับคำสั่งซื้อ #{order.id} สำเร็จแล้ว! คำสั่งซื้อถูกยืนยันแล้ว')
            return redirect('shop:order_detail', pk=order.id)
        else:
            messages.info(request, f'คำสั่งซื้อ #{order.id} ได้ชำระเงินเรียบร้อยแล้ว')
            return redirect('shop:order_detail', pk=order.id)


    context = {
        'order': order,
        'payment': payment,
    }
    return render(request, 'shop/payment_process.html', context)


@login_required
def my_orders(request):
    """แสดงรายการคำสั่งซื้อทั้งหมดของผู้ใช้งาน"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'shop/my_orders.html', context)


@login_required
def order_detail(request, pk):
    """แสดงรายละเอียดคำสั่งซื้อ"""
    # จำกัดให้ผู้ใช้ดูได้เฉพาะออเดอร์ของตัวเองเท่านั้น
    order = get_object_or_404(Order, pk=pk, user=request.user)
    
    context = {
        'order': order,
        'order_items': order.items.all().select_related('product'),
    }
    return render(request, 'shop/order_detail.html', context)


# ----------------------------------------------------------------------
# 5. ADMIN MANAGEMENT VIEWS 
# ----------------------------------------------------------------------

@login_required
@user_passes_test(lambda user: user.is_staff)
def admin_dashboard(request: HttpRequest) -> HttpResponse:
    """
    หน้าแดชบอร์ดสำหรับผู้ดูแลระบบ (Admin Dashboard)
    """
    # ดึงข้อมูลสรุปสำหรับ Dashboard
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='CONFIRMED').count() # รอการจัดส่ง
    
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]

    context = {
        'total_products': total_products, 
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
    }
    return render(request, 'shop/admin_dashboard.html', context) 


@login_required
@user_passes_test(lambda user: user.is_staff)
def manage_products(request):
    """หน้าจัดการรายการสินค้าทั้งหมด"""
    products = Product.objects.all().order_by('-created_at')
    
    context = {
        'products': products
    }
    return render(request, 'shop/manage_products.html', context)

@login_required
@user_passes_test(lambda user: user.is_staff)
def add_product(request):
    """เพิ่มสินค้าใหม่"""
    if request.method == 'POST':
        # ProductForm ถูกกำหนดไว้ชั่วคราวใน views.py ด้านบน
        form = ProductForm(request.POST, request.FILES) 
        if form.is_valid():
            form.save()
            messages.success(request, 'เพิ่มสินค้าใหม่สำเร็จแล้ว')
            return redirect('shop:manage_products')
    else:
        form = ProductForm()
        
    context = {
        'form': form,
        'action': 'Add'
    }
    return render(request, 'shop/product_form.html', context)

@login_required
@user_passes_test(lambda user: user.is_staff)
def edit_product(request, pk):
    """แก้ไขสินค้าที่มีอยู่"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        # ProductForm ถูกกำหนดไว้ชั่วคราวใน views.py ด้านบน
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'แก้ไขสินค้า "{product.name}" สำเร็จแล้ว')
            return redirect('shop:manage_products')
    else:
        form = ProductForm(instance=product)
        
    context = {
        'form': form,
        'action': 'Edit',
        'product': product
    }
    return render(request, 'shop/product_form.html', context)

@login_required
@user_passes_test(lambda user: user.is_staff)
def delete_product(request, pk):
    """ลบสินค้า"""
    product = get_object_or_404(Product, pk=pk)
    product_name = product.name
    
    if request.method == 'POST':
        # ในการใช้งานจริง ควรมีการยืนยันก่อนลบ (เช่น ใช้ Modal)
        product.delete()
        messages.warning(request, f'ลบสินค้า "{product_name}" ออกจากระบบแล้ว')
        return redirect('shop:manage_products')
        
    # หากเข้าถึงด้วย GET (ไม่ควรเกิดขึ้น)
    messages.error(request, 'คำขอไม่ถูกต้อง')
    return redirect('shop:manage_products')


@login_required
@user_passes_test(lambda user: user.is_staff)
def manage_orders(request):
    """หน้าจัดการรายการคำสั่งซื้อทั้งหมดสำหรับ Admin"""
    # ดึงออเดอร์ทั้งหมดและเรียงตามวันที่สร้างล่าสุด
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
    }
    return render(request, 'shop/manage_orders.html', context)


@login_required
@user_passes_test(lambda user: user.is_staff)
def update_order_status(request, pk):
    """อัปเดตสถานะคำสั่งซื้อ (สำหรับ Admin)"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        new_tracking_number = request.POST.get('tracking_number', '').strip()
        
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]

        if new_status and new_status in valid_statuses:
            with transaction.atomic():
                order.status = new_status
                
                if new_tracking_number and new_status == 'SHIPPED':
                    order.tracking_number = new_tracking_number
                
                order.save()
                messages.success(request, f'อัปเดตสถานะคำสั่งซื้อ #{order.id} เป็น "{order.get_status_display()}" สำเร็จแล้ว')
        else:
            messages.error(request, 'สถานะคำสั่งซื้อไม่ถูกต้อง')
            
    # ไม่ว่าจะสำเร็จหรือไม่ ให้ redirect กลับไปที่หน้าจัดการออเดอร์
    return redirect('shop:manage_orders')
