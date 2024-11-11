from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
 
def index(request):
    return render(request, "api_app/index.html")

def file_browser(request, file_id):
    return render(request, "api_app/file_browser.html", {
        "file_id": file_id
    })
    # return HttpResponse(f"This is a file browser page, the file has the following ID: {file_id}")