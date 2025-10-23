# shop/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F
import uuid

# ================== Product ==================
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="ชื่อสินค้า")
    description = models.TextField(verbose_name="คำอธิบาย")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคา")
    stock = models.IntegerField(verbose_name="สต็อก")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="รูปภาพสินค้า")
    is_active = models.BooleanField(default=True, verbose_name="สถานะสินค้า")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def is_in_stock(self):
        return self.stock > 0
    is_in_stock.boolean = True
    is_in_stock.short_description = 'มีสินค้า'

# ================== Cart ==================
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="ผู้ใช้งาน")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        total = self.cartitem_set.aggregate(sum_price=Sum(F('quantity') * F('product__price')))['sum_price']
        return total if total is not None else 0.00
    
    @property
    def total_items(self):
        total = self.cartitem_set.aggregate(total_qty=Sum('quantity'))['total_qty']
        return total if total is not None else 0

    def __str__(self):
        return f"Cart of {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name="ตะกร้าสินค้า")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="สินค้า")
    quantity = models.IntegerField(default=1, verbose_name="จำนวน")

    def subtotal(self):
        if self.product and self.product.price:
            return self.quantity * self.product.price
        return 0
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.user.username}"

# ================== Order ==================
class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'รอชำระเงิน'),
        ('CONFIRMED', 'ยืนยันแล้ว'), # ยืนยันเมื่อชำระเงินสำเร็จ
        ('SHIPPED', 'กำลังจัดส่ง'), # แอดมินเปลี่ยนสถานะและใส่ Tracking Number
        ('DELIVERED', 'จัดส่งสำเร็จ'),
        ('CANCELLED', 'ยกเลิก'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="ผู้ใช้งาน")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ยอดรวมคำสั่งซื้อ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="สถานะคำสั่งซื้อ")
    shipping_address = models.TextField(verbose_name="ที่อยู่จัดส่ง")
    tracking_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="หมายเลขติดตามพัสดุ") 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    # **[NEW]** Override save method to ensure updated_at is set properly on status change
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="คำสั่งซื้อ")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="สินค้า")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ราคาต่อหน่วยตอนสั่งซื้อ")
    quantity = models.IntegerField(verbose_name="จำนวน")

    def subtotal(self):
        # แก้ไขตรงนี้ - ตรวจสอบค่า None ก่อนคำนวณ
        if self.price is not None and self.quantity is not None:
            return self.quantity * self.price
        return 0
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Deleted Product'} in Order {self.order.id}"

# ================== Payment ==================
class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="คำสั่งซื้อ")
    payment_method = models.CharField(max_length=50, verbose_name="วิธีการชำระเงิน")
    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4, verbose_name="รหัสธุรกรรม")
    is_successful = models.BooleanField(default=False, verbose_name="สำเร็จหรือไม่")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ยอดเงินที่ชำระ", default=0.00)
    paid_at = models.DateTimeField(auto_now_add=True, verbose_name="วันเวลาที่ชำระ")

    def __str__(self):
        return f"Payment for Order {self.order.id} ({'Successful' if self.is_successful else 'Failed'})"

    # **[NEW]** Override save method to automatically update Order status when payment is successful
    def save(self, *args, **kwargs):
        # ตรวจสอบสถานะเดิมก่อน
        is_new = self.pk is None
        
        # ทำการบันทึก Payment
        super().save(*args, **kwargs)

        # หากเป็นการชำระเงินสำเร็จ และสถานะเดิมของ Order ไม่ได้ถูกยืนยันแล้ว
        if self.is_successful and self.order.status == 'PENDING':
            # อัปเดตสถานะของ Order ให้เป็น 'CONFIRMED'
            self.order.status = 'CONFIRMED'
            self.order.save(update_fields=['status', 'updated_at'])
            
            # **TODO: สามารถเพิ่ม Logic การลดสต็อกสินค้า (Product Stock) ที่นี่ได้**
            # (ต้องทำในส่วนของ Logic การสร้าง Order จาก Cart ด้วย เพื่อให้สต็อกถูกลดทันที)