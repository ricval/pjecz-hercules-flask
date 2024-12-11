"""
Edictos, modelos
"""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from hercules.extensions import database
from lib.universal_mixin import UniversalMixin


class Edicto(database.Model, UniversalMixin):
    """Edicto"""

    # Nombre de la tabla
    __tablename__ = "edictos"

    # Clave primaria
    id: Mapped[int] = mapped_column(primary_key=True)

    # Clave foránea
    autoridad_id: Mapped[int] = mapped_column(ForeignKey("autoridades.id"))
    autoridad: Mapped["Autoridad"] = relationship(back_populates="edictos")

    # Columnas
    fecha: Mapped[date] = mapped_column(Date(), index=True)
    descripcion: Mapped[str] = mapped_column(String(256))
    expediente: Mapped[str] = mapped_column(String(16))
    numero_publicacion: Mapped[str] = mapped_column(String(16))
    archivo: Mapped[str] = mapped_column(String(256), default="", server_default="")
    url: Mapped[str] = mapped_column(String(512), default="", server_default="")
    acuse_num: Mapped[int] = mapped_column(default=0)
    edicto_id_original: Mapped[int] = mapped_column(default=0)
    es_declaracion_de_ausencia: Mapped[bool] = mapped_column(default=False)

    # Columnas para análisis de datos (data analytics)
    da_tiempo: Mapped[Optional[datetime]]
    da_contenido: Mapped[Optional[str]] = mapped_column(Text())
    da_modelo: Mapped[Optional[str]] = mapped_column(String(256))
    da_resumen: Mapped[Optional[str]] = mapped_column(String(1024))
    da_etiquetas: Mapped[Optional[str]] = mapped_column(String(256))

    # Hijos
    edictos_acuses: Mapped[List["EdictoAcuse"]] = relationship(back_populates="edicto")

    @property
    def descargar_url(self):
        """URL para descargar el archivo desde el sitio web"""
        if self.id:
            return f"https://www.pjecz.gob.mx/consultas/edictos/descargar/?id={self.id}"
        return ""

    def __repr__(self):
        """Representación"""
        return f"<Edicto {self.id}>"
