# Contratos de Prueba — Contract Addendum Analyzer

Este directorio contiene pares de contratos de prueba diseñados para validar el pipeline de análisis de contratos y adendas. Cada par consiste en un contrato original y su adenda correspondiente en formato PNG.

> **Nota:** Los archivos PNG actuales son placeholders mínimos (1×1 pixel). Deben ser reemplazados con imágenes reales de contratos escaneados para ejecutar pruebas end-to-end con GPT-4o Vision. Puede regenerar los placeholders ejecutando `python data/test_contracts/generate_placeholders.py`.

---

## Par 1 — Cambios Simples: Contrato de Servicios

### Archivos

| Archivo | Descripción |
|---------|-------------|
| `par1_original.png` | Contrato de servicios profesionales original |
| `par1_adenda.png` | Adenda que modifica monto mensual y fecha de vencimiento |

### Contenido del Contrato Original (`par1_original.png`)

Contrato de prestación de servicios profesionales entre Empresa ABC S.A. y Consultoría XYZ Ltda. con las siguientes cláusulas principales:

- **Cláusula 1 — Objeto:** Prestación de servicios de consultoría tecnológica.
- **Cláusula 2 — Vigencia:** Del 1 de enero de 2024 al 31 de diciembre de 2024.
- **Cláusula 3 — Monto mensual:** $5,000 USD mensuales pagaderos los primeros 5 días de cada mes.
- **Cláusula 4 — Obligaciones del prestador:** Entrega de informes mensuales, disponibilidad de lunes a viernes.
- **Cláusula 5 — Terminación:** Cualquiera de las partes puede terminar con 30 días de preaviso.

### Contenido de la Adenda (`par1_adenda.png`)

Adenda al contrato de prestación de servicios profesionales que introduce las siguientes modificaciones:

- **Cláusula 3 — Monto mensual (MODIFICACIÓN):** Se modifica el monto mensual de **$5,000 USD** a **$7,500 USD**, efectivo a partir del 1 de julio de 2024.
- **Cláusula 2 — Vigencia (MODIFICACIÓN):** Se extiende la vigencia del contrato del **31 de diciembre de 2024** al **31 de diciembre de 2025**.

### Cambios Esperados

| # | Tipo | Sección | Detalle |
|---|------|---------|---------|
| 1 | Modificación | Cláusula 3 — Monto mensual | $5,000 USD → $7,500 USD |
| 2 | Modificación | Cláusula 2 — Vigencia | Dic 2024 → Dic 2025 |

### Resultado Esperado (`ContractChangeOutput`)

```json
{
  "sections_changed": [
    "Cláusula 3 - Monto mensual",
    "Cláusula 2 - Vigencia"
  ],
  "topics_touched": [
    "Condiciones económicas",
    "Plazo contractual"
  ],
  "summary_of_the_change": "La adenda modifica el monto mensual de $5,000 USD a $7,500 USD efectivo desde julio 2024, y extiende la vigencia del contrato de diciembre 2024 a diciembre 2025."
}
```

---

## Par 2 — Cambios Complejos: Contrato de Confidencialidad

### Archivos

| Archivo | Descripción |
|---------|-------------|
| `par2_original.png` | Contrato de confidencialidad (NDA) original |
| `par2_adenda.png` | Adenda que añade cláusula, modifica alcance y elimina restricción |

### Contenido del Contrato Original (`par2_original.png`)

Acuerdo de confidencialidad (NDA) entre TechCorp Internacional S.A. y DataSoft Solutions S.R.L. con las siguientes cláusulas principales:

- **Cláusula 1 — Definición de información confidencial:** Toda información técnica, comercial o financiera compartida entre las partes.
- **Cláusula 2 — Obligaciones de confidencialidad:** Las partes se comprometen a no divulgar información confidencial a terceros.
- **Cláusula 3 — Alcance territorial:** El acuerdo aplica exclusivamente dentro del territorio **nacional**.
- **Cláusula 4 — Restricciones de uso:** La información confidencial no podrá ser utilizada para desarrollar productos competidores ni compartida con filiales sin autorización escrita.
- **Cláusula 5 — Duración:** El acuerdo tiene vigencia de 3 años a partir de la firma.
- **Cláusula 6 — Penalidades:** Incumplimiento sujeto a penalidad de $50,000 USD y acciones legales.

### Contenido de la Adenda (`par2_adenda.png`)

Adenda al acuerdo de confidencialidad que introduce las siguientes modificaciones:

- **Cláusula 7 — Protección de datos personales (ADICIÓN):** Se añade nueva cláusula que establece que ambas partes cumplirán con las regulaciones de protección de datos personales aplicables (GDPR, LGPD, etc.), incluyendo la designación de un oficial de protección de datos y la notificación de brechas de seguridad en un plazo máximo de 72 horas.
- **Cláusula 3 — Alcance territorial (MODIFICACIÓN):** Se modifica el alcance territorial de **nacional** a **internacional**, incluyendo todas las jurisdicciones donde las partes tengan operaciones.
- **Cláusula 4 — Restricciones de uso (ELIMINACIÓN PARCIAL):** Se elimina la restricción de compartir información con filiales. La información confidencial ahora puede ser compartida con filiales previa notificación escrita. Se mantiene la restricción de no desarrollar productos competidores.

### Cambios Esperados

| # | Tipo | Sección | Detalle |
|---|------|---------|---------|
| 1 | Adición | Cláusula 7 — Protección de datos personales | Nueva cláusula sobre cumplimiento de regulaciones de protección de datos (GDPR, LGPD), oficial de protección de datos y notificación de brechas en 72h |
| 2 | Modificación | Cláusula 3 — Alcance territorial | Nacional → Internacional (todas las jurisdicciones con operaciones) |
| 3 | Eliminación | Cláusula 4 — Restricciones de uso | Se elimina la restricción de compartir con filiales (ahora permitido con notificación escrita) |

### Resultado Esperado (`ContractChangeOutput`)

```json
{
  "sections_changed": [
    "Cláusula 7 - Protección de datos personales",
    "Cláusula 3 - Alcance territorial",
    "Cláusula 4 - Restricciones de uso"
  ],
  "topics_touched": [
    "Protección de datos personales",
    "Alcance territorial",
    "Restricciones de uso",
    "Cumplimiento regulatorio"
  ],
  "summary_of_the_change": "La adenda introduce tres cambios: (1) añade una nueva Cláusula 7 sobre protección de datos personales que exige cumplimiento con GDPR/LGPD, designación de oficial de protección de datos y notificación de brechas en 72 horas; (2) modifica el alcance territorial de nacional a internacional, cubriendo todas las jurisdicciones donde las partes operan; (3) elimina la restricción de compartir información confidencial con filiales, permitiéndolo ahora con notificación escrita previa."
}
```

---

## Resumen de Escenarios de Prueba

| Par | Tipo de Contrato | Complejidad | Cambios | Tipos de Cambio |
|-----|-----------------|-------------|---------|-----------------|
| Par 1 | Servicios profesionales | Simple | 2 | 2 modificaciones |
| Par 2 | Confidencialidad (NDA) | Complejo | 3 | 1 adición, 1 modificación, 1 eliminación |

## Notas para Pruebas

- Los resultados esperados (`ContractChangeOutput`) son aproximados. El LLM puede producir variaciones en la redacción exacta, pero debe capturar la esencia de cada cambio.
- Para pruebas end-to-end, reemplace los placeholders PNG con imágenes escaneadas reales que contengan el texto descrito arriba.
- Los tests de humo (`test_smoke.py`) verifican que existen exactamente 2 pares de imágenes (4 archivos PNG) en este directorio.
- Los tests end-to-end verifican que el Par 1 identifica exactamente 2 modificaciones y el Par 2 identifica al menos 1 adición, 1 modificación y 1 eliminación.
