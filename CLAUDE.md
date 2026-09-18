# Encuesta UIA — Internacionalización

App Streamlit de relevamiento de intereses de internacionalización para cámaras empresariales de la UIA.

## URLs
- **App online:** https://encuesta-uia-owyzyxrsybs4nydo7eb2t9.streamlit.app/
- **Repo GitHub:** https://github.com/adrianatulasne-dot/Encuesta-UIA

## Para correr localmente
```
cd C:\Users\atula\Documents\UIA-Comercio-Exterior\encuesta-uia\encuesta_uia
streamlit run app.py --server.port 8502
```

## Para publicar cambios
```
git add app.py
git commit -m "descripción del cambio"
git push
```
Streamlit Cloud se actualiza automáticamente en ~1 minuto.

## Estructura del proyecto
```
encuesta_uia/
├── app.py                  # App principal
├── requirements.txt        # Dependencias Python
├── CLAUDE.md               # Este archivo
├── respuestas.csv          # Respuestas guardadas (local, no sube a GitHub)
└── data_parquet/           # Datos (incluidos en el repo)
    ├── camaras.parquet         # PartidaNCM + NbreCamara (tabla camaras, DB UI)
    ├── clavecamaras.parquet    # NbreCamara + Pass (tabla clavecamaras, DB UI)
    ├── ncm_sectores.parquet    # HSUSA 6 dígitos + Sector + Subsector + Descripcion
    ├── expo_arg.parquet        # Exportaciones Argentina (8 dígitos, USD)
    ├── impo_arg.parquet        # Importaciones Argentina (8 dígitos, USD)
    ├── expo_pais_mundo.parquet # Exportaciones 12 países CPTPP vs mundo (miles USD)
    ├── impo_pais_mundo.parquet # Importaciones 12 países CPTPP vs mundo (miles USD)
    └── paisindec.parquet       # Tabla de países con codindec
```

## Fuente de datos
- **SQL Server:** `DESKTOP-1TIKEG2\SQLEXPRESS`, base `UI` y `UI_CPTPP`
- **Script de extracción:** `C:\Users\atula\Documents\UIA-Comercio-Exterior\encuesta-uia\extraer_datos.py`
- **Script sync Supabase → SQL Server:** `C:\Users\atula\Documents\UIA-Comercio-Exterior\encuesta-uia\supabase_to_sqlserver.py`
- Para actualizar los datos: correr `extraer_datos.py`, copiar los parquets a `data_parquet/` y hacer push.

## Módulos de la app

### 📋 Encuesta (4 pasos)
1. **Datos de contacto** — nombre, cargo, email, actividad (exporta/importa/ambas)
2. **Posiciones NCM** — solo las de la cámara logueada, agrupadas por subsector, mark/unmark
3. **Países y negociaciones** — 12 países CPTPP + 7 negociaciones en curso
4. **Resumen** — resumen completo + tabla de comercio por NCM × país

### 🔍 Consulta de comercio
- Selector de país CPTPP + filtro sector/subsector
- Gráfico 4 barras (azul=expo, verde=impo)
- 4 tabs con detalle por NCM

## Login
- 34 cámaras, cada una con su propia clave
- Al autenticarse se cargan solo los NCMs de esa cámara
- Fuente: `clavecamaras.parquet` (NbreCamara, Pass)

## Cosas importantes a recordar

### NCM: mismatch de dígitos
- `expo_arg` / `impo_arg` tienen NCM a **8 dígitos** (de SQL Server)
- `ncm_sectores` y `camaras` tienen NCM a **6 dígitos**
- Solución: `ncm6 = partidaNCM.str[:6].str.zfill(6)` — siempre filtrar con ncm6

### Unidades
- Argentina: datos en **USD** → se divide por 1.000.000 en app para mostrar en M USD
- Países (CPTPP y otros): datos en **M USD** — NO dividir

### CPTPP: mapeo de nombres
Los nombres en `expo/impo_pais_mundo.parquet` son distintos a los que se muestran:
- "Canadá" → "Canada", "Japón" → "Japon", "México" → "Mexico"
- Ver dict `NOMBRE_MUNDO` en app.py

### codindec para Argentina
Cada país CPTPP tiene uno o más códigos en paisindec para filtrar expo/impo arg:
- Ver dict `PAIS_CODINDEC` en app.py

## Países disponibles
CPTPP: Australia, Brunei, Canada, Chile, Japon, Malasia, Mexico, Nueva Zelanda, Peru, Reino Unido, Singapur, Vietnam
Otros: Camboya, Emiratos Árabes Unidos, Filipinas, India, Indonesia, Korea del Sur, Laos, Myanmar, Tailandia

## Respuestas — Supabase
- Tabla `respuestas_encuesta` en Supabase (PostgreSQL cloud)
- RLS habilitado con política allow_all
- matriz_interes se guarda como dict con claves tupla string: `"('ncm', 'pais')"`
- Para sincronizar a SQL Server: correr `supabase_to_sqlserver.py` → base `RespuestasEncuesta`

## Documentación
- Manual de usuario: `manual_usuario.docx`
- Manual técnico: `manual_tecnico.docx`
