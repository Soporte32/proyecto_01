from django.db import models
from django.contrib.auth.models import User

sexos = (('F','Femenino'),('M','Masculino'))
si_o_no = (('S','Sí'),('N','No'))
ACTIVO_CHOICES = [("Si", "Si"),("No", "No"),]
OPCIONES_ACTIVO = [('s', 'Sí'), ('n', 'No'),]

class TipoEmpleado(models.Model):
    nombre = models.CharField(max_length=20, choices=[('SAMIC', 'SAMIC'),('Formenti', 'Formenti'),('Residente', 'Residente'),], blank=False, null=False)  

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name='Tipo de Empleado'
        verbose_name_plural='Tipos de Empleados'
        db_table='tipos_empleados'
        ordering=['nombre']

class Empleado(models.Model):
    legajo = models.PositiveIntegerField(verbose_name='Legajo', blank=False, null=False)
    nombre =  models.CharField(max_length=254, verbose_name='Nombres', blank=False, null=False)
    apellido =  models.CharField(max_length=254, verbose_name='Apellidos', blank=False, null=False)
    usuario = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.RESTRICT, null=True, related_name='empleado_usuario')

    dni = models.PositiveIntegerField(verbose_name='DNI', blank=False, null=False)
    cuil = models.CharField(max_length=13, verbose_name='CUIL', blank=False, null=False)
    fecha_nacimiento = models.DateField(verbose_name='Fecha de Nacimiento', blank=True, null=True)

    telefono =  models.CharField(max_length=25, verbose_name='Teléfono', blank=True, null=True)
    email = models.EmailField(verbose_name='Correo Electrónico', blank=True, null=True)

    tipo_empleado = models.ForeignKey("TipoEmpleado", verbose_name='Tipo', on_delete=models.RESTRICT, null=True)
    matricula = models.CharField(max_length=20, verbose_name='Matrícula', blank=True, null=True)   
    fecha_ingreso = models.DateField(verbose_name='Fecha de Ingreso', blank=True, null=True)

    autorizante1 = models.ForeignKey(User, verbose_name='Autorizante 1', on_delete=models.RESTRICT, null=True, related_name='empleado_autorizante1')
    autorizante2 = models.ForeignKey(User, verbose_name='Autorizante 2', on_delete=models.RESTRICT, null=True, related_name='empleado_autorizante2')

  #  sexo = models.CharField(max_length=1, choices=sexos, verbose_name='Sexos', default='F')
  
    fecha_creacion = models.DateTimeField(verbose_name='Fecha de Creación', auto_now_add=True)
    activo = models.CharField(max_length=2, choices=ACTIVO_CHOICES, default="Si")
	
    def nombre_completo(self):
        return (self.apellido + ", " + self.nombre)
		
    def __str__(self):
        return self.nombre_completo()

    class Meta:
        verbose_name='Empleado'
        verbose_name_plural='Empleados'
        db_table='empleados'
        ordering=['apellido','nombre']

# -----------------------------------------------------------------------------------------------
#      R E C U R S O S  H U M A N O S
# -----------------------------------------------------------------------------------------------

class Horarios_Horas_Samic(models.Model):
    hora = models.TimeField(unique=True)
    activo = models.CharField(max_length=1, choices=OPCIONES_ACTIVO, default='s')

    def __str__(self):
        return self.hora.strftime("%H:%M")
    
    class Meta:
        verbose_name='Horario para Horas Samic'
        verbose_name_plural='Horarios para Horas Samic'
        db_table='horarios_horas_samic'    


class SolicitudHorasSamic(models.Model):
    fecha_solicitud = models.DateField(verbose_name='Fecha solicitud', blank=False, null=False) 
    empleado= models.ForeignKey("Empleado", verbose_name='Empleado', on_delete=models.RESTRICT, null=False)
    usuario = models.ForeignKey(User, verbose_name='Usuario', on_delete=models.RESTRICT, null=True, related_name='solicitudhorassamic_usuario')
    fecha = models.DateField(verbose_name='Fecha', blank=False, null=False)
    hora_desde = models.ForeignKey(Horarios_Horas_Samic, verbose_name='Hora desde', on_delete=models.RESTRICT, related_name='solicitudhorassamic_desde', null=False)
    hora_hasta = models.ForeignKey(Horarios_Horas_Samic, verbose_name='Hora hasta', on_delete=models.RESTRICT, related_name='solicitudhorassamic_hasta', null=False)
    minutos_solicitados = models.IntegerField(verbose_name='Minutos solicitados', default=0)

    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'),('autorizado', 'Autorizado'),('rechazado', 'Rechazado'),('realizado', 'Realizado'),('anulado', 'Anulado'),], blank=False, null=False)

    autorizante = models.ForeignKey(User, verbose_name='Autorizante', on_delete=models.RESTRICT, null=True, related_name='solicitudhorassamic_autorizante')
    finalizo = models.ForeignKey(User, verbose_name='Finalizó', on_delete=models.RESTRICT, null=True, related_name='solicitudhorassamic_finalizo')

    class Meta:
        verbose_name='Solicitud de Horas Samic'
        verbose_name_plural='Solicitudes de Horas Samic'
        db_table='solicitudes_horas_samic'


class TipoDia(models.Model):
    nombre = models.CharField(max_length=20, choices=[('habil', 'Hábil'),('inhabil', 'Inhábil'),('feriado', 'Feriado'),('no_laborable', 'No Laborable'),], blank=False, null=False)   
    descripcion = models.CharField(max_length=150, verbose_name='Descripción (opcional)', blank=True, null=True)
    computa_vacaciones = models.CharField(max_length=1, choices=si_o_no, verbose_name='¿Computa Vacaciones?', default='S')

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name='Tipo de Día'
        verbose_name_plural='Tipos de Días'
        db_table='tipos_dias'
        ordering=['nombre']


class Dia(models.Model):
    fecha = models.DateField(verbose_name='Fecha', blank=False, null=False)
    fecha_invertida = models.CharField(max_length=8, verbose_name='Fecha YYYYMMDD', blank=False, null=False)
    tipo_dia= models.ForeignKey("TipoDia", verbose_name='Tipo de Día', on_delete=models.RESTRICT, null=False)

    def __str__(self):
        return self.fecha

    class Meta:
        verbose_name='Día'
        verbose_name_plural='Días'
        db_table='dias'
        ordering=['fecha_invertida']


# -----------------------------------------------------------------------------------------------
#      P R E S U P U E S T O S
# -----------------------------------------------------------------------------------------------

class Prestacion(models.Model):

    codigo = models.CharField(max_length=50)  # Código de la prestación
    descripcion = models.TextField(max_length=1000)  # Descripción de la prestación
    honorarios = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Honorarios
    ayudante = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Ayudante
    gastos = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Gastos
    anestesia = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Anestesia
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Total
    servicio = models.CharField(max_length=50) #Servicio
    practica = models.CharField(max_length=150, blank=True) #Practica
    activo = models.CharField(max_length=2, choices=ACTIVO_CHOICES, default="Si")
    
    def __str__(self):
        return f"{self.descripcion} (Código: {self.codigo})"
    
    class Meta:
        verbose_name='Prestación'
        verbose_name_plural='Prestaciones'
        db_table='prestaciones'
    
class Presupuesto(models.Model):
    numero = models.AutoField(primary_key=True)  # Número único de presupuesto
    cliente = models.CharField(max_length=255)  # Nombre del cliente
    documento = models.CharField(max_length=20)  # Documento del cliente
    fecha = models.DateField(auto_now_add=True)  # Fecha de creación del presupuesto
    creado_por = models.ForeignKey(User, verbose_name='Creado por', on_delete=models.RESTRICT, null=True, related_name='presupuestos_creados')
    eliminado_por = models.ForeignKey(User, verbose_name='Eliminado por', on_delete=models.RESTRICT, null=True, related_name='presupuestos_eliminados')
    activo = models.CharField(max_length=1, choices=OPCIONES_ACTIVO, default='s')

    def __str__(self):
        return f"Presupuesto #{self.numero} - {self.cliente}"
    
    class Meta:
        verbose_name='Presupuesto'
        verbose_name_plural='Presupuestos'
        db_table='presupuestos'    
    
class PresupuestoItem(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE)
    detalle = models.CharField(max_length=100, blank=True, default='')
    cantidad = models.PositiveIntegerField(default=0)  # Nueva cantidad
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    creado_por = models.ForeignKey(User, verbose_name='Creado por', on_delete=models.RESTRICT, null=True, related_name='presupuestos_items_creados')
    eliminado_por = models.ForeignKey(User, verbose_name='Eliminado por', on_delete=models.RESTRICT, null=True, related_name='presupuestos_items_eliminados')
    activo = models.CharField(max_length=1, choices=OPCIONES_ACTIVO, default='s')

    def __str__(self):
        return f"Presupuesto {self.presupuesto.numero} - Cantidad {self.cantidad}"
    
    class Meta:
        verbose_name='Presupuesto Item'
        verbose_name_plural='Presupuestos Items'
        db_table='presupuestos_items' 
    
class PresupuestoPrestacion(models.Model):
    presupuesto = models.ForeignKey(Presupuesto, on_delete=models.CASCADE, related_name='prestaciones')
    prestacion = models.ForeignKey(Prestacion, on_delete=models.CASCADE)
    item = models.ForeignKey(PresupuestoItem, on_delete=models.CASCADE)
    
    def calcular_total(self):
        if self.item and self.prestacion:
            return self.item.cantidad * self.prestacion.total
        return 0
    
    def __str__(self):
        return f"Presupuesto {self.presupuesto.numero} - Prestacion {self.prestacion.codigo}"
    
    class Meta:
        verbose_name='Presupuesto Prestación'
        verbose_name_plural='Presupuestos Prestaciones'
        db_table='presupuestos_prestaciones'    


