from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Author


def index(request):
	author_list = Author.objects.order_by('-name')[:5]
	template = loader.get_template('mafirstapp/index.html')
	context = {
		'author_list': author_list
	}
	return HttpResponse(template.render(context, request))
