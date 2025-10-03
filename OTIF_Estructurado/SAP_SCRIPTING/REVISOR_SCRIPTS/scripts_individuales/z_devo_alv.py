# -*- coding: utf-8 -*-
"""
Z_DEVO_ALV (homologado)
- Auto-conexion/sesion (--conn -1, --sess -1)
- Arbol dinamico (evita IDs fijos)
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

def attach_to_sap(conn_idx=-1, sess_idx=-1):
    try: SapGuiAuto = win32com.client.GetObject("SAPGUI")
    except Exception: raise SAPGuiError("No se encontro SAPGUI. Abre SAP Logon.")
    try: app = SapGuiAuto.GetScriptingEngine
    except Exception: raise SAPGuiError("No se pudo obtener ScriptingEngine. Habilita scripting.")
    cc = app.Children.Count if hasattr(app.Children, 'Count') else 0
    if cc==0: raise SAPGuiError("No hay conexiones abiertas.")
    if conn_idx is None or conn_idx < 0: conn_idx = cc-1
    if conn_idx >= cc: raise SAPGuiError(f"Conexion invalida {conn_idx}/{cc}")
    conn = app.Children(conn_idx)
    sc = conn.Children.Count if hasattr(conn.Children, 'Count') else 0
    if sc==0: raise SAPGuiError("La conexion no tiene sesiones abiertas.")
    if sess_idx is None or sess_idx < 0: sess_idx = sc-1
    if sess_idx >= sc: raise SAPGuiError(f"Sesion invalida {sess_idx}/{sc}")
    sess = conn.Children(sess_idx)
    return app, conn, sess, conn_idx, sess_idx

def find(session, obj_id, timeout=12.0, interval=0.25):
    t0=time.time()
    while time.time()-t0<timeout:
        try: return session.FindById(obj_id)
        except Exception: time.sleep(interval)
    raise SAPGuiError(f"No se encontro el control: {obj_id}")

def exists(session, obj_id):
    try: session.FindById(obj_id); return True
    except Exception: return False

def press_if_exists(session, obj_id):
    if exists(session, obj_id):
        try: session.FindById(obj_id).press(); return True
        except Exception: pass
    return False

def send_tcode(session, tcode):
    wnd0=find(session,"wnd[0]")
    try: wnd0.maximize()
    except Exception: pass
    ok=find(session,"wnd[0]/tbar[0]/okcd"); ok.text=tcode; wnd0.sendVKey(0)

# ---- dinamico / debug ----

def iter_children(obj):
    try: c=obj.Children.Count
    except Exception: return
    for i in range(c): yield obj.Children(i)

def find_control_by_type(root, target_type, timeout=8.0):
    import time
    t0=time.time()
    while time.time()-t0<timeout:
        q=[root]
        while q:
            n=q.pop(0)
            try:
                if getattr(n,'Type','')==target_type: return n
            except Exception: pass
            q.extend(list(iter_children(n)))
        time.sleep(0.25)
    return None

def try_get_tree(session):
    cands=[
        "wnd[0]/usr/cntlIMAGE_CONTAINER/shellcont/shell/shellcont[0]/shell",
        "wnd[0]/usr/cntlTREE_CONTAINER/shellcont/shell/shellcont[0]/shell",
        "wnd[0]/usr/shell/shellcont[0]/shell",
        "wnd[0]/usr/cntlGRID_CONTAINER/shellcont/shell/shellcont[0]/shell",
    ]
    for cid in cands:
        if exists(session,cid):
            ctl=session.FindById(cid)
            if getattr(ctl,'Type','') in ("GuiTree","GuiShell"): return ctl
    usr=find(session,"wnd[0]/usr")
    return find_control_by_type(usr,"GuiTree",timeout=6.0)

def select_tree_node_dynamic(session,node_key,debug=False):
    tree=try_get_tree(session)
    if not tree:
        if debug: print("INFO: No se detecto GuiTree; sigo sin nodo.")
        return False
    try:
        tree.selectedNode=node_key; tree.doubleClickNode(node_key)
        if debug: print(f"OK nodo: {node_key}")
        return True
    except Exception as e:
        if debug: print(f"WARN no abrio nodo {node_key}: {e}")
        return False

def dump_controls(session,wnd="wnd[0]"):
    print("\n--- DUMP CONTROLES ---")
    root=find(session,f"{wnd}/usr"); q=[(root,f"{wnd}/usr")]
    while q:
        obj,p=q.pop(0)
        t=""; 
        try: t=obj.Type
        except Exception: pass
        print(f"{p} -> {t}")
        try:
            c=obj.Children.Count
            for i in range(c):
                ch=obj.Children(i)
                try: cid=ch.Id
                except Exception: cid=f"{p}/<?>[{i}]"
                q.append((ch,cid))
        except Exception: pass
    print("--- FIN DUMP ---\n")

def go_to_easy_access(session):
    ok=find(session,"wnd[0]/tbar[0]/okcd"); ok.text="/n"; find(session,"wnd[0]").sendVKey(0)
    for i in (2,1):
        press_if_exists(session,f"wnd[{i}]/tbar[0]/btn[0]")
        press_if_exists(session,f"wnd[{i}]/tbar[0]/btn[11]")
        press_if_exists(session,f"wnd[{i}]/usr/btnSPOP-OPTION1")


def run_z_devo_alv(session,tcode,node_key,row_number,output_path,filename,encoding="0000",debug=False):
    send_tcode(session,tcode)
    has_tree=select_tree_node_dynamic(session,node_key,debug=debug)
    if debug and not has_tree: print("INFO: sin nodo (no hay arbol o ID distinto)")
    if press_if_exists(session,"wnd[0]/tbar[1]/btn[17]") is False and debug:
        print("INFO: no boton seleccion [17]")
    ename=find(session,"wnd[1]/usr/txtENAME-LOW"); ename.text=""
    try: ename.setFocus(); ename.caretPosition=0
    except Exception: pass
    find(session,"wnd[1]/tbar[0]/btn[8]").press()
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
    p=argparse.ArgumentParser(description="Z_DEVO_ALV homologado")
    p.add_argument("--tcode",default="y_devo_alv"); p.add_argument("--node",default="F00072")
    p.add_argument("-r","--row",type=int,default=12); p.add_argument("-o","--output",default=r"C:\\data\\z_devo_alv")
    p.add_argument("-f","--filename"); p.add_argument("--conn",type=int,default=-1); p.add_argument("--sess",type=int,default=-1)
    p.add_argument("--debug",action="store_true"); return p.parse_args()

def main():
    args=parse_args()
    if not args.filename: args.filename=f"z_devo_alv_{datetime.now().strftime('%d-%m-%Y')}.xls"
    ensure_dir(args.output)
    print("INICIANDO Z_DEVO_ALV (HOMOLOGADO)\n"+"="*60)
    try:
        _,_,session,rc,rs=attach_to_sap(args.conn,args.sess)
        print(f"Conexion={rc}, Sesion={rs}\nTCode: {args.tcode} | Nodo: {args.node} | Row: {args.row}\nSalida: {args.output}\\{args.filename}\nDebug: {'ON' if args.debug else 'OFF'}\n"+"="*60)
        full_path=run_z_devo_alv(session,args.tcode,args.node,args.row,args.output,args.filename,debug=args.debug)
        print("\n"+"="*60+"\nPROCESO Z_DEVO_ALV COMPLETADO\n"+"="*60)
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

if __name__=="__main__":
    main()