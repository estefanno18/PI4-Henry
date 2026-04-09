"""Parser de imágenes de contratos usando GPT-4o Vision."""

import base64
import os

import openai

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}

VISION_PROMPT = (
    "Eres un extractor de texto especializado en documentos legales. "
    "Extrae el texto completo del contrato presente en esta imagen de forma fiel y precisa. "
    "Debes respetar estrictamente:\n"
    "- La jerarquía de secciones y subsecciones del documento\n"
    "- La numeración de cláusulas tal como aparece en el original\n"
    "- La estructura y formato del documento (títulos, párrafos, listas)\n"
    "- Todo el contenido textual sin omitir ni alterar ninguna parte\n\n"
    "Devuelve únicamente el texto extraído, sin comentarios ni explicaciones adicionales."
)


def parse_contract_image(image_path: str) -> str:
    """
    Extrae texto de una imagen de contrato usando GPT-4o Vision.

    Args:
        image_path: Ruta al archivo de imagen (JPEG/PNG).

    Returns:
        Texto extraído preservando estructura del documento.

    Raises:
        FileNotFoundError: Si la imagen no existe.
        ValueError: Si el formato no es JPEG/PNG.
        RuntimeError: Si la API retorna un error.
    """
    # Validar existencia del archivo
    if not os.path.isfile(image_path):
        raise FileNotFoundError(
            f"El archivo '{image_path}' no existe o no es un archivo válido."
        )

    # Validar extensión
    _, ext = os.path.splitext(image_path)
    ext_lower = ext.lower()
    if ext_lower not in VALID_EXTENSIONS:
        raise ValueError(
            f"Formato no soportado para '{image_path}': se recibió '{ext}'. "
            f"Formatos válidos: {', '.join(sorted(VALID_EXTENSIONS))}"
        )

    # Leer y codificar imagen en base64
    with open(image_path, "rb") as f:
        image_data = f.read()
    b64_image = base64.b64encode(image_data).decode("utf-8")

    # Determinar media type
    media_type = "image/jpeg" if ext_lower in {".jpg", ".jpeg"} else "image/png"

    # Invocar API de GPT-4o Vision
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{b64_image}"
                            },
                        },
                    ],
                }
            ],
        )
        return response.choices[0].message.content

    except openai.APITimeoutError as e:
        raise RuntimeError(
            f"Timeout al procesar la imagen '{image_path}': "
            f"la operación de extracción de texto excedió el tiempo de espera. {e}"
        ) from e

    except openai.BadRequestError as e:
        error_msg = str(e).lower()
        if "token" in error_msg or "maximum context length" in error_msg:
            raise RuntimeError(
                f"El documento '{image_path}' excede la capacidad de procesamiento: "
                f"se ha superado el límite de tokens permitido."
            ) from e
        raise RuntimeError(
            f"Error en la solicitud a la API para '{image_path}': {e}"
        ) from e

    except openai.AuthenticationError as e:
        raise RuntimeError(
            "Error de autenticación: la OPENAI_API_KEY no es válida "
            f"o no está configurada correctamente. {e}"
        ) from e

    except openai.RateLimitError as e:
        raise RuntimeError(
            "Se ha excedido el límite de solicitudes a la API de OpenAI. "
            f"Intente nuevamente más tarde. {e}"
        ) from e

    except openai.APIError as e:
        raise RuntimeError(
            f"Error en la API de OpenAI al procesar '{image_path}': {e}"
        ) from e
