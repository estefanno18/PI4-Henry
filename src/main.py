"""Punto de entrada CLI y orquestación del pipeline de análisis de contratos."""

import argparse
import sys
import time

from dotenv import load_dotenv
from langfuse import Langfuse
import os

from src.image_parser import parse_contract_image
from src.agents.contextualization_agent import ContextualizationAgent
from src.agents.extraction_agent import ExtractionAgent
from src.models import ContractChangeOutput

REQUIRED_ENV_VARS = [
    "OPENAI_API_KEY",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
    "LANGFUSE_HOST",
]


def validate_env_vars() -> None:
    """
    Verifica que todas las variables de entorno requeridas estén configuradas.

    Raises:
        EnvironmentError: Si falta al menos una variable, listando las faltantes.
    """
    missing = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing:
        raise EnvironmentError(
            f"Variables de entorno faltantes: {', '.join(missing)}"
        )


def _truncate(text: str, max_len: int = 500) -> str:
    """Trunca texto para registro en Langfuse."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def main(original_path: str, amendment_path: str) -> ContractChangeOutput:
    """
    Ejecuta el pipeline completo de análisis de contratos.

    Args:
        original_path: Ruta a la imagen del contrato original (JPEG/PNG).
        amendment_path: Ruta a la imagen de la adenda (JPEG/PNG).

    Returns:
        ContractChangeOutput validado con los cambios identificados.

    Raises:
        EnvironmentError: Si faltan variables de entorno requeridas.
        FileNotFoundError: Si alguna ruta no existe.
        ValueError: Si el formato de imagen no es soportado.
        RuntimeError: Si falla alguna etapa del pipeline.
    """
    # 1. Cargar variables de entorno
    load_dotenv()

    # 2. Validar variables de entorno
    try:
        validate_env_vars()
    except EnvironmentError:
        raise

    # 3. Inicializar Langfuse y crear traza raíz
    langfuse = Langfuse()
    trace = langfuse.trace(name="contract-analysis")

    try:
        # 4. Parsing del contrato original
        span_parse_original = trace.span(name="parse_original_contract")
        span_parse_original.update(input={"original_path": original_path})
        t0 = time.time()
        try:
            original_text = parse_contract_image(original_path)
            latency = time.time() - t0
            span_parse_original.update(
                output=_truncate(original_text),
                metadata={
                    "type": "image_parsing",
                    "size": len(original_text),
                    "status": "success",
                    "latency_seconds": round(latency, 3),
                },
            )
            span_parse_original.end()
        except Exception as e:
            latency = time.time() - t0
            span_parse_original.update(
                status_message=str(e),
                metadata={
                    "type": "image_parsing",
                    "status": "error",
                    "latency_seconds": round(latency, 3),
                    "error": str(e),
                },
                level="ERROR",
            )
            span_parse_original.end()
            raise RuntimeError(
                f"Error en etapa 'parsing contrato original' "
                f"(entrada: '{original_path}'): {e}"
            ) from e

        # 5. Parsing de la adenda
        span_parse_amendment = trace.span(name="parse_amendment_contract")
        span_parse_amendment.update(input={"amendment_path": amendment_path})
        t0 = time.time()
        try:
            amendment_text = parse_contract_image(amendment_path)
            latency = time.time() - t0
            span_parse_amendment.update(
                output=_truncate(amendment_text),
                metadata={
                    "type": "image_parsing",
                    "size": len(amendment_text),
                    "status": "success",
                    "latency_seconds": round(latency, 3),
                },
            )
            span_parse_amendment.end()
        except Exception as e:
            latency = time.time() - t0
            span_parse_amendment.update(
                status_message=str(e),
                metadata={
                    "type": "image_parsing",
                    "status": "error",
                    "latency_seconds": round(latency, 3),
                    "error": str(e),
                },
                level="ERROR",
            )
            span_parse_amendment.end()
            raise RuntimeError(
                f"Error en etapa 'parsing adenda' "
                f"(entrada: '{amendment_path}'): {e}"
            ) from e

        # 6. Agente de contextualización
        span_contextualization = trace.span(name="contextualization_agent")
        span_contextualization.update(
            input={
                "original_text": _truncate(original_text),
                "amendment_text": _truncate(amendment_text),
            }
        )
        t0 = time.time()
        try:
            contextualization_agent = ContextualizationAgent()
            contextual_map = contextualization_agent.run(original_text, amendment_text)
            latency = time.time() - t0
            span_contextualization.update(
                output=_truncate(contextual_map),
                metadata={
                    "type": "contextualization",
                    "size": len(contextual_map),
                    "status": "success",
                    "latency_seconds": round(latency, 3),
                },
            )
            span_contextualization.end()
        except Exception as e:
            latency = time.time() - t0
            span_contextualization.update(
                status_message=str(e),
                metadata={
                    "type": "contextualization",
                    "status": "error",
                    "latency_seconds": round(latency, 3),
                    "error": str(e),
                },
                level="ERROR",
            )
            span_contextualization.end()
            raise RuntimeError(
                f"Error en etapa 'contextualización' "
                f"(entrada: textos parseados): {e}"
            ) from e

        # 7. Agente de extracción
        span_extraction = trace.span(name="extraction_agent")
        span_extraction.update(
            input={
                "contextual_map": _truncate(contextual_map),
                "original_text": _truncate(original_text),
                "amendment_text": _truncate(amendment_text),
            }
        )
        t0 = time.time()
        try:
            extraction_agent = ExtractionAgent()
            changes_dict = extraction_agent.run(contextual_map, original_text, amendment_text)
            latency = time.time() - t0
            span_extraction.update(
                output=changes_dict,
                metadata={
                    "type": "extraction",
                    "status": "success",
                    "latency_seconds": round(latency, 3),
                },
            )
            span_extraction.end()
        except Exception as e:
            latency = time.time() - t0
            span_extraction.update(
                status_message=str(e),
                metadata={
                    "type": "extraction",
                    "status": "error",
                    "latency_seconds": round(latency, 3),
                    "error": str(e),
                },
                level="ERROR",
            )
            span_extraction.end()
            raise RuntimeError(
                f"Error en etapa 'extracción' "
                f"(entrada: mapa contextual + textos parseados): {e}"
            ) from e

        # 8. Validación Pydantic
        try:
            result = ContractChangeOutput.model_validate(changes_dict)
        except Exception as e:
            raise RuntimeError(
                f"Error en etapa 'validación Pydantic' "
                f"(entrada: salida del agente de extracción): {e}"
            ) from e

        # Pipeline exitoso
        trace.update(metadata={"status": "success"})
        return result

    except Exception:
        # Marcar traza raíz con error
        trace.update(metadata={"status": "error"})
        raise

    finally:
        langfuse.flush()


def cli() -> None:
    """Punto de entrada CLI que acepta dos argumentos posicionales."""
    parser = argparse.ArgumentParser(
        description="Analiza un contrato original y su adenda para identificar cambios legales."
    )
    parser.add_argument(
        "original_path",
        help="Ruta a la imagen del contrato original (JPEG/PNG)",
    )
    parser.add_argument(
        "amendment_path",
        help="Ruta a la imagen de la adenda (JPEG/PNG)",
    )
    args = parser.parse_args()

    try:
        result = main(args.original_path, args.amendment_path)
        print(result.model_dump_json(indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
