# shop/urls.py

from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'shop' 

urlpatterns = [
    # ----------------------------------------------------------------------
    # 1. CUSTOMER FLOW
    # ----------------------------------------------------------------------
    path('', views.index, name='index'), 
    path('search/', views.search_results, name='search_results'), 
    path('product/<int:pk>/', views.product_detail, name='product_detail'), 

    # ----------------------------------------------------------------------
    # 2. CART & CHECKOUT FLOW
    # ----------------------------------------------------------------------
    path('cart/', views.view_cart, name='view_cart'), 
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'), 
    path('cart/update_quantity/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('checkout/', views.checkout, name='checkout'), 
    path('payment_process/<int:order_id>/', views.payment_process, name='payment_process'), 
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order/<int:pk>/', views.order_detail, name='order_detail'),

    # ----------------------------------------------------------------------
    # 3. AUTHENTICATION
    # ----------------------------------------------------------------------
    path('register/', views.register, name='register'), 
    
    # ✅ Login: 
    path('login/', auth_views.LoginView.as_view(
        template_name='shop/login.html',
        next_page='shop:custom_login_redirect'
    ), name='login'), 
    
    # 🟢 Custom Redirect Handler: 
    path('login/redirect/', views.custom_login_redirect, name='custom_login_redirect'),
    
    # 🔴 Logout: 
    path('logout/', auth_views.LogoutView.as_view(
        # ชี้ next_page ไปที่ 'shop:logout_done'
        next_page='shop:logout_done'
    ), name='logout'),

    # ✅ Logout Done: **[แก้ไข/รวม]** มีเพียง URL เดียวสำหรับแสดงหน้าออกจากระบบสำเร็จ
    path('logout-done/', views.logout_done_page, name='logout_done'),
    
    path('profile/', views.profile, name='profile'),
    
    # ✅ Password Change:
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='shop/password_change_form.html',
        success_url='/profile/password_change/done/' 
    ), name='password_change'),
    
    path('profile/password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='shop/password_change_done.html'
    ), name='password_change_done'),

    # ----------------------------------------------------------------------
    # 4. ADMIN FLOW
    # ----------------------------------------------------------------------
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    path('manage/products/', views.manage_products, name='manage_products'),
    path('manage/product/add/', views.add_product, name='add_product'),
    path('manage/product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('manage/product/delete/<int:pk>/', views.delete_product, name='delete_product'),
    
    path('manage/orders/', views.manage_orders, name='manage_orders'),
    path('manage/order/update_status/<int:pk>/', views.update_order_status, name='update_order_status'), 
]