from django.core.cache import cache as core_cache

'''
refer:
    http://stackoverflow.com/questions/20146741/django-per-user-view-caching
    https://djangosnippets.org/snippets/2524/
'''


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


def cache_per_user_function(ttl=None, prefix=None, cache_post=False):
    '''
    Decorator which caches the view for each User
    * ttl - the cache lifetime, do not send this parameter means that the cache
      will last until the restart server or decide to remove it
    * prefix - Prefix to use to store the response in the cache. If not informed,
      it will be used 'view_cache _' + function.__ name__
    * cache_post - Determine whether to make requests cache POST
    * The caching for anonymous users is shared with everyone
    
    How to use it:

    @cache_per_user_function(ttl=3600, cache_post=False)
    def my_view(request):
        return HttpResponse("LOL %s" % (request.user))
    '''
    def decorator(function):
        def apply_cache(request, *args, **kwargs):
            CACHE_KEY = cache_key(request)
            # Gera a chave do cache
            if prefix:
                CACHE_KEY = '%s_%s' % (prefix, CACHE_KEY)
            
            # Verifica se pode fazer o cache do request
            if not cache_post and request.method == 'POST':
                can_cache = False
            else:
                can_cache = True

            if can_cache:
                response = core_cache.get(CACHE_KEY, None)
            else:
                response = None

            if not response:
                response = function(request, *args, **kwargs)
                if can_cache:
                    core_cache.set(CACHE_KEY, response, ttl)
            return response
        return apply_cache
    return decorator


def cache_per_user_method(ttl=None, prefix=None, cache_post=False):
    '''
    Decorator which caches the view for each User
    * ttl - the cache lifetime, do not send this parameter means that the cache
      will last until the restart server or decide to remove it
    * prefix - Prefix to use to store the response in the cache. If not informed,
      it will be used 'view_cache _' + function.__ name__
    * cache_post - Determine whether to make requests cache POST
    * The caching for anonymous users is shared with everyone

    How to use it:
    @cache_per_user_method(ttl=3600, cache_post=False)
    def get(self, request):
        ...
    '''
    def decorator(view_method):
        def apply_cache(obj, request, *args, **kwargs):

            CACHE_KEY = cache_key(request)
            # Gera a chave do cache
            if prefix:
                CACHE_KEY = '%s_%s' % (prefix, CACHE_KEY)

            # Verifica se pode fazer o cache do request
            if not cache_post and request.method == 'POST':
                can_cache = False
            else:
                can_cache = True

            if can_cache:
                response = core_cache.get(CACHE_KEY, None)
            else:
                response = None

            if not response:
                response = view_method(obj, request, *args, **kwargs)
                if can_cache and hasattr(response, 'render'):
                    core_cache.set(CACHE_KEY, response.render(), ttl)
            return response
        return apply_cache
    return decorator