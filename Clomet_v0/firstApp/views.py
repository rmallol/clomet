
import json
import re
from django.shortcuts import render
from .forms import UploadForm, UrlForm
from django.http import JsonResponse

from utilities.clomet_v2.Dataset import Dataset

from django.shortcuts import HttpResponse

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def indexView(request):

    global dataset
    dataset = Dataset()

    form = UrlForm()
    return render(request, "firstApp/index.html", {"form": form})

def indexLocal(request):
    global dataset
    dataset = Dataset()

    form = UploadForm()
    return render(request, "firstApp/indexLocal.html", {"form": form})

def procno(request):
    if is_ajax(request=request) and request.method == "POST":
        form = UrlForm(request.POST)
        if form.is_valid():

            id = request.POST.get('urldata', '')
            result = dataset.firstView(id)

            if ( result["errors"]["message"] == "No"):
                return JsonResponse({"instance": result["procnos"], "links": result["links"]}, status=200)
            else:
                return JsonResponse( {"error": result}, status=400 )

        else:
            return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": ""}, status=400)

def procnoLocal(request):
    if is_ajax(request=request) and request.method == "POST":
        if request.FILES['localdata']:
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                id = request.FILES['localdata']

                if 'dataset' not in globals():
                    global dataset
                    dataset = Dataset()

                result = dataset.firstViewLocal(id)


                if ( result["errors"]["message"] == "No"):
                    return JsonResponse({"instance": result["procnos"], "links": result["links"]}, status=200)
                else:
                    return JsonResponse( {"error": result}, status=400 )
        else:
            return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": ""}, status=400)




def dataimport(request):
    if is_ajax(request=request) and request.method == "POST":
        form = UrlForm(request.POST)
        if form.is_valid():

            procnofull = request.POST.get('urldata', '')
            id = request.POST.get('id', '')

            result = dataset.secondView(procnofull, id)

            if ( result["errors"]["message"] == "No"):
                return JsonResponse({"values": result["files"], "tabledata": result["data"], "extras": result["extras"]}, status=200)
            else:
                return JsonResponse( {"error": result}, status=400 )
        else:
            return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": ""}, status=400)

def dataimportLocal(request):
    if is_ajax(request=request) and request.method == "POST":
        form = UrlForm(request.POST)
        if form.is_valid():

            procnofull = request.POST.get('urldata', '')
            id = request.POST.get('id', '')

            id = id.split('\\')[-1]
            id = id.split(".", 1)[0]

            if 'dataset' not in globals():
                    global dataset
                    dataset = Dataset()
                    
            result = dataset.secondView(procnofull, str(id) + "_data")

            if ( result["errors"]["message"] == "No"):
                return JsonResponse({"values": result["files"], "tabledata": result["data"], "extras": result["extras"]}, status=200)
            else:
                return JsonResponse( {"error": result}, status=400 )
        else:
            return JsonResponse({"error": form.errors}, status=400)
    return JsonResponse({"error": ""}, status=400)

def docker(request):
    return render(request, 'firstApp/docker.html')

def about(request):
    return render(request, 'firstApp/about.html')

def tutorials(request):

    dataset = Dataset()
    result = dataset.tutorials()

    return render(request, 'firstApp/tutorials.html', {"datasets": result["datasets"], "rawdata": result["rawdata"], "mas": result["mas"], "w4ms": result["w4ms"]})

def tests(request):
    dataset = Dataset()
    result = dataset.tests()
    return render(request, 'firstApp/popup.html')
