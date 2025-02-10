from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from api_app.csv_parser.csv_parser import generate_report, example_files

# Create your views here.
def index(request):
    return render(request, "api_app/index.html")

def file_browser(request, file_id):
    return render(request, "api_app/file_browser.html", {
        "file_id": file_id
    })
    # return HttpResponse(f"This is a file browser page, the file has the following ID: {file_id}")

def get_file_names(request):
    return JsonResponse(example_files, safe=False)