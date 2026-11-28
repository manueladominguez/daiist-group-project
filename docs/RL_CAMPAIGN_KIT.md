# Kit de la campaña de feedback (WP6)

Guía operativa para Manuela. Aplica el protocolo preregistrado [`docs/RL_FEEDBACK_PROTOCOL.md`](RL_FEEDBACK_PROTOCOL.md) sin cambiar sus reglas: objetivo de 150 valoraciones elegibles, lecturas solo de validación, como máximo 15 valoraciones por sesión, parada fijada de antemano y aceptación de que puede no haber un estilo ganador.

**Estado (28 nov, mañana): no iniciada.** Empieza solo cuando se cumpla la sección 5 ("Checklist de lanzamiento"), y en particular cuando `agent-v2` esté desplegado ([`docs/GEMINI_VALIDATION.md`](GEMINI_VALIDATION.md), problema 1).

## 1. Material preparado

| Archivo | Para qué |
|---|---|
| `eval/rl_campaign/sheets/P01.md` … `P10.md` | Hoja de cada participante: 15 lecturas en orden aleatorio. Solo los seis valores de entrada: sin etiqueta de fallo, sin modo de fallo, sin banda de riesgo y sin identificador de la lectura ni mención del split, para que nadie pueda buscar la respuesta en los archivos públicos del repositorio |
| `eval/rl_campaign/sheets/P11.md`, `P12.md` | Reserva, solo si alguien de P01–P10 no puede participar |
| `eval/rl_campaign/tracker_template.csv` | Tabla de control: turno, estado y valoraciones elegibles antes y después de cada sesión |
| `eval/rl_scenarios.csv` | Las 30 lecturas definitivas (`status = final`), con sus etiquetas: **no se envía a los participantes** |

**Nombres.** El repositorio es público: en la tabla solo van los números P01–P12. Guarda la correspondencia número → nombre en una copia privada (por ejemplo, una hoja de cálculo tuya) y no la subas a GitHub.

## 2. Reparto de escenarios y equilibrio

Cada hoja reproduce exactamente `uv run python eval/select_rl_scenarios.py --order N` (semilla fija), como fija el protocolo; ese comando también da la correspondencia entre cada fila y su lectura (S01–S30), que solo necesita la coordinadora. Con P01–P10 salen 150 valoraciones:

| Banda de riesgo | Lecturas en el conjunto (30) | Valoraciones previstas (150) | Si fuera exactamente proporcional |
|---|---|---|---|
| Baja | 18 | 95 | 90 |
| Media | 2 | 8 | 10 |
| Alta | 4 | 18 | 20 |
| Crítica | 6 | 29 | 30 |

- Por bandas, el reparto es casi proporcional.
- **Por lectura no es uniforme:** cada lectura se valora entre 3 y 10 veces (la mayoría, 4–6), y P01 y P08 no tienen ninguna lectura de riesgo alto. Es consecuencia del orden aleatorio preregistrado; no se corrige a mano. Se informará en el análisis.
- Cada hoja tiene entre 4 y 7 lecturas que fallaron en el dataset y entre 8 y 11 de riesgo bajo.

## 3. Tiempo, cuota de Gemini y turnos

**Tiempo por participante: 15–20 minutos** (15 órdenes: introducir 6 valores, unos 3–5 s de análisis, leer y valorar).

**Cuota.** Una orden de riesgo bajo usa 1 llamada a Gemini; las demás, 3. Con las hojas reales:

| Hoja | P01 | P02 | P03 | P04 | P05 | P06 | P07 | P08 | P09 | P10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Llamadas (+10 % de reintentos) | 25 | 25 | 32 | 30 | 30 | 32 | 30 | 25 | 30 | 28 |

- Total: **unas 287 llamadas** para 150 valoraciones. Es una estimación: 1 llamada por orden de riesgo bajo, 3 por las demás y un 10 % de reintentos. Las peticiones fuera de alcance (por ejemplo, una errata que deja un valor fuera de rango) no gastan cuota.
- **Reinicio de la cuota: a las 09:00, hora de España** (medianoche en el Pacífico; comprobado para el 28, 29 y 30 de noviembre). El presupuesto de Render (`DAILY_LLM_BUDGET=400`) cuenta las llamadas del día del Pacífico a partir de los logs, así que sobrevive a los reinicios.
- El protocolo permite como máximo **300 llamadas de campaña al día** y deja 100 de reserva en Render (pruebas, profesor, demos).
- **Como máximo 2 participantes a la vez:** el 28 nov apareció un error 429 con unas 13 llamadas en un minuto, y esa petición tardó 31 s.

**Margen para WP4.** La evaluación de WP4 se ejecuta en local con la clave de quien la lance y su propia caché: **no** consume el presupuesto de 400 de Render. Pero el límite gratuito de Google es **por proyecto** (unas 500 llamadas al día con Flash-Lite, según nuestra suposición, no confirmada en AI Studio). Si la clave de WP4 es del mismo proyecto que la de Render, comparten ese límite. El juez de WP4 usa otro modelo (`gemini-3.8-flash`), con su propio límite diario, que el plan estimaba en unas 20 llamadas: WP4 debe comprobarlo en AI Studio, porque no alcanzaría para juzgar 41 órdenes en un solo día.

| Plan | Día del presupuesto | Campaña | Quedan en Render (de 400) | Margen del proyecto si WP4 comparte proyecto (unas 500) |
|---|---|---|---|---|
| A (recomendado) | Sábado 28 | P01–P05: unas 142 | unas 258 | unas 358 para WP4 y demos |
| A | Domingo 29 | P06–P10: unas 145 (+57 si hay reservas) | unas 198–255 | unas 298–355 |
| B (todo el domingo) | Domingo 29 | P01–P10: unas 287 (hasta 300) | unas 100–113 | unas 200–213: **la evaluación de WP4 debe hacerse el sábado o con una clave de otro proyecto** |

**Turnos propuestos** (ya están en la tabla de control):

| Día del presupuesto | Turno | Participantes | Llamadas aprox. |
|---|---|---|---|
| Sábado 28 (hasta el domingo a las 09:00) | 18:00–18:30 · 18:30–19:00 · 19:00–19:30 | P01–P05 (equipo) | 142 |
| Domingo 29 | 10:00–10:30 · 10:30–11:00 · 11:00–11:30 | P06–P10 (externos) | 145 |
| Domingo 29 | 12:00–13:30 | P11–P12 (solo si falta alguien) | hasta 57 |

- Equipo el sábado y compañeros externos el domingo: así se cumple la separación por ventanas que pide el protocolo (sección 3).
- **Plan B**, si `agent-v2` no llega el sábado: los 10 el domingo, de 10:00 a 15:00, de dos en dos (unas 287 llamadas, por debajo de las 300 del protocolo). Cabe, pero deja poco margen en Render y en el proyecto: ver la tabla anterior. Las reservas P11–P12 solo caben si sobran llamadas de ese día.
- **Límite: domingo a las 18:00**, con lo que se haya conseguido (sección 9 del protocolo).

## 4. Mensaje de WhatsApp (copiar y pegar)

> ¡Hola! Te escribo por el proyecto de IA de mantenimiento predictivo (MaintAI). ¿Nos ayudas con unos **15–20 minutos** el **[día] a las [hora]**?
>
> 1. Abre https://maintai-238a.onrender.com (si tarda en cargar, espera un minuto: el servidor se está despertando).
> 2. En la pestaña **App**, introduce una a una las 15 lecturas de la hoja que te adjunto, **en ese orden**, y pulsa **Analyse machine**.
> 3. Lee cada orden de trabajo como si fueras el responsable de mantenimiento y vota con sinceridad: 👍 **Useful** o 👎 **Not useful**. **Vota todas**, también las normales.
> 4. Usa una sola ventana y no recargues la página. No comentes las órdenes con nadie hasta que todos hayan terminado.
>
> No se guardan nombres ni datos personales: solo un identificador temporal y aleatorio de la sesión, y los resultados se publican de forma agregada en un trabajo de la universidad. ¡Gracias!

Adjunta la hoja `Pxx.md` del participante (como captura o PDF). Si alguien no puede, usa una hoja de reserva (P11, P12) y nunca repitas una hoja.

## 5. Checklist de lanzamiento (cuando `agent-v2` esté desplegado)

**A. Correcciones de WP3**
1. Comprueba en GitHub que el PR de Jacobo con `agent-v2` está fusionado, y en Render → **Events** que el último despliegue está *Live* con ese commit.
2. En local, sobre `main` actualizado:
   - `uv run python tests/test_agent.py`;
   - `uv run python tests/test_bandit.py`;
   - comprueba que `agent.PROMPT_VERSION` es `agent-v2`.
3. Comprobación real de la corrección (**1 llamada a Gemini**, necesita tu autorización):
   ```bash
   uv run python eval/controlled_validation/controlled_gemini_validation.py --i-authorise-gemini-calls --only B_low_cost
   ```
   La justificación ya no debe citar un ratio de costes ni horas de parada. Opcional, si Jacobo cambió algo sobre la revisión variable: `--only C_high_checklist,C_high_cost,C_high_root_cause` (9 llamadas).

**B. Render: memoria, CPU y errores**

4. Render → servicio **maintai** → **Metrics**: anota la memoria en reposo.
5. Haz **una** petición en la app online (muestra *Heat dissipation*, sin valorarla). Gasta 3 llamadas y queda como tráfico real sin valorar. Mira en Metrics el pico de memoria y CPU. Mi estimación es de unos 315 MB, con un límite de 512 MB.
6. Render → **Logs**: busca `Traceback`, `429`, `llm_unavailable`, `budget` y `memory`. Si hay errores, **no lances la campaña**.

**C. Estado inicial de la política (exportación de inicio)**

7. Ejecuta `uv run python main.py export-logs` (con `LOGS_DATABASE_URL` en `.env`).
8. Ejecuta `uv run python eval/export_rl_evidence.py --logs-dir logs --out eval/rl_evidence/start`.
9. Comprueba en `eval/rl_evidence/start/manifest.json`:
   - `prompt_version = agent-v2`;
   - `n_eligible_ratings = 0`;
   - prior `neutral Beta(1, 1)`;
   - el aviso de "no eligible real rating yet".

   Ese es el estado inicial: los tres estilos con un 50 % [3 %–98 %] y unos 33 % de probabilidad de selección.
10. Haz una captura de Monitoring → Adaptive Intelligence.
11. Avisa al equipo: **no fusionar nada que toque el agente o los prompts hasta el domingo a las 18:00**, porque una nueva versión de los prompts reinicia la política.

**D. Lanzamiento y comprobación auténtica del bandit**

12. Envía el mensaje del apartado 4 a P01 y P02 con sus hojas.
13. Cuando P01 haya valorado su primera orden, pulsa **Refresh** en Monitoring:
    - *Eligible real ratings* debe pasar de 0 a 1;
    - el α o el β del estilo servido debe subir en uno.

    Esta es la validación auténtica del bucle, hecha con una valoración real de la campaña: no hace falta ninguna valoración de prueba. Si sigue en 0 tras un par de valoraciones, **pausa la campaña** (regla 6 del protocolo) y avísame.

**E. Seguimiento (después de cada turno)**

14. Anota en la tabla las *Eligible real ratings* antes y después del turno. La diferencia debería ser unas 15 por participante.
15. Comprueba el consumo de Gemini del día (tras un `export-logs`):
    ```bash
    uv run python -c "import pandas as pd; r=pd.read_json('logs/requests-export.jsonl',lines=True); t=pd.to_datetime(r.timestamp,utc=True).dt.tz_convert('America/Los_Angeles'); m=t.dt.date==pd.Timestamp.now(tz='America/Los_Angeles').date(); l=r.loc[m,'llm'].apply(lambda x: x if isinstance(x,dict) else {}); print('Gemini requests today (Pacific day):', int(sum((d.get('llm_calls') or 0)+(d.get('retries') or 0) for d in l)), 'of 400')"
    ```
    Si las llamadas de campaña del día se acercan a 300, no empieces otro turno ese día.
16. **Pausa la campaña** si:
    - una orden cambia la acción, la prioridad o la revisión obligatoria según el estilo;
    - una entrada fuera de alcance produce una orden;
    - más del 20 % de las últimas 20 peticiones salen degradadas;
    - las valoraciones dejan de aparecer.

    Nunca se para ni se alarga porque un estilo vaya ganando o perdiendo. Durante la campaña mira solo los números operativos, no los resultados por estilo.

**F. Final y análisis**

17. Termina al llegar a **150 valoraciones elegibles contadas** o el **domingo a las 18:00**, lo que ocurra antes.
18. Ejecuta `uv run python main.py export-logs` y después `uv run python eval/export_rl_evidence.py --logs-dir logs --out eval/rl_evidence/end`, y haz capturas del panel.
19. Compara la carpeta `start` con la `end`:
    - `policy_snapshot.csv` (α, β y media por estilo);
    - `belief_comparison.csv` (recompensa observada, media posterior, IPS exploratorio y P(selected));
    - `coverage_by_arm.csv` (valoraciones contadas por estilo);
    - `non_response.csv`, `exclusions.csv` y `metrics.json` (tasa de respuesta y retraso).
20. Aplica la lectura preregistrada (sección 11 del protocolo):
    - **preferencia clara:** P(mejor) ≥ 0,90 y al menos 30 valoraciones contadas de ese estilo;
    - **tentativa:** P(mejor) entre 0,70 y 0,90;
    - **sin preferencia clara:** por debajo de 0,70. Es un resultado válido.
21. Sube solo las carpetas agregadas `eval/rl_evidence/start` y `end`, nunca `logs/`, y actualiza la sección de RL del REPORT con las cifras reales y sus limitaciones.

## 6. Si no llegamos a 150

Se informa del número alcanzado y del motivo (cuota, tiempo o participantes), y se hace el mismo análisis con lo que haya. No se bajan los umbrales, no se añaden valoraciones simuladas, no se repiten hojas y no se mezclan valoraciones de peticiones stub o degradadas (protocolo, sección 9).
