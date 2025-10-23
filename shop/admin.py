# shop/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Product, Order, OrderItem, Cart, CartItem, Payment

# -----------------
# 1. การจัดการ Order (แสดงรายละเอียด OrderItem ภายใน Order)
# -----------------
class OrderItemInline(admin.TabularInline):
    # แสดงรายการสินค้าที่สั่งซื้อในหน้ารายละเอียด Order
    model = OrderItem
    raw_id_fields = ['product'] 
    extra = 0
    # แสดงราคาต่อหน่วยและยอดรวมย่อย แต่ไม่อนุญาตให้แก้ไขในหน้านี้
    readonly_fields = ('price', 'subtotal',) 
    
    def subtotal(self, obj):
        # คำนวณยอดรวมย่อยของรายการ
        return f"฿{obj.subtotal():,.2f}"
    subtotal.short_description = 'ยอดรวมย่อย'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # list_display: แสดงข้อมูลในหน้าลิสต์ออเดอร์
    # ✅ [UPDATED] เพิ่ม tracking_number
    list_display = ('id', 'user', 'display_total_amount', 'status', 'tracking_number', 'created_at') 
    # list_filter: แถบกรองข้อมูล
    list_filter = ('status', 'created_at')
    # search_fields: ช่องค้นหา
    search_fields = ('user__username', 'shipping_address', 'id')
    # readonly_fields: ฟิลด์ที่แก้ไขไม่ได้ในหน้ารายละเอียด
    # ✅ [UPDATED] เปลี่ยน readonly_fields
    # **หมายเหตุ:** 'status' และ 'tracking_number' ไม่อยู่ในลิสต์นี้ จึงแก้ไขได้
    readonly_fields = ('user', 'total_amount', 'shipping_address', 'created_at', 'updated_at') 
    # fields ที่แสดงในหน้ารายละเอียด
    fieldsets = (
        ('ข้อมูลคำสั่งซื้อ', {
            'fields': ('user', 'total_amount', 'shipping_address', 'created_at', 'updated_at')
        }),
        ('การจัดการ', {
            # ฟิลด์เหล่านี้สามารถแก้ไขได้
            'fields': ('status', 'tracking_number') 
        }),
    )
    inlines = [OrderItemInline]
    
    # ฟังก์ชันช่วยแสดงผล
    def display_total_amount(self, obj):
        return f"฿{obj.total_amount:,.2f}"
    display_total_amount.short_description = 'ยอดรวม'


# -----------------
# 2. การจัดการ Product
# -----------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # ❌ [FIXED] เปลี่ยน 'display_price' กลับเป็น 'price' เพื่อให้ 'list_editable' ทำงานได้
    # เราจะใช้การแสดงผลแบบดิบของ Django Admin สำหรับฟิลด์ที่สามารถแก้ไขได้
    list_display = ('name', 'price', 'stock', 'is_active', 'is_in_stock', 'image_tag') 
    list_filter = ('is_active', 'created_at')
    # สามารถแก้ไขราคากับสต็อกได้จากหน้าลิสต์
    list_editable = ('price', 'stock', 'is_active') 
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'

    # ❌ [REMOVED] ลบ display_price ออก เพราะเราใช้ price ใน list_display แล้ว
    # def display_price(self, obj):
    #     return f"฿{obj.price:,.2f}"
    # display_price.short_description = 'ราคา'

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 5px;" />'.format(obj.image.url))
        return "No Image"
    image_tag.short_description = 'รูปภาพ'
    image_tag.admin_order_field = 'image'


# -----------------
# 3. การจัดการ Cart, CartItem, Payment
# -----------------
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    # ✅ [UPDATED] ใช้ @property จาก models.py
    list_display = ('user', 'total_cart_price', 'total_items_in_cart', 'created_at') 
    search_fields = ('user__username',)
    readonly_fields = ('total_cart_price', 'total_items_in_cart')

    def total_cart_price(self, obj):
        return f"฿{obj.total_price:,.2f}"
    total_cart_price.short_description = 'ราคารวมในตะกร้า'
    
    def total_items_in_cart(self, obj): 
        return obj.total_items
    total_items_in_cart.short_description = 'จำนวนชิ้นสินค้า'
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'display_subtotal')
    list_filter = ('product',)
    list_editable = ('quantity',)
    raw_id_fields = ('cart', 'product') 
    
    def display_subtotal(self, obj):
        # ใช้ obj.subtotal() จาก models.py
        return f"฿{obj.subtotal():,.2f}"
    display_subtotal.short_description = 'ยอดรวมย่อย'
    
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # ✅ [UPDATED] เพิ่ม order_link และ paid_at
    list_display = ('order_link', 'transaction_id', 'amount_paid', 'is_successful', 'payment_method', 'paid_at')
    list_filter = ('is_successful', 'payment_method', 'paid_at')
    search_fields = ('transaction_id', 'order__id')
    readonly_fields = ('order', 'transaction_id', 'amount_paid', 'paid_at')
    
    # ลิงก์ไปยังหน้ารายละเอียด Order ใน Django Admin
    def order_link(self, obj):
        if obj.order:
            link = f'/admin/shop/order/{obj.order.id}/'
            return format_html('<a href="{}">Order #{}</a>', link, obj.order.id)
        return 'N/A'
    order_link.short_description = 'Order ID'