from django.shortcuts import redirect, render, HttpResponse ,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.core.mail import send_mail
from .models import Product, Cart , CartItem , Transaction
from django.views.decorators.csrf import csrf_exempt
import pyotp
from django.contrib.auth import authenticate, login
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("index") 
        else:
            messages.error(request, "Email and password are incorrect")
            return render(request, 'login.html')
    return render(request, 'login.html')
def send_otp(email):
    otp_secret = pyotp.random_base32()
    otp = pyotp.TOTP(otp_secret)
    otp_code = otp.now()

    send_mail(
        'OTP Verification',
        f'Your OTP is: {otp_code}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

    return otp_secret, otp_code
def signup(request):
    if request.method == "POST":
        name = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if pass1 == pass2:
            try:
                # Validate password
                validate_password(pass1, user=User)
                
                # Send OTP
                otp_secret, otp_code = send_otp(email)
                request.session['otp_secret'] = otp_secret
                request.session['email'] = email
                request.session['otp_code'] = otp_code
                request.session['name'] = name
                request.session['lname'] = lname
                request.session['pass1'] = pass1
                return redirect('otp verify')
            except ValidationError as error:
                messages.error(request, error)
        else:
            messages.error(request, "Passwords do not match")

    return render(request, 'signup.html')

def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get('otp')
        otp_secret = request.session.get('otp_secret')
        email = request.session.get('email')
        otp_code = request.session.get('otp_code')
        name = request.session.get('name')
        lname = request.session.get('lname')
        password=request.session.get('pass1')
        if otp_secret and otp == otp_code:
            myuser = User.objects.create_user(email=email, username=email, password=password)
            myuser.first_name = name
            myuser.last_name = lname
            myuser.save()
            messages.success(request, "Your account has been successfully created")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP")
    else:
        return render(request, 'opt.html')
    return redirect('signup')
def logout_view(request):
    logout(request)
    return redirect('index')  
def home(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})
from django.shortcuts import get_object_or_404, redirect
from .models import Cart, CartItem, Product

from django.shortcuts import get_object_or_404, redirect
from .models import Cart, CartItem, Product

def add_to_cart(request, product_id):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
            
            # Get the product and its quantity from the request
            product = get_object_or_404(Product, pk=product_id)
            quantity = int(request.POST.get('quantity', 1))  # Default to 1 if not provided
            price=product.price
            # Get or create the cart item for the product
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product,price=price)

            # If the cart item is not newly created, update its quantity
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                # If the cart item is newly created, set its quantity and price
                cart_item.quantity = quantity
                cart_item.price = product.price  # Set the price from the product
                cart_item.save()

            messages.success(request, f'{product.name} has been added to your cart.')

            return redirect('home')  # Redirect to the home page
        else:
            # Redirect to login page if user is not authenticated
            return redirect('login')
    else:
        # Handle the case where the request method is not POST
        return redirect('home')  # Redirect to the home page or another appropriate page


def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cartitem_set.all()
    total_price = sum(item.get_total_price() for item in cart_items)
    fname=request.user.first_name
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price, 'fname':fname})



def checkout(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = CartItem.objects.filter(cart=cart)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})



def update_quantity(request, product_id):
    if request.method == 'POST':
        user = request.user
        if user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=user)
            product = get_object_or_404(Product, pk=product_id)
            quantity = int(request.POST.get('quantity', 1))
            action = request.POST.get('action')

            # Get or create the cart item for the product
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

            if action == 'add':
                cart_item.quantity += quantity
            elif action == 'subtract':
                cart_item.quantity -= quantity
                if cart_item.quantity < 1:
                    cart_item.delete()

                    messages.info(request, f"{product.name} removed from cart.")
                    return redirect('cart')

            cart_item.save()

            messages.success(request, f"{product.name} quantity updated.")
            return redirect('cart')
        else:
            messages.error(request, "Please login to update cart.")
            return redirect('login')
    else:
        return redirect('cart')  # Redirect to the home page or another appropriate page
@csrf_exempt
def initiate_payment(request):
    user = request.user
    if request.method == 'POST':
        # Fetch the cart items for the current user
        cart = Cart.objects.get(user=user)
        cart_items = cart.cartitem_set.all()

        # Calculate total amount from cart items
        total_amount = sum(item.get_total_price() for item in cart_items)

        # Create a transaction with 'Pending' status
        transaction = Transaction.objects.create(amount=total_amount, status='Pending')

        # Clear cart items after initiating payment
        cart_items.delete()

        return render(request, 'payment.html', {'transaction_id': transaction.transaction_id, 'totalamt':total_amount})
    else:
        return HttpResponse("Method not allowed", status=405)

@csrf_exempt

def process_payment(request, transaction_id):  
    if request.method == 'POST':
        # Try to get the transaction object
        transaction = get_object_or_404(Transaction, pk=transaction_id)
        
        # Simulate payment process
        transaction.status = 'Success'
        transaction.save()
        user_email = request.user.email
        
        # Send email confirmation
        subject = 'Payment Confirmation'
        message = f'Your payment for transaction ID {transaction_id} has been successfully registered.'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user_email]  # Using current user's email
        send_mail(subject, message, email_from, recipient_list)

        return render(request, 'process_payment.html', {'transaction': transaction})
    
    else:
        # Return method not allowed if request method is not POST
        return HttpResponse("Method not allowed", status=405)

def resend_otp(request):
    if request.method == 'GET':
        email = request.session.get('email')
        if email:
            otp_secret, otp_code = send_otp(email)
            request.session['otp_secret'] = otp_secret
            request.session['otp_code'] = otp_code
            return HttpResponse('OTP resent!')
    return HttpResponse('Failed to resend OTP', status=400)
def track_order(request):
    return render(request,"map.html")
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomerReview

def submit_review(request):
    if request.method == 'POST':
        customer_name = request.POST.get('customerName')
        review_text = request.POST.get('reviewText')
        
        # Save the review to the database
        review = CustomerReview.objects.create(customer_name=customer_name, review_text=review_text)
        review.save()
        
        messages.success(request, 'Thank you for your review!')
        return redirect('track_order')
    else:
        messages.error(request, 'Invalid request method')
        return redirect('track_order')


