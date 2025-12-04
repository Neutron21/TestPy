from datetime import datetime
from enum import Enum
from typing import List, Optional
from zoneinfo import ZoneInfo
from pydantic import BaseModel, EmailStr, field_validator
from sqlmodel import SQLModel, Field, Relationship, Session, select
from app.db import engine
from pydantic import ConfigDict
from pydantic import BaseModel
from typing import List
from sqlmodel import SQLModel, Field
from typing import Optional



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
    # img: str = Field(default=None)

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

class ProductosTipoPersonaDTO(ProductosDTO):
    id: int
    tipo_persona: List[str] = Field(default_factory=list)

class Productos(ProductosDTO,table=True):
    pass
    id: int | None = Field(default=None, primary_key=True)  # Permite que la BD genere el ID
 
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
    membresia: Optional[int] = None
    id_broker: Optional[int] = Field(default=None, foreign_key="brokers.id")
    id_sede: Optional[int] = Field(default=None, foreign_key="sedes.id")
    celular: Optional[str] = None
    nivel: Optional[int] = None
    id_financiera: Optional[int] = Field(default=None, foreign_key="financieras.id")
    id_superior: Optional[int] = Field(default=None, foreign_key="usuarios.id")


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
    plazo: int = Field(nullable=False)
    edad: int = Field(nullable=False)
    monto: float = Field(nullable=False)  
    ingresos: float = Field(nullable=False)
    estatus: int = Field(nullable=False) 
    antiguedad_empresa: int = Field(nullable=False)
    OpCliente: str = Field(max_length=250, nullable=False)
    broker: int = Field(default=None, nullable=True)
    sede: Optional[int] = Field(default=None, nullable=True) # aun no se recibe del front
    destinoCredito: str = Field(max_length=250, nullable=False)
    custom_prod: Optional[str] = Field(default=None, nullable=True)

class Cotizacion (CotizacionDTO, table=True ):   
    pass 
    timestamp: datetime | None = Field(default_factory=mexico_timestamp, nullable=False)
    id_cotizacion: int | None = Field(default=None, primary_key=True, nullable=False)
    id_user: int = Field(foreign_key="usuarios.id", nullable=False)

class ComentariosDTO(SQLModel):
    id_cotizacion: int = Field(default=None)
    id_usuario: str = Field(default=None)
    comentarios: str = Field(default=None)


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
    producto: str
    userName: str
    numCotizacion: int

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
    plazo: int
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

# MODELOS DE EJEMPLO
class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class CustomerPlan(SQLModel, table=True):
    id: int = Field(primary_key=True)
    plan_id: int = Field(foreign_key="plan.id")
    customer_id: int = Field(foreign_key="customer.id")
    status: StatusEnum = Field(default=StatusEnum.ACTIVE)

class Plan(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    name: str = Field(default=None)
    price: int = Field(default=None)
    descripcion: str = Field(default=None)
    customers: list['Customer'] = Relationship( # Custome aun no esta definido en esta linea, por ese se usan comillas
    back_populates="plans", link_model=CustomerPlan
    )

class CustomerBase(SQLModel):
    name: str = Field(default=None)
    description: str | None = Field(default=None)
    email: EmailStr = Field(default=None)
    age: int = Field(default=None)

    @field_validator("email")
    @classmethod # field_validator necesita ser un classmethod
    def validate_email(cls, value):
        session = Session(engine)
        query = select(Customer).where(Customer.email == value)
        result = session.exec(query).first()
        if result:
            raise ValueError("Este correo ya esta registrado")
        return value

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(CustomerBase):
    pass

class Customer(CustomerBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    transactions: list["Transaction"] = Relationship(back_populates="customer")
    plans: list[Plan] = Relationship(
        back_populates="customers", link_model=CustomerPlan
    )

class TransactionBase(SQLModel):
    ammount: int
    description: str

class Transaction(TransactionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id")
    customer: Customer = Relationship(back_populates="transactions")

class TransactionCreate(TransactionBase):
    customer_id: int = Field(foreign_key="customer.id")

class Invoice(BaseModel):
    id: int
    customer: Customer
    transactions: list[Transaction] # Como Transaction ya existe a esta altura se puede usar sin comillas
    total: int

    @property
    def ammount_total(self):
        return sum(transaction.ammount for transaction in self.transactions)
    
class PaginatedTransactionsResponse(SQLModel):
    total_count: int  # Total de elementos
    total_pages: int   # Total de páginas
    current_page: int  # Página actual
    limit: int         # Límite de elementos por página
    transactions: list[Transaction] 

class utils(BaseModel):
    numeros: List[int]

