from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional
from zoneinfo import ZoneInfo
from pydantic import BaseModel, EmailStr, condecimal
from sqlmodel import DECIMAL, SQLModel, Field
from app.db import engine
from typing import List
from sqlmodel import SQLModel, Field
from typing import Optional

Decimal_7_5 = condecimal(max_digits=15, decimal_places=5)
# Una buena práctica en arquitecturas limpias es usar ORM para la capa de acceso a datos y DTO
# para la comunicación con la API, evitando exponer modelos de la base de datos directamente. 🚀
def mexico_timestamp():
    return datetime.now(ZoneInfo("America/Mexico_City"))
# MODELOS OFICIALES
class TipoFinEnum(str, Enum):
    LIGA = "L"
    MAIL = "M"

class FinancierasDTO(SQLModel):
    id: int = Field(primary_key=True)
    nombre: str = Field(default=None)
    tipo: str = Field(min_length=1, max_length=1)
    fase: int = Field(default=None)
    liga_carpeta: str = Field(default=None)
    url: str = Field (default=None)
    img: str = Field (default=None)


class Financieras(FinancierasDTO,table=True):
        pass
        id: int | None = Field(default=None,primary_key=True)

class Categorias(SQLModel):
    id: int = Field(primary_key=True)
    nombre: str = Field(default=None)

class SubCategorias(SQLModel):
    __tablename__ = "subCategorias"
    id: int = Field(primary_key=True)
    nombre: str = Field(default=None)

class ProductosDTO(SQLModel):
    nombre: str = Field(default=None)
    checklist: str = Field(default=None)
    ch_viabilidad: str = Field(default=None)
    institucion_id: int = Field(foreign_key="financiera.id")
    id_categoria: int = Field(foreign_key="categorias.id")
    id_subCategoria: int = Field(foreign_key="subCategorias.id")


 
class ProductoFormatoTipoPersona(SQLModel, table=True):
    __tablename__ = "producto_formato_tipo_persona"
    id: int | None = Field(default=None, primary_key=True)  
    producto_id: int = Field(foreign_key="producto.id")
    formato_id: int = Field(foreign_key="formato.id")
    tipo_persona: str = Field(primary_key=True)

class UsuarioDTO(BaseModel):
    nombre: str
    email: str
    rol: str
    membresia: Optional[int] = None
    id_broker: Optional[int] = None
    id_sede: Optional[int] = None
    celular: Optional[str] = None
    nivel: Optional[int] = None
    id_financiera: Optional[int] = None
    id_superior: Optional[int] = None   # ← AHORA SÍ SE MANDA
    

class Usuarios(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str
    rol: str
    membresia: Optional[int] = Field(default=None, foreign_key="membresias.id")
    id_broker: Optional[int] = Field(default=None, foreign_key="brokers.id")
    id_sede: Optional[int] = Field(default=None, foreign_key="sedes.id")
    celular: Optional[str] = None
    nivel: Optional[int] = None
    id_financiera: Optional[int] = Field(default=None, foreign_key="financieras.id")
    id_superior: Optional[int] = Field(default=None, foreign_key="usuarios.id")
    created_at: datetime = Field(
    default_factory=lambda: datetime.now(ZoneInfo("America/Mexico_City"))
    )
    comisiones: str 

class UsuarioSimple(BaseModel):
    id: int
    nombre: str
    
class UsuarioResponse(SQLModel):
    id: int
    nombre: str
    email: str
    rol: str
    membresia: Optional[int]
    id_broker: Optional[int]
    id_sede: Optional[int]
    celular: Optional[str]
    nivel: Optional[int]
    id_financiera: Optional[int]
    id_superior: Optional[int]
    created_at: Optional[datetime]
    



class Formatos (SQLModel, table=True):
    id: int = Field(primary_key=True)
    nombre: str = Field(default=None)
    financiera_id: int = Field(foreign_key="financiera.id")

class Producto_formato(SQLModel, table=True):
    producto_id: int = Field(foreign_key="producto.id", primary_key=True)
    formato_id: int = Field(foreign_key="formato.id", primary_key=True)  

class Estatus_tramites(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(default=None)

class Documentos(SQLModel, table=True):
    id: int = Field(primary_key=True)
    id_producto: int = Field(foreign_key="producto.id")
    tipo_persona: str
    nombre: str
    desc: str
    responsable: str

class Viabilidad(SQLModel, table=True):
    id: int = Field(primary_key=True)
    id_producto: int = Field(foreign_key="producto.id")  # ← ya NO lleva primary_key=True
    tipo_persona: str
    nombre: str   
    desc: str
    responsable: str

class CotizacionDTO (SQLModel):
    id_usuario: str = Field(max_length=100, nullable=False)
    id_user: int = Field(nullable=False) 
    id_financiera: int = Field(nullable=False)
    producto: int = Field(nullable=False)
    tipo_persona: str = Field(nullable=False)  
    nombre: str = Field(max_length=100, nullable=False)
    rfc: str = Field(max_length=100, nullable=False)
    plazo: str = Field(max_length=100, nullable=False)
    edad: int = Field(nullable=False)
    monto: int = Field(nullable=False)  
    ingresos: int = Field(nullable=False)
    estatus: int = Field(nullable=False) 
    antiguedad_empresa: int = Field(nullable=False)
    OpCliente: str = Field(max_length=250, nullable=False)
    broker: int = Field(default=None, nullable=True)
    sede: Optional[int] = Field(default=None, nullable=True) # aun no se recibe del front
    destinoCredito: str = Field(max_length=250, nullable=False)
    custom_prod: Optional[str] = Field(default=None, nullable=True)
    fecha_pago: Optional[date] = Field(default=None)




class Cotizacion (CotizacionDTO, table=True ):   
    pass 
    timestamp: datetime | None = Field(default_factory=mexico_timestamp, nullable=False)
    id_cotizacion: int | None = Field(default=None, primary_key=True, nullable=False)
    id_user: int = Field(foreign_key="usuarios.id", nullable=False)
    fecha_pago: Optional[date] = Field(default=None)


class ComentariosDTO(SQLModel):
    id_cotizacion: int = Field(default=None)
    id_usuario: str = Field(default=None)
    comentarios: str = Field(default=None)

class FechaPagoDTO(BaseModel):
    id_cotizacion: int
    fecha_pago: date

class CorreosPagos(SQLModel, table=True):
    __tablename__ = "correos_pagos"

    id: Optional[int] = Field(default=None, primary_key=True)
    id_financiera: int = Field(foreign_key="financieras.id", index=True)

    nombre_contacto: str
    telefono: int
    correo: str    


class Comentarios(ComentariosDTO, table=True):
    pass
    id_comentario: Optional[int] | None = Field(primary_key=True)
    timestamp: datetime = Field(default_factory=mexico_timestamp, nullable=False)

class CorreosDTO(SQLModel):
    id_financiera: int = Field(default=None)
    correo: str = Field(default=None)
    nombre: str = Field(default=None)
    v_comercial: bool = Field(default=True) # vista comercial
    v_mail: bool = Field(default=True) # envio de correos
    telefono: str = Field(default=None)
    categoria_id: int = Field(foreign_key="categorias.id")

class Correos(CorreosDTO ,table=True ):  
    pass
    id_correo: int | None = Field(default=None, primary_key=True)

class ReqMail(BaseModel):
    isNew:  bool
    numCotizacion: int

class ReqMailComentarioDir(BaseModel):
    idCotizacion: int
    message: str

class BodyMail(BaseModel):
    OpCliente: str
    brokerName: str
    cliente: str
    emailUser: EmailStr
    ifName: str
    isNew:  bool
    listaMails: list[str]
    monto: str
    numCotizacion: int
    productoName: str
    rfc: str
    sedeName: str
    # update: int
    userName: str
    cotizacionB64: Optional[str] = None
    ingresos: str
    tipoPersona: str
    antiguedadEmpresa: int
    edad: int
    plazo: str
    celular: Optional[str] = None
    destinoCredito: str

class EstatusUpdate(BaseModel):
    estatus: int
    id_cotizacion: int

class MontoUpdate(BaseModel):
    monto: float
    id_cotizacion: int


class Sedes(SQLModel, table=True):
    id: int = Field(primary_key=True)
    nombre: str = Field(default=None)

class Tp_producto_checklist(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, nullable=False)
    producto_id: int = Field(foreign_key="productos.id")
    tipo_persona: str = Field(default=None)
    checklist: str = Field(default=None)
    ch_viabilidad: str = Field(default=None)

class ChecklistResponse(SQLModel):
    producto_id: int
    tipo_persona: str
    checklist: str
    ch_viabilidad: str
    id_categoria: int
    id_subCategoria: int

class MontoUpdateDTO(BaseModel):
    id_cotizacion: int
    monto: float

class Brokers(SQLModel, table=True):
    __tablename__ = "brokers"
    __table_args__ = {"extend_existing": True} 
    id: int = Field(default=None, primary_key=True)
    nombre: str

class Proceso(SQLModel, table=True):
    __tablename__ = "procesos"
    id: int = Field(default=None, primary_key=True)
    step: str
    descripcion: str
    id_financiera: int = Field(foreign_key="financieras.id")
    id_categoria: int = Field(foreign_key="categorias.id")
    id_subcategoria: int = Field(foreign_key="subCategorias.id")

class Membresias(SQLModel, table=True):
     id: int = Field(default=None, primary_key=True)
     nombre: str

class Utms(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    id_usuario: Optional[int] = Field(default=None, foreign_key="usuarios.id")
    id_financiera: int = Field(foreign_key="financieras.id")
    tipo_persona: Optional[str] = Field(default=None)
    url: str


class utils(BaseModel):
    numeros: List[int]


class ProductoParametros(SQLModel, table=True):
    __tablename__ = "producto_desc"

    id: int | None = Field(default=None, primary_key=True)
    id_producto: int = Field(foreign_key="productos.id")

    param: str
    value: str
    orden: int


class ParametroResponse(BaseModel):
    param: str
    value: str
    orden: int

    class Config:
        from_attributes = True

class ProductoResponse(BaseModel):
    id: int
    nombre: str
    parametros: list[ParametroResponse]

    class Config:
        from_attributes = True

class ProductosTipoPersonaDTO(ProductosDTO):
    id: int
    tipo_persona: List[str] = Field(default_factory=list)

class Productos(ProductosDTO, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plazo: Optional[str] = None


class Pagos(SQLModel, table=True):

    id: int = Field(primary_key=True)
    id_financiera: Optional[int] = Field(default=None, foreign_key="financieras.id")
    regla:  str

    id_producto: Optional[int] = Field(foreign_key="productos.id")
    m_max: Optional[int]
    m_min: Optional[int]

    pago_a_konnect: Decimal = Field (DECIMAL(7, 5), nullable=False)

    c_apertura: Decimal = Field (DECIMAL(7, 5), nullable=False)
    c_plata: Decimal = Field (DECIMAL(7, 5), nullable=False)
    c_oro: Decimal = Field (DECIMAL(7, 5), nullable=False)
    c_platino: Decimal = Field (DECIMAL(7, 5), nullable=False)
    c_diamante: Decimal = Field (DECIMAL(7, 5), nullable=False)

    notas: Optional[str] = Field(default=None, max_length=300)

    ganancia_plata: Decimal = Field (DECIMAL(7, 5), nullable=False)
    ganancia_oro: Decimal = Field (DECIMAL(7, 5), nullable=False)
    ganancia_platino: Decimal = Field (DECIMAL(7, 5), nullable=False)
    ganancia_diamante: Decimal = Field (DECIMAL(7, 5), nullable=False)
    ganancia_konnect: Decimal = Field (DECIMAL(7, 5), nullable=False)

class ResponsePagos(BaseModel):
    id_cotizacion: int
    id_financiera: int
    financiera: str
    regla: str
    id_producto: int
    producto: str
    membresia_broker: str
    nombre_usuario: str
    monto_credito: Decimal_7_5 # type: ignore
    
    comision_apertura_porcentaje: Optional[str] = None
    comision_apertura_pesos: Optional[str] = None
    
    porcentaje_pago_a_konnect: str
    pago_a_konnect: Decimal_7_5 # type: ignore
    iva_pago_a_konnect: Decimal_7_5 # type: ignore
    total_pago_a_konnect: Decimal_7_5 # type: ignore

    porcentaje_pago_broker: str
    pago_broker: Decimal_7_5 # type: ignore
    iva_pago_broker: Decimal_7_5 # type: ignore
    total_pago_broker: Decimal_7_5 # type: ignore
    
    ganancia_konnect: Decimal_7_5 # type: ignore
    iva_ganancia_konnect: Decimal_7_5 # type: ignore
    total_ganancia_konnect: Decimal_7_5 # type: ignore

    lineas_broker: Optional[int] | None = None
    lineas_konnect: Optional[int] | None = None