from django.shortcuts import render


def records_app(request):
    """
    Главная страница со списком записей ДДС.
    Шаблон: templates/dds/records_spa.html
    """
    return render(request, 'dds/records_spa.html')


def dictionaries_app(request):
    """
    Страница управления справочниками (статусы, типы, категории, подкатегории).
    Шаблон: templates/dds/dictionaries_spa.html
    """
    return render(request, 'dds/dictionaries_spa.html')