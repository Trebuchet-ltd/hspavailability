from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,template_name='v2/index.html')

def login(request):
    return render(request, template_name='v2/login.html')