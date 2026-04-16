"""Pydantic schemas para a API ARIA."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class IncidentInput(BaseModel):
    """Payload de entrada para predicoes."""
    prio_num: int = Field(3, ge=1, le=5, description="Prioridade numerica (1-5)")
    hora_abertura: int = Field(10, ge=0, le=23)
    dia_semana: int = Field(0, ge=0, le=6, description="0=Seg, 6=Dom")
    mes: int = Field(6, ge=1, le=12)
    is_monitoring: int = Field(1, ge=0, le=1)
    has_parent: int = Field(0, ge=0, le=1)
    produto_enc: int = Field(0, ge=0)
    grupo_enc: int = Field(0, ge=0)
    categoria_enc: int = Field(0, ge=0)
    subcategoria_enc: int = Field(0, ge=0)
    cod_fechamento_enc: int = Field(0, ge=0)
    cod_fechamento: Optional[str] = None
    descricao: str = Field("Problem: Check Application Monitoring")

    # Campos opcionais para contexto / persistencia
    numero: Optional[str] = None
    produto: Optional[str] = None
    grupo: Optional[str] = None
    categoria: Optional[str] = None
    subcategoria: Optional[str] = None


class OLAPrediction(BaseModel):
    """Resultado da predicao de violacao OLA."""
    probabilidade: float
    percentual: str
    nivel_risco: str          # BAIXO / MEDIO / ALTO
    recomendacao: str
    numero: Optional[str] = None
    timestamp: datetime


class PriorityPrediction(BaseModel):
    """Resultado da predicao de prioridade."""
    prioridade_predita: int
    label: str
    numero: Optional[str] = None
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    version: str
    modelos_carregados: bool
    db_conectado: bool
