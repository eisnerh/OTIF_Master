# -*- coding: utf-8 -*-
"""
ZRED (homologado)
- Auto-conexion/sesion (--conn -1, --sess -1)
- --debug con DUMP de controles
- Exportacion y retorno a Easy Access
"""
import os, sys, time, argparse
from datetime import datetime
try:
    import win32com.client
except ImportError:
    print("❌ Falta pywin32. Instala con: pip install pywin32"); sys.exit(1)

class SAPGuiError(Exception): pass

def ensure_dir(p): os.makedirs(p, exist_ok=True)
from z_devo_alv import attach_to_sap, find, exists, press_if_exists, send_tcode, dump_controls, go_to_easy_access

def run_zred(session,row_number,output_path,filename,encoding="0000",debug=False):
    send_tcode(session,"zred")
    if press_if_exists(session,"wnd[0]/tbar[1]/btn[17]") is False and debug:
        print("INFO: no boton seleccion [17]")
    alv=find(session,"wnd[1]/usr/cntlALV_CONTAINER_1/shellcont/shell")
    try:
        if row_number>10: alv.firstVisibleRow=max(row_number-10,0)
    except Exception: pass
    alv.currentCellRow=row_number; alv.selectedRows=str(row_number); alv.doubleClickCurrentCell()
    find(session,"wnd[0]/tbar[1]/btn[8]").press()
    find(session,"wnd[0]/mbar/menu[0]/menu[3]/menu[2]").select()
    rb="wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]"
    find(session,rb).select(); find(session,"wnd[1]/tbar[0]/btn[0]").press()
    ensure_dir(output_path); full_path=os.path.join(output_path,filename)
    if os.path.exists(full_path):
        try: os.remove(full_path)
        except PermissionError:
            base,ext=os.path.splitext(filename); filename=f"{base}_{datetime.now().strftime('%H%M%S')}{ext}"; full_path=os.path.join(output_path,filename)
    find(session,"wnd[1]/usr/ctxtDY_PATH").text=output_path
    find(session,"wnd[1]/usr/ctxtDY_FILENAME").text=filename
    enc=find(session,"wnd[1]/usr/ctxtDY_FILE_ENCODING"); enc.text=encoding
    try: enc.setFocus(); enc.caretPosition=len(encoding)
    except Exception: pass
    find(session,"wnd[1]/tbar[0]/btn[11]").press()
    for i in (2,1):
        press_if_exists(session,f"wnd[{i}]/tbar[0]/btn[0]"); press_if_exists(session,f"wnd[{i}]/tbar[0]/btn[11]")
    if not os.path.isfile(full_path):
        if debug: dump_controls(session,"wnd[0]")
        press_if_exists(session,"wnd[0]/tbar[0]/btn[3]"); raise SAPGuiError(f"No se genero: {full_path}")
    go_to_easy_access(session)
    return full_path


def parse_args():
    p=argparse.ArgumentParser(description="ZRED homologado")
    p.add_argument("-o","--output",default=r"C:\\data\\zred"); p.add_argument("-f","--filename")
    p.add_argument("-r","--row",type=int,default=1); p.add_argument("--conn",type=int,default=-1); p.add_argument("--sess",type=int,default=-1)
    p.add_argument("--debug",action="store_true"); return p.parse_args()

def main():
    args=parse_args()
    if not args.filename: args.filename=f"zred_{datetime.now().strftime('%d-%m-%Y')}.xls"
    ensure_dir(args.output)
    print("INICIANDO ZRED (HOMOLOGADO)\n"+"="*60)
    try:
        _,_,session,rc,rs=attach_to_sap(args.conn,args.sess)
        print(f"Conexion={rc}, Sesion={rs}\nRow: {args.row}\nSalida: {args.output}\\{args.filename}\nDebug: {'ON' if args.debug else 'OFF'}\n"+"="*60)
        full_path=run_zred(session,args.row,args.output,args.filename,debug=args.debug)
        print("\n"+"="*60+"\nPROCESO ZRED COMPLETADO\n"+"="*60)
        print(f"Archivo: {os.path.basename(full_path)}\nUbicacion: {os.path.dirname(full_path)}\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"+"="*60)
        sys.exit(0)
    except KeyboardInterrupt:
        print("\nScript interrumpido"); sys.exit(1)
    except SAPGuiError as e:
        print(f"Error SAP: {e}");
        if args.debug:
            try: _,_,session,_,_=attach_to_sap(args.conn,args.sess); dump_controls(session,"wnd[0]")
            except Exception: pass
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}");
        if args.debug:
            try: _,_,session,_,_=attach_to_sap(args.conn,args.sess); dump_controls(session,"wnd[0]")
            except Exception: pass
        sys.exit(1)

if __name__=="__main__": main()
