# shop/signals.py 

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, Cart
from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404 # 💡 เพิ่ม import

# 💡 Signal สำหรับสร้างตะกร้าสินค้า (Cart) ทันทีที่ User ถูกสร้าง
@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        try:
            Cart.objects.create(user=instance)
        except Exception as e:
            # ควรจัดการข้อผิดพลาดในการสร้างตะกร้าด้วย
            print(f"Error creating cart for user {instance.username}: {e}")


# 💡 Signal สำหรับจัดการสต็อกเมื่อ Order ถูกยืนยัน
@receiver(post_save, sender=Order)
def update_product_stock_on_order_confirm(sender, instance, created, **kwargs):
    # ตรวจสอบว่า status field มีการเปลี่ยนแปลงหรือไม่ (อ้างอิงจาก update_fields)
    # และทำงานเฉพาะเมื่อสถานะเปลี่ยนเป็น CONFIRMED หรือ SHIPPED
    
    # ⚠️ [IMPORTANT] เนื่องจากเราใช้ `transaction.atomic` ใน checkout/views 
    # เราจะให้ signal นี้ทำงานเมื่อสถานะเป็น CONFIRMED เท่านั้น เพื่อตัดสต็อก
    
    # post_save ถูกเรียกทั้งตอนสร้าง (created=True) และตอนอัปเดต (created=False)
    # เราต้องการให้ทำงานตอนอัปเดตสถานะเท่านั้น (created=False)
    if not created and instance.status == 'CONFIRMED':
        # ใช้ transaction.atomic เพื่อให้แน่ใจว่าการดำเนินการทั้งหมดสำเร็จ
        with transaction.atomic():
            # ดึงรายการสินค้าที่ถูกสั่งซื้อ (related_name='items' ใน OrderItem)
            for item in instance.items.all():
                try:
                    product = get_object_or_404(item.product) # ใช้ get_object_or_404 แทน
                    
                    # ตรวจสอบว่าสินค้ายังมีสต็อกพอหรือไม่
                    if product.stock >= item.quantity:
                        product.stock -= item.quantity
                        # อัปเดตเฉพาะ field 'stock' เพื่อประสิทธิภาพ
                        product.save(update_fields=['stock']) 
                        print(f"✅ Stock updated: {item.quantity} units of {product.name} deducted.")
                    else:
                        # กรณีที่สต็อกไม่พอ (ไม่ควรเกิดขึ้นหากมีการตรวจสอบใน views.checkout แล้ว)
                        print(f"⚠️ Warning: Product {product.name} (ID: {product.id}) has insufficient stock ({product.stock} available).")
                        # หากจำเป็น คุณอาจต้องเปลี่ยนสถานะ Order กลับเป็น CANCELLED หรือ HOLD 
                        # เช่น order.status = 'CANCELLED', order.save() 
                        
                except ObjectDoesNotExist:
                    print(f"Product not found (deleted) for OrderItem ID: {item.id}")
                except Exception as e:
                    print(f"Error updating stock for OrderItem ID: {item.id}: {e}")
