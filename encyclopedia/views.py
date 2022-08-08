from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from markdown2 import Markdown
from . import util

import random


markdowner = Markdown()

class NewPageForm(forms.Form):
    title = forms.CharField(label = "New Page Title", max_length=50)
    content = forms.CharField(label="New Markdown", 
        widget=forms.Textarea())


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def get_random_page(request):
    entries = util.list_entries()
    if entries:
        request.session["random"] = True
        title = random.choice(entries)
        return HttpResponseRedirect(reverse("entry_name", kwargs={ "title": title }))
    
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title): 
    
    if "random" in request.session and request.session["random"]:
         request.session["random"] = False
         return render(request, "encyclopedia/entry.html", {
                "entry": title, "entry_content": markdowner.convert(util.get_entry(title)) 
            })
    else:

        entry_search = title.upper()
        entries = util.list_entries()
        for entry in entries:
            if entry.upper() == entry_search:
                return render(request, "encyclopedia/entry.html", {
                    "entry": entry, "entry_content": markdowner.convert(util.get_entry(entry)) 
                })
    return render(request, "encyclopedia/pageNotFound.html", {
                "title": title})


def search_entry(request):
    search_query = request.GET.get('q', '')
    entries = util.list_entries()
    substrings = []
    for entry in entries:
        if search_query.upper() in entry.upper():
            # if exact match return the page
            if search_query.upper() == entry.upper():
                return render(request, "encyclopedia/entry.html", {
                    "entry": entry, "entry_content": markdowner.convert(util.get_entry(entry)) 
                })

            # otherwise its a substring of the entry
            substrings.append(entry)
    return render(request, "encyclopedia/search_results.html", {
        "search_results": substrings
    })        
            


def add_new_entry(request):
    if request.method == "POST":
        form = NewPageForm(request.POST)
        if form.is_valid():
            new_title = form.cleaned_data["title"]
            new_content = form.cleaned_data["content"]

            # you can't create a page that already exists
            if new_title.upper() in [entry.upper() for entry in util.list_entries()]:
                return render(request, "encyclopedia/new_entry.html", {
                    "form": form, 
                    "error_message": "A page with this title already exists!"
                }) 
    
            else:
                util.save_entry(new_title, new_content)
                return HttpResponseRedirect(reverse("entry_name", kwargs={ "title": new_title }))
                
        else:
            return render(request, "encyclopedia/new_entry.html", {
                "form": form
            })

    # if it's a GET request just return the page with a blank form
    return render(request, "encyclopedia/new_entry.html", {
        "form": NewPageForm()
    })


def edit_entry(request, title):
    if request.method == "POST":
        content = request.POST["content"]
        form = NewPageForm({
            "title": title, "content": content
        })
        if form.is_valid():
            new_content = form.cleaned_data["content"]
            util.save_entry(title, new_content)
            return HttpResponseRedirect(reverse("entry_name", kwargs={ "title": title }))              
        else:
            return render(request, "encyclopedia/edit_entry.html", {
                "form": form, "entry": title
            })

    # a GET request to edite the page with given title
    form = NewPageForm(initial={
        "title": title, "content": util.get_entry(title)
    })
    # do not allow the user to change the title
    form.fields["title"].disabled = True
    return render(request, "encyclopedia/edit_entry.html", {
        "form": form, "entry": title
    })