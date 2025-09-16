from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie, WishList, WishListItem
from .utils import calculate_cart_total

from movies.views import getWishList

from django.shortcuts import get_object_or_404, redirect

def add(request, id):
    print('adding multi')
    movie = get_object_or_404(Movie, id=id)  # Ensure movie exists
    cart = request.session.get('cart', {})  # Get existing cart or empty dict
    print(cart)

    current_quantity = int(cart.get(str(id), 0))  # Existing quantity or 0

    if 'quantity' in request.POST:
        # Add the posted quantity to current quantity
        try:
            added_quantity = int(request.POST['quantity'])
        except ValueError:
            added_quantity = 1  # fallback if invalid input
        cart[str(id)] = current_quantity + added_quantity
    else:
        # Add 1 if no quantity specified
        cart[str(id)] = current_quantity + 1

    request.session['cart'] = cart  # Save back to session
    return redirect('home.index')

from django.shortcuts import get_object_or_404, redirect

def remove(request, id):
    print('deleting movie', id)
    movie = get_object_or_404(Movie, id=id)  # Ensure movie exists
    cart = request.session.get('cart', {})
    print('cart', cart)

    item_key = str(id)
    current_quantity = int(cart.get(item_key, 0))

    if 'quantity' in request.POST:
        try:
            remove_quant = int(request.POST['quantity'])
        except ValueError:
            remove_quant = 1  # fallback if invalid input
        new_quantity = max(current_quantity - remove_quant, 0)
        if new_quantity > 0:
            cart[item_key] = new_quantity
        else:
            cart.pop(item_key, None)  # safely remove if 0
    else:
        # Remove the item completely, safely
        cart.pop(item_key, None)

    request.session['cart'] = cart
    return redirect('home.index')


def index(request):
    print('accessing cart')
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart,
            movies_in_cart)
        
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total

    if request.user.is_authenticated: 
        print('getting auth user iwshList', [item.movie for item in getWishList(request).wishList.all()])
        template_data['wishList_items'] = [item.movie for item in getWishList(request).wishList.all()]

    else:
        print('session wishLIst', request.session.get('wishList', []))
        template_data['wishList_items'] = [Movie.objects.get(id=id) for id in request.session.get('wishList', [])]
        print('wishList objects sql', template_data['wishList_items'])
        
    return render(request, 'cart/index.html',
        {'template_data': template_data})

def add_to_cart(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')



def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

from .models import Order, Item
from django.contrib.auth.decorators import login_required

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
    item.save()
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html',
        {'template_data': template_data})