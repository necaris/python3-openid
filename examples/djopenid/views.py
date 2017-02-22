from djopenid import util
from django.views.generic.base import TemplateView


def index(request):
    consumer_url = util.getViewURL(request,
                                   'djopenid.consumer.views.startOpenID')
    server_url = util.getViewURL(request, 'djopenid.server.views.server')

    return TemplateView(request, 'index.html', {
        'consumer_url': consumer_url,
        'server_url': server_url
    })
