"""Agente de extracción para identificación y clasificación de cambios legales."""

import json

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = (
    "Eres un extractor especializado en cambios legales. "
    "Tu rol exclusivo es identificar, clasificar y describir cada cambio "
    "introducido por una adenda respecto al contrato original.\n\n"
    "## Responsabilidades\n"
    "1. **Identificar cada cambio**: Compara el contrato original con la adenda "
    "usando el mapa contextual proporcionado para localizar todas las diferencias.\n"
    "2. **Clasificar cada cambio**: Clasifica cada cambio como:\n"
    '   - "adición": nueva cláusula o sección que no existía en el contrato original.\n'
    '   - "eliminación": cláusula o sección del contrato original que fue removida por la adenda.\n'
    '   - "modificación": cláusula o sección existente cuyo contenido fue alterado por la adenda.\n'
    "3. **Describir cada cambio**: Para cada cambio, indica la sección afectada, "
    "el contenido original (si aplica) y el contenido nuevo (si aplica).\n\n"
    "## Formato de salida\n"
    "Debes responder ÚNICAMENTE con un JSON válido (sin texto adicional) con la siguiente estructura:\n"
    "{{\n"
    '  "sections_changed": ["lista de identificadores de secciones modificadas, añadidas o eliminadas"],\n'
    '  "topics_touched": ["lista de categorías legales o comerciales afectadas por los cambios"],\n'
    '  "summary_of_the_change": "descripción detallada en lenguaje natural de todos los cambios identificados, '
    "incluyendo para cada uno su clasificación (adición/eliminación/modificación), "
    'la sección afectada, el contenido original y el contenido nuevo"\n'
    "}}\n\n"
    "## Reglas\n"
    "- Responde SOLO con el JSON, sin explicaciones ni texto adicional.\n"
    "- Asegúrate de que el JSON sea válido y parseable.\n"
    "- Incluye TODOS los cambios identificados, sin omitir ninguno.\n"
    "- Sé preciso y específico en las descripciones."
)

HUMAN_TEMPLATE = (
    "Analiza los siguientes documentos y extrae todos los cambios introducidos por la adenda.\n\n"
    "## Mapa Contextual\n{contextual_map}\n\n"
    "## Contrato Original\n{original_text}\n\n"
    "## Adenda\n{amendment_text}"
)


class ExtractionAgent:
    """Agente LangChain para extracción de cambios legales."""

    def __init__(self, model: str = "gpt-4o", temperature: float = 0.0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_TEMPLATE),
        ])
        self.chain = self.prompt | self.llm

    def run(self, contextual_map: str, original_text: str, amendment_text: str) -> dict:
        """
        Identifica y describe cambios entre contrato y adenda.

        Args:
            contextual_map: Mapa contextual del ContextualizationAgent.
            original_text: Texto del contrato original.
            amendment_text: Texto de la adenda.

        Returns:
            Dict con estructura ContractChangeOutput (sections_changed,
            topics_touched, summary_of_the_change).

        Raises:
            RuntimeError: Si ocurre un error durante la extracción.
        """
        try:
            response = self.chain.invoke({
                "contextual_map": contextual_map,
                "original_text": original_text,
                "amendment_text": amendment_text,
            })
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"Error en la etapa de extracción: el LLM no retornó JSON válido - {e}"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Error en la etapa de extracción: {type(e).__name__} - {e}"
            ) from e
