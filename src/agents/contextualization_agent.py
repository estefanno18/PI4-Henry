"""Agente de contextualización para análisis estructural de documentos legales."""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = (
    "Eres un analista estructural especializado en documentos legales. "
    "Tu rol exclusivo es analizar la estructura de un contrato original y su adenda "
    "para producir un mapa contextual comparativo.\n\n"
    "## Responsabilidades\n"
    "1. **Identificar secciones**: Enumera todas las secciones, cláusulas y bloques "
    "presentes en ambos documentos (contrato original y adenda).\n"
    "2. **Establecer correspondencias**: Para cada sección de la adenda, indica a qué "
    "sección del contrato original corresponde. Si una sección de la adenda no tiene "
    "correspondencia directa, indícalo explícitamente.\n"
    "3. **Describir propósitos**: Para cada sección o bloque identificado, describe "
    "brevemente su propósito general dentro del documento (por ejemplo: 'define las "
    "condiciones económicas', 'establece la vigencia del contrato').\n\n"
    "## Limitaciones estrictas\n"
    "- NO debes extraer ni describir cambios específicos entre los documentos.\n"
    "- NO debes comparar valores, montos, fechas ni contenido particular.\n"
    "- NO debes clasificar cambios como adiciones, eliminaciones o modificaciones.\n"
    "- Tu trabajo es ÚNICAMENTE mapear la estructura y correspondencias, NO analizar diferencias.\n\n"
    "## Formato de salida\n"
    "Produce un mapa contextual como texto estructurado que incluya:\n"
    "- Lista de secciones del contrato original con su propósito\n"
    "- Lista de secciones de la adenda con su propósito\n"
    "- Tabla o lista de correspondencias entre secciones de ambos documentos"
)

HUMAN_TEMPLATE = (
    "Analiza la estructura de los siguientes documentos y produce un mapa contextual.\n\n"
    "## Contrato Original\n{original_text}\n\n"
    "## Adenda\n{amendment_text}"
)


class ContextualizationAgent:
    """Agente LangChain para análisis estructural de documentos legales."""

    def __init__(self, model: str = "gpt-4o", temperature: float = 0.0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("human", HUMAN_TEMPLATE),
        ])
        self.chain = self.prompt | self.llm

    def run(self, original_text: str, amendment_text: str) -> str:
        """
        Produce un mapa contextual comparativo de ambos documentos.

        Args:
            original_text: Texto del contrato original.
            amendment_text: Texto de la adenda.

        Returns:
            Mapa contextual como texto estructurado.

        Raises:
            RuntimeError: Si ocurre un error durante la contextualización.
        """
        try:
            response = self.chain.invoke({
                "original_text": original_text,
                "amendment_text": amendment_text,
            })
            return response.content
        except Exception as e:
            raise RuntimeError(
                f"Error en la etapa de contextualización: {type(e).__name__} - {e}"
            ) from e
