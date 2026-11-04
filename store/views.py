
import uuid

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm, RegistrationForm, StoreForm
from .models import Cart, CartItem, Order, OrderItem, Product, Review, Store
from .functions.reddit import get_reddit_posts


from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    StoreSerializer,
    ProductSerializer,
    ReviewSerializer,
)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            if user.profile.role == 'vendor':
                return redirect('vendor_dashboard')

            return redirect('buyer_dashboard')
    else:
        form = RegistrationForm()

    return render(
        request,
        'store/register.html',
        {'form': form}
    )


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            if user.profile.role == 'vendor':
                return redirect('vendor_dashboard')

            return redirect('buyer_dashboard')

        messages.error(
            request,
            'Invalid username or password.'
        )

    return render(
        request,
        'store/login.html'
    )


@login_required
def buyer_dashboard(request):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can access the buyer dashboard.'
        )
        return redirect('home')

    return render(
        request,
        'store/buyer_dashboard.html'
    )


@login_required
def vendor_dashboard(request):
    if request.user.profile.role != 'vendor':
        messages.error(
            request,
            'Only vendors can access the vendor dashboard.'
        )
        return redirect('home')

    stores = Store.objects.filter(
        vendor=request.user
    )

    return render(
        request,
        'store/vendor_dashboard.html',
        {'stores': stores}
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


def home(request):
    return render(
        request,
        'store/home.html'
    )


@login_required
def create_store(request):
    if request.user.profile.role != 'vendor':
        messages.error(
            request,
            'Only vendors can create stores.'
        )
        return redirect('home')

    if request.method == 'POST':
        form = StoreForm(request.POST)

        if form.is_valid():
            store = form.save(commit=False)
            store.vendor = request.user
            store.save()

            messages.success(
                request,
                'Store created successfully.'
            )

            return redirect('view_stores')
    else:
        form = StoreForm()

    return render(
        request,
        'store/create_store.html',
        {'form': form}
    )


@login_required
def view_stores(request):
    if request.user.profile.role == 'vendor':
        stores = Store.objects.filter(
            vendor=request.user
        )
    else:
        stores = Store.objects.all()

    return render(
        request,
        'store/view_stores.html',
        {'stores': stores}
    )


@login_required
def edit_store(request, store_id):
    if request.user.profile.role != 'vendor':
        messages.error(
            request,
            'Only vendors can edit stores.'
        )
        return redirect('home')

    store = get_object_or_404(
        Store,
        id=store_id,
        vendor=request.user
    )

    if request.method == 'POST':
        form = StoreForm(
            request.POST,
            instance=store
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Store updated successfully.'
            )

            return redirect('view_stores')
    else:
        form = StoreForm(
            instance=store
        )

    return render(
        request,
        'store/edit_store.html',
        {
            'form': form,
            'store': store
        }
    )


@login_required
def delete_store(request, store_id):
    if request.user.profile.role != 'vendor':
        messages.error(
            request,
            'Only vendors can delete stores.'
        )
        return redirect('home')

    store = get_object_or_404(
        Store,
        id=store_id,
        vendor=request.user
    )

    if request.method == 'POST':
        store.delete()

        messages.success(
            request,
            'Store deleted successfully.'
        )

        return redirect('view_stores')

    return render(
        request,
        'store/delete_store.html',
        {'store': store}
    )


@login_required
def create_product(request, store_id):
    if request.user.profile.role != 'vendor':
        messages.error(
            request,
            'Only vendors can create products.'
        )
        return redirect('home')

    store = get_object_or_404(
        Store,
        id=store_id,
        vendor=request.user
    )

    if request.method == 'POST':
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()

            messages.success(
                request,
                'Product created successfully.'
            )

            return redirect(
                'view_products',
                store_id=store.id
            )
    else:
        form = ProductForm()

    return render(
        request,
        'store/create_product.html',
        {
            'form': form,
            'store': store
        }
    )


@login_required
def view_products(request, store_id):
    store = get_object_or_404(
        Store,
        id=store_id
    )

    products = Product.objects.filter(
        store=store
    )

    return render(
        request,
        'store/view_products.html',
        {
            'store': store,
            'products': products
        }
    )


@login_required
def edit_product(request, product_id):
    if request.user.profile.role != 'vendor':
        messages.error(
            request,
            'Only vendors can edit products.'
        )
        return redirect('home')

    product = get_object_or_404(
        Product,
        id=product_id,
        store__vendor=request.user
    )

    if request.method == 'POST':
        form = ProductForm(
            request.POST,
            instance=product
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Product updated successfully.'
            )

            return redirect(
                'view_products',
                store_id=product.store.id
            )
    else:
        form = ProductForm(
            instance=product
        )

    return render(
        request,
        'store/edit_product.html',
        {
            'form': form,
            'product': product
        }
    )


@login_required
def delete_product(request, product_id):
    if request.user.profile.role != 'vendor':
        messages.error(
            request,
            'Only vendors can delete products.'
        )
        return redirect('home')

    product = get_object_or_404(
        Product,
        id=product_id,
        store__vendor=request.user
    )

    store_id = product.store.id

    if request.method == 'POST':
        product.delete()

        messages.success(
            request,
            'Product deleted successfully.'
        )

        return redirect(
            'view_products',
            store_id=store_id
        )

    return render(
        request,
        'store/delete_product.html',
        {'product': product}
    )


@login_required
def browse_products(request):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can browse products.'
        )
        return redirect('home')

    products = Product.objects.filter(
        stock__gt=0
    ).select_related('store')

    return render(
        request,
        'store/browse_products.html',
        {'products': products}
    )


@login_required
def search_products(request):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can search products.'
        )
        return redirect('home')

    query = request.GET.get(
        'q',
        ''
    ).strip()

    products = Product.objects.filter(
        stock__gt=0
    ).select_related('store')

    if query:
        products = products.filter(
            name__icontains=query
        )

    return render(
        request,
        'store/search_products.html',
        {
            'products': products,
            'query': query
        }
    )


@login_required
def product_detail(request, product_id):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can view product details.'
        )
        return redirect('home')

    product = get_object_or_404(
        Product,
        id=product_id
    )

    reviews = Review.objects.filter(
        product=product
    ).select_related('user').order_by('-created_at')

    return render(
        request,
        'store/product_detail.html',
        {
            'product': product,
            'reviews': reviews,
        }
    )

@login_required
def add_to_cart(request, product_id):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can add products to a cart.'
        )
        return redirect('home')

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if product.stock <= 0:
        messages.error(
            request,
            'This product is out of stock.'
        )
        return redirect(
            'product_detail',
            product_id=product.id
        )

    cart, created = Cart.objects.get_or_create(
        buyer=request.user
    )

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            messages.error(
                request,
                'You cannot add more than the available stock.'
            )
            return redirect('view_cart')

    messages.success(
        request,
        f'{product.name} added to your cart.'
    )

    return redirect('view_cart')


@login_required
def view_cart(request):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can view a cart.'
        )
        return redirect('home')

    cart, created = Cart.objects.get_or_create(
        buyer=request.user
    )

    items = cart.items.select_related(
        'product'
    )

    total = sum(
        item.product.price * item.quantity
        for item in items
    )

    return render(
        request,
        'store/view_cart.html',
        {
            'cart': cart,
            'items': items,
            'total': total
        }
    )


@login_required
def update_cart(request, item_id):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can update a cart.'
        )
        return redirect('home')

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__buyer=request.user
    )

    if request.method == 'POST':
        try:
            quantity = int(
                request.POST.get(
                    'quantity',
                    1
                )
            )
        except (TypeError, ValueError):
            quantity = 1

        if quantity < 1:
            messages.error(
                request,
                'Quantity must be at least 1.'
            )
            return redirect('view_cart')

        if quantity > item.product.stock:
            messages.error(
                request,
                'Quantity cannot exceed available stock.'
            )
            return redirect('view_cart')

        item.quantity = quantity
        item.save()

        messages.success(
            request,
            'Cart updated successfully.'
        )

    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can remove cart items.'
        )
        return redirect('home')

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart__buyer=request.user
    )

    if request.method == 'POST':
        item.delete()

        messages.success(
            request,
            'Product removed from your cart.'
        )

    return redirect('view_cart')


@login_required
def checkout(request):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can checkout.'
        )
        return redirect('home')

    cart = get_object_or_404(
        Cart,
        buyer=request.user
    )

    items = cart.items.select_related(
        'product'
    )

    if not items.exists():
        messages.error(
            request,
            'Your cart is empty.'
        )
        return redirect('view_cart')

    total = sum(
        item.product.price * item.quantity
        for item in items
    )

    if request.method == 'POST':
        with transaction.atomic():
            order_items = list(items)

            for item in order_items:
                product = Product.objects.select_for_update().get(
                    id=item.product.id
                )

                if product.stock < item.quantity:
                    messages.error(
                        request,
                        f'Not enough stock for {product.name}.'
                    )
                    return redirect('view_cart')

            order = Order.objects.create(
                buyer=request.user,
                order_number=uuid.uuid4().hex[:12].upper(),
                total=total
            )

            for item in order_items:
                product = Product.objects.select_for_update().get(
                    id=item.product.id
                )

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item.quantity,
                    price=product.price
                )

                product.stock -= item.quantity
                product.save()

            cart.items.all().delete()

        invoice_lines = [
            'eCommerce Invoice',
            '',
            f'Order Number: {order.order_number}',
            f'Customer: {request.user.username}',
            '',
            'Items:',
            '----------------------------------------'
        ]

        for order_item in order.items.select_related('product'):
            item_total = (
                order_item.price * order_item.quantity
            )

            invoice_lines.append(
                f'{order_item.product.name} - '
                f'Qty: {order_item.quantity} - '
                f'R{item_total:.2f}'
            )

        invoice_lines.extend([
            '----------------------------------------',
            f'Total: R{order.total:.2f}',
            '',
            'Thank you for your purchase.'
        ])

        invoice_message = '\n'.join(invoice_lines)

        send_mail(
            subject=f'Invoice - Order {order.order_number}',
            message=invoice_message,
            from_email=None,
            recipient_list=[request.user.email],
            fail_silently=False
        )

        messages.success(
            request,
            'Your order has been placed successfully and '
            'the invoice has been emailed to you.'
        )

        return redirect(
            'order_detail',
            order_id=order.id
        )

    return render(
        request,
        'store/checkout.html',
        {
            'items': items,
            'total': total
        }
    )


@login_required
def order_detail(request, order_id):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can view orders.'
        )
        return redirect('home')

    order = get_object_or_404(
        Order,
        id=order_id,
        buyer=request.user
    )

    items = order.items.select_related(
        'product'
    )

    return render(
        request,
        'store/order_detail.html',
        {
            'order': order,
            'items': items
        }
    )


@login_required
def vendor_reviews(request):
    """Display reviews for products belonging to the logged-in vendor."""

    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'vendor':
        return redirect('home')

    reviews = (
        Review.objects
        .filter(product__store__vendor=request.user)
        .select_related('product', 'product__store', 'user')
        .order_by('-created_at')
    )

    return render(
        request,
        'store/vendor_reviews.html',
        {'reviews': reviews},
    )

@login_required
def order_list(request):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can view orders.'
        )
        return redirect('home')

    orders = Order.objects.filter(
        buyer=request.user
    ).order_by('-created_at')

    return render(
        request,
        'store/order_list.html',
        {'orders': orders}
    )

@login_required
def submit_review(request, product_id):
    if request.user.profile.role != 'buyer':
        messages.error(
            request,
            'Only buyers can submit reviews.'
        )
        return redirect('home')

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method != 'POST':
        return redirect(
            'product_detail',
            product_id=product.id
        )

    try:
        rating = int(request.POST.get('rating', ''))
    except (TypeError, ValueError):
        rating = 0

    comment = request.POST.get('comment', '').strip()

    if rating < 1 or rating > 5:
        messages.error(
            request,
            'Please select a rating between 1 and 5.'
        )
        return redirect(
            'product_detail',
            product_id=product.id
        )

    if not comment:
        messages.error(
            request,
            'Please enter a review comment.'
        )
        return redirect(
            'product_detail',
            product_id=product.id
        )

    verified_purchase = OrderItem.objects.filter(
        order__buyer=request.user,
        product=product
    ).exists()

    Review.objects.create(
        product=product,
        user=request.user,
        rating=rating,
        comment=comment,
        is_verified=verified_purchase
    )

    messages.success(
        request,
        'Your review has been submitted successfully.'
    )

    return redirect(
        'product_detail',
        product_id=product.id
    )

# REST API: List stores and create stores

@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_stores(request):
    """List stores or create a store for an authenticated vendor."""
    if request.method == 'GET':
        stores = Store.objects.all().select_related('vendor')
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)

    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'vendor':
        return Response(
            {'error': 'Only vendors can create stores.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = StoreSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(vendor=request.user)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


# REST API: List products and add products to a store

@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_store_products(request, store_id):
    """List a store's products or add a product to that store."""
    store = get_object_or_404(Store, id=store_id)

    if request.method == 'GET':
        products = Product.objects.filter(
            store=store
        ).select_related('store')

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    profile = getattr(request.user, 'profile', None)

    if not profile or profile.role != 'vendor':
        return Response(
            {'error': 'Only vendors can add products.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if store.vendor_id != request.user.id:
        return Response(
            {'error': 'You can only add products to your own stores.'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ProductSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(store=store)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )



# REST API: Retrieve reviews
@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_reviews(request):
    
    """Retrieve reviews, restricting vendors to their own products."""

    reviews = Review.objects.select_related(
        'product',
        'product__store',
        'user',
    ).all().order_by('-created_at')

    profile = getattr(request.user, 'profile', None)

    if profile and profile.role == 'vendor':
        reviews = reviews.filter(
            product__store__vendor=request.user
        )

    product_id = request.query_params.get('product_id')

    if product_id:
        reviews = reviews.filter(product_id=product_id)

    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


def reddit_feed(request):
    posts = get_reddit_posts()

    return render(request, 'store/reddit_feed.html', {
        'posts': posts
    })