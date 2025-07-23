from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def consultar_reportes(request):
    return render(request, 'consultar_reportes.html')