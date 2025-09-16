from django.shortcuts import render #type: ignore
from cart.models import Order
from django.db.models import Sum


def index(request):
    template_data = {}
    template_data['title'] = 'Movies Store'

    return render(request, 'home/index.html', {
        'template_data': template_data})


def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request,
        'home/about.html',
        {'template_data': template_data})

def subs(request):
    template_data = {}
    template_data['title'] = 'About'
    subs = get_total_spent(request.user)
    if subs < 15:
        template_data['subscription'] = 'Basic'
    elif subs < 30:
        template_data['subscription'] = 'Medium'
    else: 
        template_data['subscription'] = 'Premium'

    return render(request,
        'home/subs.html',
        {'template_data': template_data})

def get_total_spent(user):
    return (
        Order.objects
        .filter(user=user)
        .aggregate(total_spent=Sum('total'))
    )['total_spent'] or 0

