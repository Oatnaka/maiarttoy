from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    # 💡 ต้องเพิ่มเมธอด ready() เพื่อโหลด signals.py
    def ready(self):
        # นำเข้า Signals เมื่อ App พร้อมใช้งาน
        try:
            from . import signals  # noqa
        except ImportError:
            pass
