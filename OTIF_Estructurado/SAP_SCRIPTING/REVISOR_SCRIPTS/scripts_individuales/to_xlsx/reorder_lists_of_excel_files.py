#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import glob
import re
import unicodedata
import json
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import traceback

# Config por defecto: si usas siempre el mismo YAML, déjalo aquí
DEFAULT_CONFIG_PATH = r"C:\Users\ELOPEZ21334\anaconda_projects\OTIF_Master\OTIF_Estructurado\SAP_SCRIPTING\REVISOR_SCRIPTS\scripts_individuales\to_xlsx\lista_excel_files.yaml"

# ----------------- Utiles de nombres/fechas -----------------
def _strip_accents(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))

def detect_date_columns(columns: List[str], forced: List[str] = None) -> List[str]:
    """
    Detecta columnas de fecha por nombre (insensible a mayúsculas y acentos).
    Ej.: 'Fe.Entrega', 'Fecha Guía', 'Creado el', etc.
    """
    date_like = []
    pattern = re.compile(r"(^|\b)(fe(cha)?|creado|gu[ií]a)(\b|$)|fe\.|entrega", re.IGNORECASE)
    for col in columns:
        base = _strip_accents(col).lower().strip()
        if pattern.search(base):
            date_like.append(col)
    if forced:
        for c in forced:
            candidates = [x for x in columns if x == c or _strip_accents(x).lower() == _strip_accents(c).lower()]
            date_like.extend(candidates)
    seen = set(); out = []
    for c in date_like:
        if c not in seen:
            seen.add(c); out.append(c)
    return out

def fix_dot_dates(series: pd.Series) -> pd.Series:
    """
    Reemplaza '.' por '-' cuando el valor es string con patrón dd.mm.yyyy.
    No toca datetimes ni horas '00:00:00'.
    """
    date_re = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
    def _fix(val):
        if isinstance(val, str):
            s = val.strip()
            if date_re.fullmatch(s):
                return s.replace('.', '-')
        return val
    return series.map(_fix)

def drop_header_like_rows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Elimina filas que parecen encabezados repetidos: >=50% de celdas iguales al nombre de su columna.
    """
    if df.empty:
        return df
    cols = list(df.columns)
    to_drop = []
    threshold = max(1, int(0.5 * len(cols)))
    for idx, row in df.iterrows():
        matches = 0
        for c in cols:
            cell = str(row[c]).strip()
            if cell == str(c).strip():
                matches += 1
                if matches >= threshold:
                    to_drop.append(idx)
                    break
    if to_drop:
        df = df.drop(index=to_drop)
    return df

# ----------------- Soporte de inicio flexible -----------------
def col_letter_to_index(letter: str) -> int:
    """
    Convierte letras de columna tipo Excel (A, B, ..., AA) a índice 0-based.
    """
    letter = letter.strip().upper()
    num = 0
    for ch in letter:
        if not ('A' <= ch <= 'Z'):
            raise ValueError(f"Columna inválida: {letter}")
        num = num * 26 + (ord(ch) - ord('A') + 1)
    return num - 1  # 0-based

def parse_start_cell(start_cell: str) -> Tuple[int, int]:
    """
    Parsea 'B5' -> (row_idx_0based=4, col_idx_0based=1) donde esa fila es el ENCABEZADO.
    """
    m = re.fullmatch(r"\s*([A-Za-z]+)\s*(\d+)\s*", start_cell)
    if not m:
        raise ValueError(f"start_cell inválido: {start_cell}")
    col_letters, row_str = m.group(1), m.group(2)
    col_idx = col_letter_to_index(col_letters)
    row_idx = int(row_str) - 1  # 0-based
    return row_idx, col_idx

def read_with_start(src_path: str,
                    header_row_1based: Optional[int] = None,
                    start_col: Optional[str] = None,
                    start_cell: Optional[str] = None) -> pd.DataFrame:
    """
    Lee el Excel aplicando un punto de inicio:
      - Si se indica start_cell (p.ej. 'B5'), el encabezado está en esa fila/columna.
      - Sino, si se indica start_col + header_row, se combina (equivale a start_cell).
      - En ausencia de ambos, cae al modo estándar (header=header_row-1).
    Retorna un DataFrame con columnas = encabezado detectado y datos desde la fila siguiente.
    """
    if start_cell or (start_col and header_row_1based):
        # Leer sin encabezado para rebanar manualmente
        df_raw = pd.read_excel(src_path, header=None, engine='openpyxl')
        if start_cell:
            header_row_idx, start_col_idx = parse_start_cell(start_cell)
        else:
            start_col_idx = col_letter_to_index(str(start_col))
            header_row_idx = max(0, int(header_row_1based) - 1)

        # Construir encabezado y cuerpo desde ese punto
        header_vals = list(df_raw.iloc[header_row_idx, start_col_idx:])
        data = df_raw.iloc[header_row_idx + 1 :, start_col_idx:].copy()

        # Limpiar encabezados vacíos (None/NaN) al final
        # (si hay columnas sin nombre, pandas las conserva como NaN; las dejamos, pero puedes quitarlas si quieres)
        data.columns = header_vals
        return data

    # Modo estándar (sin offset de columna)
    header_idx = max(0, (header_row_1based or 1) - 1)
    return pd.read_excel(src_path, header=header_idx, engine='openpyxl')

# ---------------------- Proceso de un archivo ----------------------
def process_file(
    src_path: str,
    ref_cols: List[str],
    header_row_1based: int = 5,
    keep_extras: bool = True,
    forced_date_cols: List[str] = None,
    start_col: Optional[str] = None,
    start_cell: Optional[str] = None,
) -> pd.DataFrame:
    """
    - Lee el archivo considerando start_cell o start_col/header_row.
    - Limpia filas vacías / encabezados repetidos
    - Corrige fechas dd.mm.yyyy -> dd-mm-yyyy
    - Reordena para coincidir con ref_cols; crea vacías las faltantes
    - Si keep_extras=True, deja columnas extra al final
    """
    df = read_with_start(
        src_path=src_path,
        header_row_1based=header_row_1based,
        start_col=start_col,
        start_cell=start_cell,
    )

    df = df.dropna(how='all')
    df = drop_header_like_rows(df)

    date_cols = detect_date_columns(list(df.columns), forced=forced_date_cols)
    for c in date_cols:
        if c in df.columns:
            df[c] = fix_dot_dates(df[c])

    for c in ref_cols:
        if c not in df.columns:
            df[c] = pd.NA

    extras = [c for c in df.columns if c not in ref_cols]
    df = df.reindex(columns=(ref_cols + extras) if keep_extras else ref_cols)
    return df

# ---------------------- Carga de CONFIG ----------------------
def load_jobs_from_config(config_path: str) -> List[Dict[str, Any]]:
    """
    Lee un archivo de configuración JSON o YAML con múltiples jobs.
    Campos soportados por job:
      - name, src_dir, out_dir, ref, pattern, header_row, keep_extras, date_cols, suffix
      - NUEVOS: start_cell (e.g., 'B5') ó start_col ('B')
    """
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"No se encuentra el archivo de configuración: {config_path}")

    ext = os.path.splitext(config_path)[1].lower()
    if ext in (".yaml", ".yml"):
        import yaml  # requiere pyyaml
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    else:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    jobs = data.get("jobs", [])
    if not isinstance(jobs, list) or not jobs:
        raise ValueError("El archivo de configuración no contiene la clave 'jobs' con una lista válida.")

    # Validar mínimos por job y defaults
    for i, j in enumerate(jobs):
        for k in ("src_dir", "out_dir", "ref"):
            if not j.get(k):
                raise ValueError(f"Job #{i+1} carece de '{k}'.")
        if not os.path.isdir(j["src_dir"]):
            raise FileNotFoundError(f"Carpeta no existe (job #{i+1}): {j['src_dir']}")
        if not os.path.isfile(j["ref"]):
            raise FileNotFoundError(f"Referencia no existe (job #{i+1}): {j['ref']}")
        os.makedirs(j["out_dir"], exist_ok=True)
        j.setdefault("pattern", "*.xlsx")
        j.setdefault("header_row", 5)
        j.setdefault("keep_extras", True)
        j.setdefault("date_cols", [])
        j.setdefault("suffix", "_REORDENADO")
        # Normalización para start_col: permitir número o letra
        if "start_col" in j and j["start_col"] is not None:
            j["start_col"] = str(j["start_col"]).strip()
        if "start_cell" in j and j["start_cell"] is not None:
            j["start_cell"] = str(j["start_cell"]).strip().upper()
    return jobs

# ----------------------------- MAIN -----------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Procesa múltiples carpetas de reportes PLR con una o varias salidas y plantillas (YAML/JSON)."
    )
    parser.add_argument("--config", default=None, help="Ruta a config YAML/JSON con 'jobs' múltiples.")
    parser.add_argument("--suffix", default=None, help="Sufijo global para los archivos de salida (opcional).")
    args = parser.parse_args()

    config_path = args.config or DEFAULT_CONFIG_PATH
    if not os.path.isfile(config_path):
        print(f"✖ No se encontró el archivo de configuración: {config_path}")
        print("  - Pasa uno con --config <ruta> o ajusta DEFAULT_CONFIG_PATH en el script.")
        sys.exit(1)

    try:
        jobs = load_jobs_from_config(config_path)
    except Exception as e:
        print(f"✖ Error leyendo la configuración: {e}")
        traceback.print_exc()
        sys.exit(1)

    total_files = 0
    print(f"Se ejecutarán {len(jobs)} job(s) del archivo:\n  {config_path}\n")
    for idx, job in enumerate(jobs, 1):
        sd = job["src_dir"]; od = job["out_dir"]; rf = job["ref"]
        pattern = job.get("pattern", "*.xlsx")
        header_row = job.get("header_row", 5)
        keep_extras = job.get("keep_extras", True)
        date_cols = job.get("date_cols", [])
        suffix = args.suffix if args.suffix is not None else job.get("suffix", "_REORDENADO")
        start_col = job.get("start_col")      # puede ser 'B'
        start_cell = job.get("start_cell")    # puede ser 'B5'

        print(f"Job {idx}: {job.get('name', '(sin nombre)')}")
        print(f"  Origen : {sd}")
        print(f"  Salida : {od}")
        print(f"  Ref    : {rf}")
        print(f"  Patrón : {pattern}")
        print(f"  Encab. : fila {header_row}")
        print(f"  Extras : {'mantener' if keep_extras else 'descartar'}")
        print(f"  Fecha  : {date_cols if date_cols else 'auto-detección'}")
        print(f"  Inicio : start_cell={start_cell or '-'} | start_col={start_col or '-'}")
        print(f"  Sufijo : {suffix}")

        # Cargar layout referencia
        try:
            df_ref = pd.read_excel(rf, header=0, engine="openpyxl")
            ref_cols = list(df_ref.columns)
        except Exception as e:
            print(f"  ✖ Error leyendo referencia: {e}")
            traceback.print_exc()
            continue

        # Enumerar archivos a procesar
        paths = sorted(glob.glob(os.path.join(sd, pattern)))
        # Excluir la propia referencia si está dentro de la carpeta
        paths = [p for p in paths if os.path.abspath(p) != os.path.abspath(rf)]

        if not paths:
            print(f"  ⚠ No se encontraron archivos en {sd} con patrón {pattern}")
            continue

        # Procesar
        print(f"  Encontrados: {len(paths)} archivo(s)")
        for src_path in paths:
            base = os.path.basename(src_path)
            try:
                df_out = process_file(
                    src_path=src_path,
                    ref_cols=ref_cols,
                    header_row_1based=header_row,
                    keep_extras=keep_extras,
                    forced_date_cols=date_cols,
                    start_col=start_col,
                    start_cell=start_cell,
                )
                name, ext = os.path.splitext(base)
                out_path = os.path.join(od, f"{name}{suffix}{ext}")
                with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                    df_out.to_excel(writer, index=False, sheet_name="Hoja1")
                total_files += 1
                print(f"  ✔ {base} -> {os.path.basename(out_path)} (filas: {len(df_out)})")
            except Exception as e:
                print(f"  ✖ Error procesando {base}: {e}")
                traceback.print_exc()

    print(f"\nTerminado. Archivos generados: {total_files}")

if __name__ == "__main__":
    main()
