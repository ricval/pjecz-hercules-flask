"""
Funcionarios

- asignar_oficinas: Asignar funcionarios_oficinas a partir de una direccion
- limpiar_oficinas: Limpiar funcionarios_oficinas
- enviar_reporte: Enviar via correo electronico el reporte de funcionarios
- sincronizar: Sincronizar funcionarios con la API de RRHH Personal
"""

import click

from hercules.app import create_app
from hercules.blueprints.domicilios.models import Domicilio
from hercules.blueprints.funcionarios.models import Funcionario
from hercules.extensions import database

app = create_app()
database.app = app


@click.group()
def cli():
    """Funcionarios"""


@click.command()
@click.argument("curp", type=str)
@click.argument("domicilio_id", type=int)
def asignar_oficinas(curp, domicilio_id):
    """Asignar funcionarios_oficinas a partir de una direccion"""
    # Validar funcionario
    funcionario = Funcionario.query.filter_by(curp=curp).first()
    if funcionario is None:
        click.echo(f"No se encuentra al funcionario con CURP {curp}")
        return
    # Validar domicilio
    domicilio = Domicilio.query.get(domicilio_id)
    if domicilio is None:
        click.echo(f"No se encuentra el domicilio con ID {domicilio_id}")
        return
    # Poner tarea en el fondo
    app.task_queue.enqueue(
        "hercules.blueprints.funcionarios.tasks.asignar_oficinas",
        funcionario_id=funcionario.id,
        domicilio_id=domicilio.id,
    )
    click.echo("Asignar oficinas se está ejecutando en el fondo.")


@click.command()
@click.argument("curp", type=str)
def limpiar_oficinas(curp):
    """Limpiar funcionarios_oficinas"""
    funcionario = Funcionario.query.filter_by(curp=curp).first()
    if funcionario is None:
        click.echo(f"No se encuentra al funcionario con CURP {curp}")
        return
    app.task_queue.enqueue(
        "hercules.blueprints.funcionarios.tasks.limpiar_oficinas",
        funcionario_id=funcionario.id,
    )
    click.echo("Limpiar oficinas se está ejecutando en el fondo.")


@click.command()
def enviar_reporte():
    """Enviar via correo electronico el reporte"""
    app.task_queue.enqueue("hercules.blueprints.funcionarios.tasks.enviar_reporte")
    click.echo("Enviar reporte se está ejecutando en el fondo.")


@click.command()
def sincronizar():
    """Sincronizar con RRHH Personal"""
    app.task_queue.enqueue("hercules.blueprints.funcionarios.tasks.sincronizar")
    click.echo("Sincronizar se está ejecutando en el fondo.")


cli.add_command(asignar_oficinas)
cli.add_command(limpiar_oficinas)
cli.add_command(enviar_reporte)
cli.add_command(sincronizar)
