"""
Inventarios Custodias, vistas
"""

import json
from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from hercules.blueprints.bitacoras.models import Bitacora
from hercules.blueprints.inv_custodias.forms import InvCustodiaForm
from hercules.blueprints.inv_custodias.models import InvCustodia
from hercules.blueprints.modulos.models import Modulo
from hercules.blueprints.permisos.models import Permiso
from hercules.blueprints.usuarios.decorators import permission_required
from hercules.blueprints.usuarios.models import Usuario
from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_message, safe_string

MODULO = "INV CUSTODIAS"

inv_custodias = Blueprint("inv_custodias", __name__, template_folder="templates")


@inv_custodias.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@inv_custodias.route("/inv_custodias/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de InvCustodia"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = InvCustodia.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "inv_custodia_id" in request.form:
        try:
            consulta = consulta.filter_by(id=int(request.form["inv_custodia_id"]))
        except ValueError:
            pass
    else:
        if "usuario_id" in request.form:
            consulta = consulta.filter_by(usuario_id=request.form["usuario_id"])
        if "nombre_completo" in request.form:
            nombre_completo = safe_string(request.form["nombre_completo"])
            if nombre_completo != "":
                consulta = consulta.filter(InvCustodia.nombre_completo.contains(nombre_completo))
    # Ordenar y paginar
    registros = consulta.order_by(InvCustodia.id).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "detalle": {
                    "id": resultado.id,
                    "url": url_for("inv_custodias.detail", inv_custodia_id=resultado.id),
                },
                "nombre_completo": resultado.nombre_completo,
                "oficina_clave": resultado.usuario.oficina.clave,
                "fecha": resultado.fecha.strftime("%Y-%m-%d"),
                "equipos_cantidad": resultado.equipos_cantidad if resultado.equipos_cantidad != 0 else "-",
                "equipos_fotos_cantidad": resultado.equipos_fotos_cantidad if resultado.equipos_fotos_cantidad != 0 else "-",
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)


@inv_custodias.route("/inv_custodias")
def list_active():
    """Listado de InvCustodia activos"""
    return render_template(
        "inv_custodias/list.jinja2",
        filtros=json.dumps({"estatus": "A"}),
        titulo="Custodias",
        estatus="A",
    )


@inv_custodias.route("/inv_custodias/inactivos")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def list_inactive():
    """Listado de InvCustodia inactivos"""
    return render_template(
        "inv_custodias/list.jinja2",
        filtros=json.dumps({"estatus": "B"}),
        titulo="Custodias inactivos",
        estatus="B",
    )


@inv_custodias.route("/inv_custodias/<int:inv_custodia_id>")
def detail(inv_custodia_id):
    """Detalle de un InvCustodia"""
    inv_custodia = InvCustodia.query.get_or_404(inv_custodia_id)
    return render_template("inv_custodias/detail.jinja2", inv_custodia=inv_custodia)


@inv_custodias.route("/inv_custodias/nuevo")
@permission_required(MODULO, Permiso.CREAR)
def new():
    """Nueva Custodia 1. Elegir Usuario"""
    return render_template("inv_custodias/new_1_choose.jinja2")


@inv_custodias.route("/inv_custodias/nuevo/<int:usuario_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.CREAR)
def new_with_usuario_id(usuario_id):
    """Nueva Custodia 2. Crear"""
    # Consultar al usuario elegido
    usuario = Usuario.query.get_or_404(usuario_id)
    # Consultar las custodias que ya tenga el usuario
    tiene_inv_custodias = InvCustodia.query.filter_by(usuario_id=usuario.id, estatus="A").order_by(InvCustodia.id).count() > 0
    # Preparar el formulario
    form = InvCustodiaForm()
    if form.validate_on_submit():
        # Guardar
        inv_custodia = InvCustodia(
            usuario_id=usuario.id,
            fecha=form.fecha.data,
            curp=usuario.curp,
            nombre_completo=usuario.nombre,
            equipos_cantidad=0,
            equipos_fotos_cantidad=0,
        )
        inv_custodia.save()
        # Guardar bitácora
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Nueva InvCustodia {inv_custodia.id} de {usuario.email}"),
            url=url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id),
        )
        bitacora.save()
        # Entregar detalle
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    # Mostrar formulario con la fecha de hoy por defecto
    form.fecha.data = date.today()
    return render_template(
        "inv_custodias/new_2_create.jinja2",
        form=form,
        tiene_inv_custodias=tiene_inv_custodias,
        usuario=usuario,
    )


@inv_custodias.route("/inv_custodias/edicion/<int:inv_custodia_id>", methods=["GET", "POST"])
@permission_required(MODULO, Permiso.MODIFICAR)
def edit(inv_custodia_id):
    """Editar InvCustodia"""
    inv_custodia = InvCustodia.query.get_or_404(inv_custodia_id)
    form = InvCustodiaForm()
    if form.validate_on_submit():
        # Guardar
        inv_custodia.fecha = form.fecha.data
        inv_custodia.curp = inv_custodia.usuario.curp  # Actualizarlo desde su Usuario relacionado
        inv_custodia.nombre_completo = inv_custodia.usuario.nombre  # Actualizarlo desde su Usuario relacionado
        inv_custodia.save()
        # Guardar bitácora
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Editado InvCustodia {inv_custodia.id} de {inv_custodia.usuario.email}"),
            url=url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id),
        )
        bitacora.save()
        # Entregar detalle
        flash(bitacora.descripcion, "success")
        return redirect(bitacora.url)
    form.fecha.data = inv_custodia.fecha
    return render_template("inv_custodias/edit.jinja2", form=form, inv_custodia=inv_custodia)


@inv_custodias.route("/inv_custodias/eliminar/<int:inv_custodia_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def delete(inv_custodia_id):
    """Eliminar InvCustodia"""
    inv_custodia = InvCustodia.query.get_or_404(inv_custodia_id)
    if inv_custodia.estatus == "A":
        # Eliminar InvCustodia
        inv_custodia.delete()
        # Eliminar los InvEquipos de la InvCustodia
        for inv_equipo in inv_custodia.inv_equipos:
            inv_equipo.delete()
            # Eliminar los InvComponentes de cada InvEquipo
            for inv_componente in inv_equipo.inv_componentes:
                inv_componente.delete()
        # Agregar a la bitácora
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Eliminado InvCustodia {inv_custodia.id} de {inv_custodia.usuario.email}"),
            url=url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id))


@inv_custodias.route("/inv_custodias/recuperar/<int:inv_custodia_id>")
@permission_required(MODULO, Permiso.ADMINISTRAR)
def recover(inv_custodia_id):
    """Recuperar InvCustodia"""
    inv_custodia = InvCustodia.query.get_or_404(inv_custodia_id)
    if inv_custodia.estatus == "B":
        # Recuperar InvCustodia
        inv_custodia.recover()
        # Recuperar los InvEquipos de la InvCustodia
        for inv_equipo in inv_custodia.inv_equipos:
            inv_equipo.recover()
            # Recuperar los InvComponentes de cada InvEquipo
            for inv_componente in inv_equipo.inv_componentes:
                inv_componente.recover()
        bitacora = Bitacora(
            modulo=Modulo.query.filter_by(nombre=MODULO).first(),
            usuario=current_user,
            descripcion=safe_message(f"Recuperado InvCustodia {inv_custodia.id} de {inv_custodia.usuario.email}"),
            url=url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id),
        )
        bitacora.save()
        flash(bitacora.descripcion, "success")
    return redirect(url_for("inv_custodias.detail", inv_custodia_id=inv_custodia.id))