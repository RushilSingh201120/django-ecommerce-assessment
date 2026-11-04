
from django.urls import path

from . import views


urlpatterns = [
    # Home and authentication
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboards
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('vendor/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/reviews/', views.vendor_reviews, name='vendor_reviews'),

    # Store management
    path('stores/', views.view_stores, name='view_stores'),
    path('stores/create/', views.create_store, name='create_store'),
    path(
        'stores/<int:store_id>/edit/',
        views.edit_store,
        name='edit_store'
    ),
    path(
        'stores/<int:store_id>/delete/',
        views.delete_store,
        name='delete_store'
    ),

    # Vendor product management
    path(
        'stores/<int:store_id>/products/',
        views.view_products,
        name='view_products'
    ),
    path(
        'stores/<int:store_id>/products/create/',
        views.create_product,
        name='create_product'
    ),
    path(
        'products/<int:product_id>/edit/',
        views.edit_product,
        name='edit_product'
    ),
    path(
        'products/<int:product_id>/delete/',
        views.delete_product,
        name='delete_product'
    ),

    # Buyer product browsing
    path('products/', views.browse_products, name='browse_products'),
    path(
        'products/search/',
        views.search_products,
        name='search_products'
    ),
    path(
        'products/<int:product_id>/',
        views.product_detail,
        name='product_detail'
    ),
    path(
        'products/<int:product_id>/review/',
        views.submit_review,
        name='submit_review'
    ),

    # Shopping cart
    path(
        'products/<int:product_id>/add-to-cart/',
        views.add_to_cart,
        name='add_to_cart'
    ),
    path('cart/', views.view_cart, name='view_cart'),
    path(
        'cart/update/<int:item_id>/',
        views.update_cart,
        name='update_cart'
    ),
    path(
        'cart/remove/<int:item_id>/',
        views.remove_from_cart,
        name='remove_from_cart'
    ),

    # Checkout and orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.order_list, name='order_list'),
    path(
        'orders/<int:order_id>/',
        views.order_detail,
        name='order_detail'
    ),

    # REST API
    path('api/stores/', views.api_stores, name='api_stores'),
    path(
        'api/stores/<int:store_id>/products/',
        views.api_store_products,
        name='api_store_products'
    ),
    path('api/reviews/', views.api_reviews, name='api_reviews'),
    
    path('reddit/', views.reddit_feed, name='reddit_feed'),
]