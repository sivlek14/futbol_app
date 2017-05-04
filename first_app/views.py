# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from django.http import JsonResponse

from django.views.decorators.cache import cache_control
from cache import cache_per_user_function
import datetime

@cache_per_user_function(ttl=5, prefix="hey")
def index(request):
	print 
	response = {"datetime": datetime.datetime.now(),"completed_in": "2.0028 segundos","c": {"d": "e"},"a": "b"}
	return JsonResponse(response)