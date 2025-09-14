from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, WishList, WishListItem, UserReviewHeart
from django.contrib.auth.decorators import login_required
from django.db.models import Q


def index(request):

    sort = request.GET.get('sort', '')
    search_term = request.GET.get('search', '')

    if search_term:
        movies = Movie.objects.filter(
            Q(name__icontains=search_term) |
            Q(genre__icontains=search_term)
        )
    elif sort:
        movies = Movie.objects.order_by(sort)
        print(movies)
    else:
        movies = Movie.objects.all()

    template_data = {
        'title': 'Movies',
        'movies': movies,
        'recently_viewed': [Movie.objects.get(id=id) for id in request.session.get('recently_viewed', [])],
        'reviews': Review.objects.order_by('-votes')[:5],
        'most_voted': Movie.objects.order_by('-votes')[:5],
        'favorites': [Movie.objects.get(id=id) for id in request.session.get('favorites', [])],
        'sort_options': get_sort_options()
    }

    return render(request, 'movies/index.html', {'template_data': template_data})

def get_sort_options():
    allowed_fields = ['name', 'price', 'votes', 'genre']  

    sort_options = []
    for f in allowed_fields:
        sort_options.append((f, f"Ascending by {f.capitalize()}"))
        sort_options.append((f"-{f}", f"Descending by {f.capitalize()}"))

    return sort_options



def vote_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.votes += 1
    review.save()
    return redirect('movies.index')

def addFavorite(request, id):
    favs = request.session.get('favorites', [])
    if id not in favs:
        favs.append(id)
    request.session['favorites'] = favs
    return redirect('movies.show', id=id)  # redirect back to movie page

def removeFavorite(request, id):
    favs = request.session.get('favorites', [])
    if id in favs:
        favs.remove(id)
    request.session['favorites'] = favs
    return redirect('movies.index')  # redirect back to movie page

def vote_movie(request, id):
    movie = get_object_or_404(Movie, id=id)
    movie.votes += 1
    movie.save()
    return redirect('movies.show', id=id)  # redirect back to movie page

def vote_movie_down(request, id):
    movie = get_object_or_404(Movie, id=id)
    movie.de_vote()
    return redirect('movies.show', id=id)  # redirect back to movie page


def show(request, id):
    movie = get_object_or_404(Movie, id=id)
    reviews = Review.objects.filter(movie=movie).order_by('-votes')[:5]

    exists = isWishListEmpty(request, movie)
    addToRecent(request, id)
    print('added to recents', request.session.get('recently_viewed'))

    reviews = get_reviews(reviews, request)


    template_data = {
        'title': movie.name,
        'reviews': reviews,
        'movie': movie,
        'inCart': str(id) in request.session.get('cart', {}),
        'wishList': 'Remove' if exists else 'Add',
        'inFavorite': id in request.session.get('favorites', []),
        'stars': movie.avg_stars(),
    }

    return render(request, 'movies/show.html', {'template_data': template_data})

def get_reviews(reviews, request):
    if not request.user.is_authenticated:
        return reviews
    full_reviews = []

    for i, review in enumerate(reviews):
        userHeart = getOrCreateUserHeart(request, review)
        full_reviews.append((userHeart.heart, review))

    return full_reviews


def getOrCreateUserHeart(request, review): 
    if UserReviewHeart.objects.filter(user=request.user, review=review).exists():
        userHeart = UserReviewHeart.objects.get(user=request.user, review=review)
    else:
        userHeart = UserReviewHeart.objects.create(user=request.user, review=review)

    return userHeart

@login_required
def like_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Checkbox sends 'on' if checked, nothing if unchecked
    liked = 'liked' in request.POST  

    userHeart = getOrCreateUserHeart(request, review)

    userHeart.heart = liked

    userHeart.save()

    # redirect back to the movie detail page
    return redirect('movies.show', id=review.movie.id)


def addToRecent(request, id):
    recents = request.session.get('recently_viewed', [])

    if id in recents:
        recents.remove(id)

    recents.insert(0, id)
    recents = recents[:5]

    request.session['recently_viewed'] = recents


@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = get_object_or_404(Movie, id=id)
        review = Review(comment=request.POST['comment'], movie=movie, user=request.user, stars=request.POST['stars'])
        review.save()
    return redirect('movies.show', id=id)


@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {'title': 'Edit Review', 'review': review}
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review.comment = request.POST['comment']
        review.save()
    return redirect('movies.show', id=id)


@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)


def addWishList(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    wishList = getWishList(request)
    addToWishList(request, movie, wishList)
    return redirect('movies.show', id=movie_id)


def removeWishList(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    wishList = getWishList(request)
    removeFromWishList(request, movie, wishList)
    return redirect('movies.show', id=movie_id)


def getWishList(request):
    user = request.user
    if not user.is_authenticated:
        return request.session.get('wishList', [])
    wishList = WishList.objects.filter(user=user).first()
    if not wishList:
        wishList = WishList.objects.create(user=user)
    return wishList

def convertSesionWishListToModel(request):
    sessionList = request.session.get('wishList', {})
    if len(sessionList) > 0:
        wishList = getWishList(request)
        print('user', wishList)
        for movie_id in sessionList:
            movie = Movie.objects.get(id=movie_id)
            WishListItem.objects.create(movie=movie, wishList=wishList)
            print('created new wishLiust item')
        del request.session['wishList']
        


def isWishListEmpty(request, movie):
    if request.user.is_authenticated:
        return WishListItem.objects.filter(movie=movie, wishList=getWishList(request)).exists()
    return movie.id in request.session.get('wishList', [])


def addToWishList(request, movie, wishList):
    if request.user.is_authenticated:
        WishListItem.objects.get_or_create(movie=movie, wishList=wishList)
    else:
        if movie.id not in wishList:
            wishList.insert(0, movie.id)
            request.session['wishList'] = wishList


def removeFromWishList(request, movie, wishList):
    if request.user.is_authenticated:
        WishListItem.objects.filter(movie=movie, wishList=wishList).delete()
    else:
        if movie.id in wishList:
            wishList = set(wishList)
            wishList.remove(movie.id)
            wishList = list(wishList)
            request.session['wishList'] = wishList
