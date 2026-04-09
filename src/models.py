from pydantic import BaseModel


class ContractChangeOutput(BaseModel):
    """Modelo de salida validado del pipeline de análisis de contratos."""

    sections_changed: list[str]
    topics_touched: list[str]
    summary_of_the_change: str
