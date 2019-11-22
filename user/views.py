import redis
import mysql
from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect

from .models import Url


pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
r = redis.Redis(connection_pool=pool)


class IndexView(View):
    '''首页'''
    def get(self, request):
        # 首页
        return render(request, 'index.html', {
            'short_url': ''
        })

    def post(self, request):
        # 把传入的上网址分配一个id，并存入mysql
        long_url = request.POST.get('long_url', '')
        if long_url:
            index = int(r.incr(0))
            locked = r.set('string_locked%s'%index, 1, ex=30, nx=2)
            if locked:
                r.set(name=index, value=long_url)
                short_url = 'http://182.61.150.93:82/' + str(index)
                r.lpush('queue', index, long_url)
                r.delete('string_locked%s'%index)
                return render(request, 'index.html', {
                    'short_url': short_url
                })
            else:
                return render(request, 'failure.html')


class UrlView(View):
    '''根据传入的参数查找出长网址，为避免缓存穿透，在查找不存在的key时会在缓存中记录为空，直至被修改'''
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
    lenn = r.llen('list')
    if lenn:
        for i in range(int(lenn/2)):
            id = r.rpop('list')
            url = r.rpop('list').decode('utf-8')
            # 这里应该有mysql的消息队列可以用才好
            try:
                status = Url.objects.get(id=t.decode('utf-8'))
            except:
                status = Url()
                status.id = id
            status.url = url
            status.save()
