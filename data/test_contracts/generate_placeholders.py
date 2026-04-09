"""
Script para generar imágenes PNG placeholder de contratos de prueba.
Genera PNGs mínimos válidos (1x1 pixel blanco) como placeholders.
Estos archivos deben ser reemplazados con imágenes reales de contratos escaneados
para pruebas end-to-end con GPT-4o Vision.

Uso: python data/test_contracts/generate_placeholders.py
"""

import struct
import zlib
import os

def create_minimal_png(filepath: str) -> None:
    """Crea un archivo PNG mínimo válido (1x1 pixel blanco)."""
    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk: width=1, height=1, bit_depth=8, color_type=2 (RGB)
    ihdr_data = struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr_chunk = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)

    # IDAT chunk: single white pixel (filter byte 0 + RGB 255,255,255)
    raw_data = b'\x00\xff\xff\xff'
    compressed = zlib.compress(raw_data)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat_chunk = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)

    # IEND chunk
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)

    with open(filepath, 'wb') as f:
        f.write(signature + ihdr_chunk + idat_chunk + iend_chunk)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    files = [
        'par1_original.png',
        'par1_adenda.png',
        'par2_original.png',
        'par2_adenda.png',
    ]
    for filename in files:
        filepath = os.path.join(script_dir, filename)
        create_minimal_png(filepath)
        print(f"Creado: {filepath}")
    print("\nNota: Estos son placeholders de 1x1 pixel.")
    print("Reemplácelos con imágenes reales de contratos escaneados para pruebas E2E.")


if __name__ == '__main__':
    main()
