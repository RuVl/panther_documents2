from django.http import HttpRequest, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, TemplateView

from mainapp.forms import GetProducts
from mainapp.models import Country

'''
ListView - данные о каждой записи модели
DetailedView - данные о конкретной записи в бд
CreateView - создание записи с помощью формы
'''


class PassportListView(ListView):
    queryset = (Country.objects.exclude(passport__isnull=True)
                .exclude(passport__passportfile__is_sold=True)
                .exclude(passport__passportfile__is_reserved=True)
                .prefetch_related('passport_set').all())
    template_name = 'main/passports.html'
    context_object_name = 'countries'  # Переменная в шаблоне для модели

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['lang'] = 'ru'
        context['title'] = 'PantherDoc'
        return context


class SupportView(TemplateView):
    template_name = 'main/support.html'


def get_products(request: HttpRequest):
    if request.method != 'POST':
        return HttpResponseBadRequest('Only post request!')

    form = GetProducts(request.POST)
    return JsonResponse(form.response) if form.is_valid() else HttpResponseBadRequest(form.errors)


# noinspection PyUnusedLocal
def page_not_found(request, exception):
    return render(request, '404.html', status=404)
