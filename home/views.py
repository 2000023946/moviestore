from django.shortcuts import render #type: ignore

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

