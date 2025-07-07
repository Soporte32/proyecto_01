from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Create your views here.

@login_required
def dashboard(request):
    usuario = request.user
    jadministradores = False
    jpresupuestos = False
    jventas = False
    jrrhh = False
    if usuario.groups.filter(name='Administradores').exists():
        jadministradores = True
    if usuario.groups.filter(name='Recursos Humanos').exists():
        jrrhh = True
    if usuario.groups.filter(name='Presupuestos').exists():
        jpresupuestos = True
    if usuario.groups.filter(name='Ventas').exists():
        jventas = True			
    contexto = {"jadministradores": jadministradores,"jrrhh": jrrhh,"jpresupuestos": jpresupuestos,"jventas": jventas}
    return render(request, 'dashboard.html', contexto)

