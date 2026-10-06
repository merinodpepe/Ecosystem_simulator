# Guía para Agentes de IA - Vault Ecosystem

Este documento proporciona instrucciones claras para cualquier agente de IA que interactúe con el proyecto **ecosystem_simulator** y su vault de Obsidian llamado **ecosystem**.

## Ubicación del Vault
El vault se encuentra en la carpeta:
```
/home/pepe/proyectos/ecosystem_simulator/ecosystem/
```

## Estructura del Vault
Dentro del vault, mantenga la siguiente organización:
- `ecosystem/wiki/` → Contiene explicaciones, documentación y notas descriptivas.
- `ecosystem/data/` → Contiene los datos brutos, procesados o cualquier archivo de información del proyecto.

## Qué Guardar
Cada vez que un agente realice una acción relevante (por ejemplo, generar un informe, procesar datos, crear un modelo, etc.) debe:
1. **Guardar el resultado** en la ubicación adecuada dentro del vault.
2. **Crear una explicación** del resultado y colocarla en `ecosystem/wiki/`.
3. **Vincular** la explicación con el dato correspondiente (usando enlaces de Obsidian o notas al pie).

## Convenciones de Nombrado
- **Archivos de datos**: colocar en `ecosystem/data/` con nombres descriptivos, por ejemplo:
  - `species_observations.csv`
  - `climate_data.xlsx`
  - `model_predictions.json`
- **Archivos de explicación**: colocar en `ecosystem/wiki/` con el mismo nombre base que el dato, añadiendo el sufijo `_explicación.md` (o `.md`). Por ejemplo:
  - Para `species_observations.csv` → `species_observations_explicación.md`
  - Para `climate_data.xlsx` → `climate_data_explicación.md`
- Dentro de cada archivo de explicación, incluya:
  - **Qué es**: descripción del contenido.
  - **Fuente u origen**: cómo se obtuvo o generó.
  - **Formato y estructura**: columnas, tipos de datos, etc.
  - **Uso previsto**: para qué se utiliza en el proyecto.
  - **Limitaciones o notas importantes**.

## Ejemplo
Si un agente genera un archivo `ecosystem/data/biodiversity_indices.csv`, debe crear:
```
ecosystem/wiki/biodiversity_indices_explicación.md
```
con al menos las secciones mencionadas arriba.

## Enlaces en Obsidian
Utilice la sintaxis de enlaces de Obsidian para conectar la explicación con el dato:
```
[[biodiversity_indices_explicación]]
```
o, desde la explicación, enlace al dato:
```
[[../data/biodiversity_indices.csv]]
```
(Relative paths desde la wiki al data).

## Responsabilidad del Agente
- Antes de finalizar cualquier tarea, verifique que tanto el dato como su explicación exista y esté correctamente vinculado.
- Si actualiza un dato, actualice también su explicación.
- Si elimina un dato, considere archivar o marcar su explicación como obsoleta.

## Preguntas
Si tiene dudas sobre dónde guardar algo o cómo estructurar la explicación, consulte el archivo `PROJECT_OVERVIEW.md` en la raíz del proyecto o pregunte al usuario.

---

**Recuerda**: El vault es la memoria compartida del proyecto. Mantenerlo ordenado y bien documentado facilita la colaboración entre humanos y agentes de IA.