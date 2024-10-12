from django.shortcuts import render


def homepage(request):
    # return HttpResponse("Hello World! I'm Home.")
    return render(request, 'home.html')
