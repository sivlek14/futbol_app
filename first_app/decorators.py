from django.http import JsonResponse

from django.core.cache import cache as core_cache

from xml.etree import ElementTree

import time, datetime, requests

def cache_key(request):
	if request.user.is_anonymous():
		user = 'anonymous'
	else:
		user = request.user.id

	q = getattr(request, request.method)
	q.lists()
	urlencode = q.urlencode(safe='()')

	CACHE_KEY = 'view_cache_%s_%s_%s' % (request.path, user, urlencode)
	return CACHE_KEY

def get_data():
	def decorator(function):
		def get_xml(request, *args, **kwargs):
			url = "https://s3-sa-east-1.amazonaws.com/cmpsbtv/matchs.xml"
			response = requests.get(url, stream=True)
			response.raw.decode_content = True
			events = ElementTree.parse(response.raw)

			return function(request, events=events, *args, **kwargs)
		return get_xml
	return decorator

def cache_per_user_function(ttl=None, prefix=None, cache_post=False):
	def decorator(function):
		def apply_cache(request, *args, **kwargs):
			CACHE_KEY = cache_key(request)
			now = datetime.datetime.now()
			can_cache = True
			response = core_cache.get(CACHE_KEY, None)
			if not response:
				time.sleep(2)
				kwargs['datetime'] = now
				response = function(request, *args, **kwargs)
				if can_cache:
					core_cache.set(CACHE_KEY, response, ttl)
				return JsonResponse(response)
			else:
				response["completed_in"] = "%s segundos" %str(datetime.datetime.now() - now) 
				return JsonResponse(response)
		return apply_cache
	return decorator