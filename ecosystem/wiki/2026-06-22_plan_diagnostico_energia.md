# Plan de trabajo – Diagnóstico técnico‑biológico para el cálculo de calorías y consumo en la simulación agent‑based del Alt Pirineu

**Fecha:** 2026-06-22  
**Hora:** (al crear este documento)

---

## 1. Objetivo del diagnóstico  
Obtener la información biológica y técnica necesaria para estimar:
- **Gasto energético diario (DEE)** de cada agente (metabolismo basal + actividad + termogénesis).  
- **Ingesta energética potencial** basada en la dieta y la disponibilidad de recursos.  
- **Eficiencia de conversión** (asimilación, producción, pérdidas).  

Estos valores alimentarán el sistema de energía del agente (intake vs. expenditure) y permitirán validar dinámicas poblacionales frente a datos de monitoreo.

---

## 2. Etapas del diagnóstico  

| Etapa                                                    | Acción concreta                                                                                                                                                                                                                                                                                                                                 | Producto esperado                                                                                                                       | Dónde guardar (vault)                                                                      |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **2.1 Revisión bibliográfica de metabología**            | Buscar ecuaciones allométricas (Kleiber, Brody, etc.) y factores de actividad para mamíferos, aves, reptiles, anfibios y peces presentes en la lista de vertebrados y en los clusters de invertebrados.                                                                                                                                         | Tabla de referencias con ecuaciones, rangos de masa corporal y fuentes (artículos, libros, bases de datos como PanTHERIA, EltonTraits). | `ecosystem/wiki/metabolismo_revision.md` + enlaces a PDFs en `ecosystem/data/referencias/` |
| **2.2 Caracterización de la dieta**                      | Extraer de `vertebrates.tsv` y `trophic_matrix.tsv` los ítems de `main_diet` y los tipos de interacción (herbivoría, predación, carroñería, etc.). Convertirlos en categorías de recurso (plantas, invertebrados, vertebrados) y estimar la proporción de cada categoría en la dieta.                                                           | Matriz de proporciones dietéticas por especie/grupo funcional.                                                                          | `ecosystem/wiki/dieta_proporciones.md` + `ecosystem/data/dieta_proporciones.tsv`           |
| **2.3 Contenido energético de los recursos**             | Recoger valores típicos de kilocalorías por gramo (kcal/g) para: <br>• Plantas (hojas, frutos, semillas) – usar datos de composición química (carbohidratos, proteínas, lípidos). <br>• Invertebrados – valores según orden (Lepidoptera, coleópteros, etc.). <br>• Vertebrados – valores según tejido (músculo, grasa, órganos).               | Tabla de densité energética (kcal/g) por tipo de recurso, con rangos y fuentes.                                                         | `ecosystem/wiki/energia_recursos.md` + `ecosystem/data/energia_recursos.tsv`               |
| **2.4 Cálculo del Gasto Energético Diario (DEE)**        | Aplicar la ecuación allométrica elegida (ej. `DEE = a * M^b * FAct`) donde `M` es la masa corporal (kg) de `vertebrates.tsv` o la masa promedio asignada a cada cluster funcional. `FAct` se deriva de un factor de actividad (basal, foraging, locomotion, etc.) basado en observaciones etológicas o en valores típicos por clase taxonómica. | Hoja de cálculo con DEE estimado para cada especie/cluster.                                                                             | `ecosystem/wiki/dee_calculo.md` + `ecosystem/data/dee_estimado.tsv`                        |
| **2.5 Cálculo de la Ingesta Energética Potencial (IEP)** | `IEP = Σ (proporción_i * densidad_i * ingestión_max_i)` donde `ingestión_max_i` se puede estimar mediante allometría de ingesta (ej. `Ing = c * M^d`) o tomando valores de consumo máximo observados en la literatura.                                                                                                                          | Tabla de IEP por especie/cluster y comparación con DEE (balance energético).                                                            | `ecosystem/wiki/iep_calculo.md` + `ecosystem/data/iep_estimado.tsv`                        |
| **2.6 Validación y ajuste**                              | Comparar los balances DEE/IEP con datos de campo disponibles (p.ej., tasas de crecimiento observadas, ciclos reproductivos, datos de监测). Ajustar factores de actividad o eficiencias de asimilación si es necesario.                                                                                                                            | Informe de validación con gráficos de balance energético y recomendaciones de parámetros para el motor de simulación.                   | `ecosystem/wiki/validacion_energia.md` + figuras en `ecosystem/data/validacion/`           |
| **2.7 Integración al motor de simulación**               | Documentar cómo se pasarán los valores (DEE, IEP, eficiencia) al agente (p.ej., como atributos iniciales o como funciones que se actualizan cada timestep).                                                                                                                                                                                     | Especificación técnica para el programador (pseudocódigo o descripciones de módulos).                                                   | `ecosystem/wiki/integracion_energia.md`                                                    |

---

## 3. Herramientas y fuentes recomendadas  

| Tipo                                  | Fuente / Herramienta                                                                                                                         | Comentario                                              |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| **Ecología metabólica**               | *PanTHERIA* (base de datos de rasgos de mamíferos), *EltonTraits* (aves), *AmphibiaWeb*, *FishBase*                                          | Proporcionan masa corporal, tasa metabólica basal, etc. |
| **Ecuaciones allométricas**           | Kleiber (B = aM^0.75), campos específicos para locomotion, foraging, etc. (consultar Nagy 2005, “Field Metabolic Rate and Body Size”)        | Selección según grupo taxonómico.                       |
| **Contenido energético de alimentos** | USDA FoodData Central (para plantas), literatura de invertebrados (ej. “Energy content of insects”), tablas de composición de carne de caza. |                                                         |
| **Datos de ingestión**                | Estudios de tasas de ingesta (Ingestion Rate = c·M^d) para herbívoros y carnívoros.                                                          |                                                         |
| **Software**                          | Hoja de cálculo (LibreOffice/Excel) para cálculos iniciales; posteriormente scripts en Python/R para reproducibilidad.                       |                                                         |
| **Gestión de referencias**            | Zotero o gestor BibTeX para almacenar PDFs y citas; los PDFs pueden ir a `ecosystem/data/referencias/`.                                      |                                                         |

---

## 4. Próximos pasos concretos (tareas sugeridas)  

1. **Crear carpeta de referencias**  
   `mkdir -p ecosystem/data/referencias`  
2. **Descargar y almacenar PDFs clave** (PanTHERIA, EltonTraits, artículos de Nagy 2005, etc.)  
3. **Llenar la tabla de referencias** (`metabolismo_revision.md`).  
4. **Extraer y estructurar la información de dieta** a partir de los TSV existentes.  
5. **Buscar y tabular densidades energéticas** de cada tipo de recurso.  
6. **Implementar cálculos de DEE y IEP** en una hoja de cálculo provisional.  
7. **Realizar la validación** con datos de monitoreo del Alt Pirineu (si los tienes) o con valores típicos de la literatura.  
8. **Redactar la especificación de integración** para el motor de simulación.  

Cada tarea puede generar un archivo de salida en `ecosystem/wiki/` y, cuando corresponda, datos procesados en `ecosystem/data/`. Así el vault queda alimentado tanto con la información cruda como con su explicación y los resultados del diagnóstico.

---

## 5. Cómo usar el vault durante el diagnóstico  

- **Antes de iniciar cada sub‑tarea**, abre la guía `ECOSYSTEM_VAULT_GUIDE.md` (en la raíz) y verifica que el producto vaya a la ubicación correcta (`wiki/` para explicaciones, `data/` para archivos numéricos o PDFs).  
- **Después de finalizar una sub‑tarea**, crea o actualiza su archivo de explicación siguiendo la plantilla `Plantilla_explicación.md`.  
- **Enlaza siempre** al dato original (p.ej., `[[../data/dee_estimado.tsv]]`) y al `PROJECT_OVERVIEW.md` para que cualquiera que le pueda ver el porqué del cálculo dentro del proyecto.  
- **Versiona** si lo consideras útil (puedes subir los archivos a un repositorio Git o simplemente hacer copias con fecha en `ecosystem/data/versiones/`).  

---

### Resumen rápido  

| Fase | Qué se hace | Dónde queda |
|------|-------------|------------|
| Revisión bibliográfica | Recoger ecuaciones y factores taxonómicos | `ecosystem/wiki/metabolismo_revision.md` + PDFs |
| Caracterización de dieta | Proporciones de recursos por especie/cluster | `ecosystem/wiki/dieta_proporciones.md` + TSV |
| Energía de recursos | kcal/g de cada tipo de alimento | `ecosystem/wiki/energia_recursos.md` + TSV |
| Cálculo DEE | Gasto energético diario (allometría) | `ecosystem/wiki/dee_calculo.md` + TSV |
| Cálculo IEP | Ingesta energética potencial | `ecosystem/wiki/iep_calculo.md` + TSV |
| Validación | Comparar DEE/IEP con datos de campo | `ecosystem/wiki/validacion_energia.md` + figuras |
| Integración | Cómo pasar esos valores al agente | `ecosystem/wiki/integracion_energia.md` |

Con este diagnóstico tendrás una base cuantitativa y bien documentada para alimentar el módulo de energía de tu simulación agent‑based, y todo quedará registrado y enlazado dentro del vault de Obsidian **ecosystem** para que cualquier agente de IA o humano pueda consultarlo, reproducirlo o mejorarlo en el futuro. ¡Éxitos con el siguiente paso del proyecto!