"""
Inventarios Equipos, formularios
"""

from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from lib.safe_string import DIRECCION_IP_REGEXP, MAC_ADDRESS_REGEXP
from hercules.blueprints.inv_equipos.models import InvEquipo
from hercules.blueprints.inv_redes.models import InvRed


class InvEquipoForm(FlaskForm):
    """Formulario InvEquipo"""

    inv_modelo = SelectField("Marca - Modelo", coerce=int, validators=[DataRequired()], validate_choice=False)
    descripcion = StringField("Descripción", validators=[DataRequired(), Length(max=512)])
    tipo = SelectField("Tipo de equipo", choices=InvEquipo.TIPOS.items(), validators=[DataRequired()])
    fecha_fabricacion = DateField("Fecha de fabricación", validators=[Optional()])
    numero_serie = StringField("Número de serie", validators=[Optional()])
    numero_inventario = IntegerField("Número de inventario", validators=[Optional()])
    inv_red = SelectField("Red", coerce=int, validators=[DataRequired()])
    direccion_ip = StringField("Dirección IP", validators=[Optional(), Regexp(DIRECCION_IP_REGEXP)])
    direccion_mac = StringField("Dirección MAC", validators=[Optional(), Regexp(MAC_ADDRESS_REGEXP)])
    numero_nodo = IntegerField("Número de nodo", validators=[Optional()])
    numero_switch = IntegerField("Número de switch", validators=[Optional()])
    numero_puerto = IntegerField("Número de puerto", validators=[Optional()])
    guardar = SubmitField("Guardar")

    def __init__(self, *args, **kwargs):
        """Inicializar y cargar opciones de inv_red"""
        super().__init__(*args, **kwargs)
        self.inv_red.choices = [
            (r.id, f"{r.nombre} ({r.tipo})") for r in InvRed.query.filter_by(estatus="A").order_by(InvRed.nombre).all()
        ]