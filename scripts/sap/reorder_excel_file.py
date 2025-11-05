#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import glob
import re
import unicodedata
from typing import List
import pandas as pd
import traceback

# ========= RUTAS FIJAS (opcional) =========
# Deja None para usar parámetros de línea de comandos.
FIXED_SRC_DIR = r"C:\data\SAP_Extraction\rep_plr"
FIXED_OUT_DIR = r"C:\data\SAP_Extraction\rep_plr\output"
FIXED_REF_PATH = r"C:\data\SAP_Extraction\rep_plr\plantilla\REP_PLR_FINAL.xlsx"
# =========================================

def _strip_accents(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    return ''.join(c for c in unicodedata.normalize('NFKD', s) if not unicodedata.combining(c))

def detect_date_columns(columns: List[str], forced: List[str] = None) -> List[str]:
    """
    Detecta columnas de fecha por nombre (insensible a mayúsculas y acentos).
    Ej.: 'Fe.Entrega', 'Fecha Guía', 'Creado el', 'Fecha Guía', etc.
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
    # Unicos manteniendo orden
    seen = set()
    out = []
    for c in date_like:
        if c not in seen:
            seen.add(c)
            out.append(c)
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

def process_file(
    src_path: str,
    ref_cols: List[str],
    header_row_1based: int = 5,
    keep_extras: bool = True,
    forced_date_cols: List[str] = None,
) -> pd.DataFrame:
    """
    - Lee encabezados en la fila indicada (1-based)
    - Limpia filas vacías / encabezados repetidos
    - Corrige fechas dd.mm.yyyy -> dd-mm-yyyy
    - Reordena para coincidir con ref_cols; crea vacías las faltantes
    - Si keep_extras=True, deja columnas extra al final
    """
    header_idx = max(0, header_row_1based - 1)
    df = pd.read_excel(src_path, header=header_idx, engine='openpyxl')
    df = df.dropna(how='all')
    df = drop_header_like_rows(df)

    date_cols = detect_date_columns(list(df.columns), forced=forced_date_cols)
    for c in date_cols:
        if c in df.columns:
            df[c] = fix_dot_dates(df[c])

    for c in ref_cols:
        if c not in df.columns:
            df[c] = pd.NA

    if keep_extras:
        extras = [c for c in df.columns if c not in ref_cols]
        ordered = ref_cols + extras
    else:
        ordered = ref_cols

    df = df.reindex(columns=ordered)
    return df

def main():
    parser = argparse.ArgumentParser(description="Reordena columnas y corrige fechas en reportes PLR.")
    parser.add_argument("--src-dir", default=None, help="Carpeta con los archivos a procesar.")
    parser.add_argument("--ref", default=None, help="Ruta al archivo de referencia (layout final).")
    parser.add_argument("--out-dir", default=None, help="Carpeta de salida para los archivos procesados.")
    parser.add_argument("--pattern", default="*.xlsx", help="Patrón de archivos (default: *.xlsx).")
    parser.add_argument("--header-row", type=int, default=5, help="Fila (1-based) con los encabezados (default: 5).")
    parser.add_argument("--suffix", default="_REORDENADO", help="Sufijo del archivo de salida (default: _REORDENADO).")
    parser.add_argument("--keep-extras", dest="keep_extras", action="store_true", help="Conservar columnas extra al final (default).")
    parser.add_argument("--drop-extras", dest="keep_extras", action="store_false", help="Descartar columnas extra no presentes en el layout.")
    parser.set_defaults(keep_extras=True)
    parser.add_argument("--date-cols", default="", help="Lista separada por comas para forzar columnas de fecha (opcional).")
    args = parser.parse_args()

    # Resolver rutas (preferir CLI; si no, usar fijas)
    src_dir = args.src_dir or FIXED_SRC_DIR
    out_dir = args.out_dir or FIXED_OUT_DIR
    ref_path = args.ref or FIXED_REF_PATH

    # Validaciones tempranas
    if not src_dir or not os.path.isdir(src_dir):
        print(f" La carpeta de origen no existe: {src_dir}")
        sys.exit(1)
    if not ref_path or not os.path.isfile(ref_path):
        print(f" No se encuentra el archivo de referencia: {ref_path}")
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)

    # Cargar layout de referencia
    try:
        df_ref = pd.read_excel(ref_path, header=0, engine="openpyxl")
    except Exception as e:
        print(f" Error leyendo referencia '{ref_path}': {e}")
        traceback.print_exc()
        sys.exit(1)

    ref_cols = list(df_ref.columns)

    # Archivos a procesar (excluye la propia referencia)
    paths = sorted(glob.glob(os.path.join(src_dir, args.pattern)))
    paths = [p for p in paths if os.path.abspath(p) != os.path.abspath(ref_path)]

    if not paths:
        print(f" No se encontraron archivos con el patrón {args.pattern} en {src_dir}")
        sys.exit(0)

    forced_date_cols = [x.strip() for x in args.date_cols.split(",")] if args.date_cols.strip() else []

    print(f"Layout referencia: {len(ref_cols)} columnas")
    print(f"Archivos a procesar: {len(paths)}")
    print(f"Columnas de fecha: {forced_date_cols if forced_date_cols else 'auto-detección'}")
    print("Procesando...\n")

    for src_path in paths:
        base = os.path.basename(src_path)
        try:
            df_out = process_file(
                src_path=src_path,
                ref_cols=ref_cols,
                header_row_1based=args.header_row,
                keep_extras=args.keep_extras,
                forced_date_cols=forced_date_cols,
            )
            name, ext = os.path.splitext(base)
            out_path = os.path.join(out_dir, f"{name}{args.suffix}{ext}")

            with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
                df_out.to_excel(writer, index=False, sheet_name="Hoja1")

            print(f" {base} -> {os.path.basename(out_path)} (filas: {len(df_out)})")

        except Exception as e:
            print(f" Error procesando {base}: {e}")
            traceback.print_exc()

    print("\nTerminado.")

if __name__ == "__main__":
    main()