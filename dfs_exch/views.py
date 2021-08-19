from django.shortcuts import render


def test_(request):
    return render(request, "dfs\\list.html", context={"hellow": "world"})

