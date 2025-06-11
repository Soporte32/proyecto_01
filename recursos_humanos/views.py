from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import *
from django.http import HttpResponseRedirect

@login_required
def rh_inicio(request):
    usuario = request.user
    if not usuario.groups.filter(name='Recursos Humanos').exists():
        return HttpResponseRedirect("/")
    jtemplate = get_template('rh-inicio.html')
    return HttpResponse(jtemplate.render())
	
