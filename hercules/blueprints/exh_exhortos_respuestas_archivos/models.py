"""
Exh Exhortos Respuestas Archivos, modelos
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now

from hercules.extensions import database
from lib.universal_mixin import UniversalMixin


class ExhExhortoRespuestaArchivo(database.Model, UniversalMixin):
    """ExhExhortoRespuestaArchivo"""

    ESTADOS = {
        "CANCELADO": "Cancelado",
        "PENDIENTE": "Pendiente",
        "ENVIADO": "Enviado",
        "RECIBIDO": "Recibido",
    }

    TIPOS_DOCUMENTOS = {
        1: "Oficio",
        2: "Acuerdo",
        3: "Anexo",
    }

    # Nombre de la tabla
    __tablename__ = "exh_exhortos_respuestas_archivos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    exh_exhorto_respuesta_id: Mapped[int] = mapped_column(ForeignKey("exh_exhortos_respuestas.id"))
    exh_exhorto_respuesta: Mapped["ExhExhortoRespuesta"] = relationship(back_populates="exh_exhortos_respuestas_archivos")

    # Nombre del archivo, como se enviará. Este debe incluir el la extensión del archivo.
    nombre_archivo: Mapped[str] = mapped_column(String(256))

    # Hash SHA1 en hexadecimal que corresponde al archivo a recibir. Esto para comprobar la integridad del archivo. Opcional.
    hash_sha1: Mapped[Optional[str]] = mapped_column(String(256))

    # Hash SHA256 en hexadecimal que corresponde al archivo a recibir. Esto para comprobar la integridad del archivo. Opcional.
    hash_sha256: Mapped[Optional[str]] = mapped_column(String(256))

    # Identificador del tipo de documento que representa el archivo:
    # 1 = Oficio
    # 2 = Acuerdo
    # 3 = Anexo
    tipo_documento: Mapped[int]

    # Estado de recepción del documento
    estado: Mapped[str] = mapped_column(
        Enum(*ESTADOS, name="exh_exhortos_respuestas_archivos_estados", native_enum=False), index=True
    )

    # URL del archivo en Google Storage. Opcional para guardar, obtener el ID, y crear la ruta con ese ID hasheado.
    url: Mapped[Optional[str]] = mapped_column(String(512))

    # Tamaño del archivo recibido en bytes
    tamano: Mapped[Optional[int]]

    # Fecha y hora de recepción del documento
    fecha_hora_recepcion: Mapped[datetime] = mapped_column(default=now())

    @property
    def tipo_documento_descripcion(self):
        """Descripción del tipo de documento"""
        try:
            return self.TIPOS_DOCUMENTOS[self.tipo_documento]
        except KeyError:
            return "Desconocido"

    def __repr__(self):
        """Representación"""
        return f"<ExhExhortoRespuestaArchivo {self.id}>"
