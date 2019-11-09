import redis

from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect

from .models import Url


pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=2)
r = redis.Redis(connection_pool=pool)


class IndexView(View):
    def get(self, request):
        return render(request, 'index.html', {
            'short_url': ''
        })

    def post(self, request):
        long_url = request.POST.get('long_url', '')
        if long_url:
            index = int(r.incr(0))
            r.set(name=index, value=long_url)
            short_url = 'http://182.61.150.93:82/' + str(index)
            return render(request, 'index.html', {
                'short_url': short_url
            })


class UrlView(View):
    def get(self, request, index):
        if index:
            long_url = r.get(index)
            if long_url:
                long_url = long_url.decode()
                if long_url[:4] != 'http':
                    long_url = 'http://' + long_url
                return render(request, 'url.html', {
                    'long_url': long_url
                })
            try:
                long_url = Url.objects.get(id=index).url
                r.set(name=index, value=long_url)
                if long_url[:4] != 'http':
                    long_url = 'http://' + long_url
            except:
                long_url = None
                r.set(index, None)
            finally:
                return render(request, 'url.html', {
                    'long_url': long_url
                })


def play():
    for t in r.keys():
        if t == b'0':
            continue
        try:
            start = Url.objects.get(id=t.decode('utf-8'))
        except:
            start = Url()
            start.id = t.decode('utf-8')
        start.url = r.get(t).decode('utf-8')
        start.save()



