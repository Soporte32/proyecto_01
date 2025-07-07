from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect


@login_required
def rh_inicio(request):
    usuario = request.user
    if not usuario.groups.filter(name='Recursos Humanos').exists():
        return HttpResponseRedirect("/")
    return render(request, 'rh-inicio.html')
	
