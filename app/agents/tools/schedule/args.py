from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


EventStatus = Literal["ACTIVE", "CANCELLED"]


def _validate_timezone(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} deve incluir o fuso horário.")


class AddEventArgs(BaseModel):
    title: str = Field(..., min_length=1, description="Título do evento.")
    start_time: datetime = Field(..., description="Início do evento em ISO 8601 com fuso horário.")
    source_text: str = Field(..., min_length=1, description="Texto original do usuário.")
    end_time: Optional[datetime] = Field(default=None, description="Fim do evento em ISO 8601 com fuso horário.")
    location: Optional[str] = Field(default=None, description="Local do evento.")
    notes: Optional[str] = Field(default=None, description="Observações adicionais.")

    @model_validator(mode="after")
    def validate_interval(self):
        _validate_timezone(self.start_time, "start_time")
        if self.end_time is not None:
            _validate_timezone(self.end_time, "end_time")
            if self.end_time <= self.start_time:
                raise ValueError("end_time deve ser posterior a start_time.")
        return self


class ListEventsArgs(BaseModel):
    event_id: Optional[int] = Field(default=None, gt=0, description="ID do evento.")
    search: Optional[str] = Field(default=None, description="Texto no título, local, observações ou texto original.")
    start_from: Optional[datetime] = Field(default=None, description="Início mínimo em ISO 8601 com fuso horário.")
    start_until: Optional[datetime] = Field(default=None, description="Início máximo em ISO 8601 com fuso horário.")
    status: Optional[EventStatus] = Field(default="ACTIVE", description="Estado do evento.")
    limit: int = Field(default=20, ge=1, le=100, description="Número máximo de eventos.")

    @model_validator(mode="after")
    def validate_period(self):
        for field_name in ("start_from", "start_until"):
            value = getattr(self, field_name)
            if value is not None:
                _validate_timezone(value, field_name)
        if self.start_from and self.start_until and self.start_until <= self.start_from:
            raise ValueError("start_until deve ser posterior a start_from.")
        return self


class CheckAvailabilityArgs(BaseModel):
    start_time: datetime = Field(..., description="Início da janela em ISO 8601 com fuso horário.")
    end_time: datetime = Field(..., description="Fim da janela em ISO 8601 com fuso horário.")

    @model_validator(mode="after")
    def validate_interval(self):
        _validate_timezone(self.start_time, "start_time")
        _validate_timezone(self.end_time, "end_time")
        if self.end_time <= self.start_time:
            raise ValueError("end_time deve ser posterior a start_time.")
        return self


class UpdateEventArgs(BaseModel):
    event_id: int = Field(..., gt=0, description="ID do evento.")
    title: Optional[str] = Field(default=None, min_length=1, description="Novo título.")
    start_time: Optional[datetime] = Field(default=None, description="Novo início em ISO 8601 com fuso horário.")
    end_time: Optional[datetime] = Field(default=None, description="Novo fim em ISO 8601 com fuso horário.")
    location: Optional[str] = Field(default=None, description="Novo local.")
    notes: Optional[str] = Field(default=None, description="Novas observações.")

    @model_validator(mode="after")
    def validate_update(self):
        values = (self.title, self.start_time, self.end_time, self.location, self.notes)
        if all(value is None for value in values):
            raise ValueError("Informe pelo menos um campo para atualização.")
        for field_name in ("start_time", "end_time"):
            value = getattr(self, field_name)
            if value is not None:
                _validate_timezone(value, field_name)
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValueError("end_time deve ser posterior a start_time.")
        return self


class CancelEventArgs(BaseModel):
    event_id: int = Field(..., gt=0, description="ID do evento a cancelar.")
