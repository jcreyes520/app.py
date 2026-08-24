import streamlit as st
import io, os, pandas as pd
from datetime import datetime
import base64

st.set_page_config(page_title="FITCA - Sistema de Gestión de Proveedores v5.0", page_icon="🏢", layout="wide")

# =========================================================================
# 🏛️ SUITE DE ESTILOS PROFESIONALES - ERP CORPORATIVO CENTRAL FITCA v5.0
# =========================================================================
st.markdown("""
    <style>
    .stApp { background-color: #F4F5F7 !important; font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif !important; }
    .login-container { max-width: 320px; margin: 100px auto; background-color: #FFFFFF; padding: 25px; border-radius: 4px; border-top: 5px solid #1E5A34; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #D1D5DB; }
    .fitca-header-box { background-color: #FFFFFF !important; padding: 12px 20px !important; border-radius: 3px !important; border-left: 6px solid #1E5A34 !important; border-bottom: 1px solid #E5E7EB !important; box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important; margin-bottom: 20px !important; width: 100% !important; }
    .main-title { font-size:20px !important; font-weight:700 !important; color:#1E5A34 !important; line-height:1.2 !important; margin:0px !important; letter-spacing: -0.2px; text-transform: uppercase; }
    .sub-title { font-size:11px !important; color:#4B5563 !important; margin-top:3px !important; font-family: monospace !important; font-weight: 600; }
    div.stButton > button:first-child { background-color: #1E5A34 !important; color: #FFFFFF !important; border: 1px solid #1E5A34 !important; font-weight: 600 !important; font-size: 12.5px !important; border-radius: 3px !important; width: 100% !important; padding: 5px 10px !important; transition: background 0.15s ease-in-out; }
    div.stButton > button:first-child:hover { background-color: #153E20 !important; border-color: #153E20 !important; }
    .sidebar-user { background-color:#F9FAFB; padding:10px 12px; border-radius:3px; border: 1px solid #E5E7EB; border-left:4px solid #1E5A34; font-size:12px; color:#1E5A34; font-family: monospace; font-weight: 600; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #FFFFFF !important; border: 1px solid #C4C7CC !important; border-radius: 3px !important; padding: 3px 6px !important; font-size: 12.5px !important; color: #111827 !important; }
    div[data-testid='stSelectbox'] { width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# 📑 LISTA MAESTRA DE LAS ENTIDADES BANCARIAS VENEZOLANAS (SINTAXIS BLINDADA)
BCOS_LISTA_REAL = [
    "0102 - Banco de Venezuela (BDV)", "0163 - Banco del Tesoro", "0175 - Banco Digital de los Trabajadores (BDT)",
    "0177 - Banco de la Fuerza Armada Nacional Bolivariana (BANFANB)", "0166 - Banco Agrícola de Venezuela",
    "0134 - Banesco Banco Universal", "0105 - Mercantil Banco", "0108 - BBVA Provincial", "0191 - Banco Nacional de Crédito (BNC)",
    "0172 - Bancamiga Banco Universal", "0114 - BanCaribe", "0115 - Banco Exterior", "0138 - Banco Plaza", 
    "0151 - Banco Fondo Común (BFC)", "0174 - Banplus", "0104 - Banco Venezolano de Crédito (BVC)", "0128 - Banco Caroní",
    "0157 - Banco del Sur", "0171 - Banco Activo", "0137 - Banco Sofitasa", "0156 - 100% Banco", 
    "0001 - Banco Central de Venezuela (BCV)", "0146 - Bangente", "0168 - Bancrecer", "0169 - Mi Banco", 
    "0182 - N58 Banco Digital", "Otros (Internacional / Cuenta Extranjera)"
# 📑 LISTA MAESTRA DE LOS 12 RECAUDOS EXHAUSTIVOS DE LA PLANILLA FISCAL REAL DE PLANTA
RECAUDOS_GLOBAL = [
    ("Copia del Registro Mercantil.", "mer"), ("Copia del Registro de Información Fiscal (RIF).", "rif"),
    ("Copia de la Cédula de Identidad del Accionista.", "ced"), ("Licencia de Actividades Económicas.", "lic"),
    ("Cartas de Referencias Comerciales (Mínimo 2).", "ref_c"), ("Cartas de Referencias Bancarias (Mínimo 2).", "ref_b"),
    ("Suministros de Datos Bancarios para realizar pagos en cuentas nacionales.", "db"), ("Persona Contacto.", "p_cont"),
    ("Correo Electrónico.", "email"), ("Permiso sanitario y/o INSAI de los productos (Si aplica)", "san"),
    ("Declaración de IVA del 16-03-2026 al 31-03-2026.", "d_iva"), ("Declaración Definitiva de ISLR del 01-01-2025 al 31-12-2025.", "d_islr")
]

if "usuarios_db" not in st.session_state:
    st.session_state["usuarios_db"] = [
        {"nombre": "Juan Carlos", "apellido": "Reyes", "usuario": "supervisor", "clave": "fitca2026", "rol": "Contabilidad"},
        {"nombre": "Carlos", "apellido": "Mendoza", "usuario": "compras", "clave": "compras2026", "rol": "Compras"}
    ]
if "empresa_db" not in st.session_state: st.session_state["empresa_db"] = {"rs": "FRIGORÍFICO INDUSTRIAL TURMERO C.A. (FITCA)", "rif": "J-00015198-9", "dir": "Calle Las Industrias, Tronconal, Turmero, Edo. Aragua.", "tel": "0244-3214567 / 0244-3214568", "logo_bytes": None}

if "bitacora_db" not in st.session_state: st.session_state["bitacora_db"] = []
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 12px; font-weight: 700; color: #1E5A34; text-align: center; margin-bottom: 12px; font-family:monospace; letter-spacing:0.5px;">FITCA — SGP v5.0</p>', unsafe_allow_html=True)
    u_ing = st.text_input("Usuario Master:", key="u_log_input", placeholder="Ingrese usuario")
    c_ing = st.text_input("Clave Sistema:", type="password", key="p_log_input", placeholder="••••••••")
    if st.button("🔒 Autenticar Firma"):
        u_f = next((u for u in st.session_state["usuarios_db"] if u["usuario"] == u_ing and u["clave"] == c_ing), None)
        if u_f: st.session_state["autenticado"] = True; st.session_state["usuario_actual"] = u_f; st.rerun()
        else: st.error("❌ Credenciales inválidas.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    emp = st.session_state["empresa_db"]
    u_info = st.session_state["usuario_actual"]
    persona_elabora = f"{u_info['nombre']} {u_info['apellido']}"
    if "correos_recepcion_list" not in st.session_state: st.session_state["correos_recepcion_list"] = ["jcreyes520@gmail.com", "contabilidad@fitca.com"]
    
    with st.sidebar:
        if emp.get("logo_bytes"): st.image(emp["logo_bytes"], use_container_width=True)
        st.markdown(f'<div class="sidebar-user"><b>⚙️ TERMINAL ERP CONTROL:</b><br/>{persona_elabora}<br/><b>Rol:</b> {u_info["rol"]}</div>', unsafe_allow_html=True)
        if u_info["rol"] == "Contabilidad": menu_opciones = ["Planilla de Solicitudes", "📊 Informes", "📊 Bitácora de Auditoría", "⚙️ Configuración"]
        else: menu_opciones = ["Planilla de Solicitudes", "📊 Informes"]
        opcion_menu = st.selectbox("📂 Módulos del Sistema Central", menu_opciones)
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión Segura", use_container_width=True): st.session_state["autenticado"] = False; st.rerun()
            
    st.markdown('<div class="fitca-header-box">', unsafe_allow_html=True)
    c_h1, c_h2 = st.columns(2)
    with c_h1: st.markdown("<h4 style='color:#1E5A34; margin:0;'>🏢 FRIGORÍFICO INDUSTRIAL TURMERO C.A.</h4>", unsafe_allow_html=True)
    with c_h2: st.markdown(f'<p class="main-title">{emp["rs"]}</p><p class="sub-title">RIF: {emp["rif"]} | PLANTA: {emp["dir"]}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if opcion_menu == "⚙️ Configuración":
        st.write("#### ⚙️ PANEL DE CONFIGURACIÓN ADMINISTRATIVA Y PARÁMETROS (SGP)")
        new_rs = st.text_input("Razón Social:", value=emp["rs"])
        new_rif = st.text_input("RIF:", value=emp["rif"])
        new_dir = st.text_input("Dirección de Planta:", value=emp["dir"])
        new_tel = st.text_input("Teléfonos Centrales:", value=emp["tel"])
        f_logo = st.file_uploader("Cargar Archivo de Logo Corporativo FITCA (.PNG / .JPG):", type=["png", "jpg", "jpeg"])
        if f_logo: emp["logo_bytes"] = f_logo.read()
        if st.button("💾 Guardar Parámetros de Planta", use_container_width=True):
            emp["rs"], emp["rif"], emp["dir"], emp["tel"] = new_rs, new_rif, new_dir, new_tel
            st.success("✅ Parámetros de planta actualizados."); st.rerun()

    elif opcion_menu == "Planilla de Solicitudes":
        st.write("#### 📝 PLANILLA DE REGISTRO PREVIO (ENTRADA DE DATOS)")
        accion_planilla = st.radio("Operación Contable:", ["➕ Registrar Nuevo Proveedor", "✏️ Modificar / Actualizar Proveedor Existente"], horizontal=True)
        val_nombre, val_rif, val_contacto, val_telefono, val_correo, val_codigo, val_tipo, val_notas = "", "", "", "", "", 792, "Compras de Inventario / Materia Prima", ""
        val_soportes = {k: False for _, k in RECAUDOS_GLOBAL}; idx_match = None; tipo_sujeto_sel = "Sujeto Pasivo Especial (Especial)"
        val_cuentas = {"c1_bco": "0102 - Banco de Venezuela (BDV)", "c1_ben": "", "c1_tipo": "Empresa (RIF)", "c1_doc": "", "c1_num": "", "c2_bco": "0102 - Banco de Venezuela (BDV)", "c2_ben": "", "c2_tipo": "Empresa (RIF)", "c2_doc": "", "c2_num": "", "c3_bco": "0102 - Banco de Venezuela (BDV)", "c3_ben": "", "c3_tipo": "Empresa (RIF)", "c3_doc": "", "c3_num": ""}
        val_notas_marginales = {k: "" for _, k in RECAUDOS_GLOBAL}

        if accion_planilla == "✏️ Modificar / Actualizar Proveedor Existente" and len(st.session_state["bitacora_db"]) > 0:
            df_provs_mod = pd.DataFrame(st.session_state["bitacora_db"])
            list_mod_opts = df_provs_mod.apply(lambda row: f"{row['Código']} - {row['Proveedor']}", axis=1).tolist()
            selected_mod_prov = st.selectbox("🔍 Seleccione el Expediente del Proveedor:", list_mod_opts)
            try:
                if selected_mod_prov and " - " in selected_mod_prov: codigo_a_buscar = int(selected_mod_prov.split(" - ").strip())
                else: codigo_a_buscar = None
            except: codigo_a_buscar = None

            if codigo_a_buscar is not None:
                match = next((idx for idx, item in enumerate(st.session_state["bitacora_db"]) if item["Código"] == codigo_a_buscar), None)
                if match is not None:
                    idx_match = match; datos_viejos = st.session_state["bitacora_db"][idx_match]
                    val_nombre, val_rif, val_contacto, val_telefono, val_correo, val_codigo, val_tipo, val_notas = datos_viejos['Proveedor'], datos_viejos.get('Rif_Prov',''), datos_viejos.get('Contacto',''), datos_viejos['Teléfono'], datos_viejos.get('Correo',''), datos_viejos['Código'], datos_viejos.get('Tipo','Compras de Inventario / Materia Prima'), datos_viejos.get('Notas','')
                    val_soportes, val_cuentas, tipo_sujeto_sel = datos_viejos.get('Soportes', val_soportes), datos_viejos.get('Cuentas_Bancarias', val_cuentas), datos_viejos.get('Contribuyente', "Sujeto Pasivo Especial (Especial)")
                    val_notas_marginales = datos_viejos.get('Notas_Marginales', val_notas_marginales)

        st.write("##### 1. Identificación Comercial Básica")
        c_bas1, c_bas2, c_bas3, c_bas4 = st.columns(4)
        with c_bas1: c_prov = st.number_input("Código Maestro Proveedor Interno:", value=int(val_codigo), step=1)
        with c_bas2: n_prov = st.text_input("Nombre o Razón Social Comercial Completa:", value=val_nombre, placeholder="TERMO SERVICIOS R.W, C.A.")
        with c_bas3: r_prov = st.text_input("Número de RIF Comercial:", value=val_rif, placeholder="J-XXXXXXX-X")
        with c_bas4: tipo_prov = st.selectbox("Tipo de Gasto Contable:", ["Compras de Inventario / Materia Prima", "Servicios"], index=0)

        st.write("##### 2. Información de Contacto Operativo")
        c_con1, c_con2, c_con3, c_con4 = st.columns(4)
        with c_con1: t_prov = st.text_input("Teléfono Obligatorio de Planta:", value=val_telefono, placeholder="0244-XXXXXXX")
        with c_con2: p_cont = st.text_input("Persona / Contacto de Ventas Autorizado:", value=val_contacto, placeholder="Contacto")
        with c_con3: e_prov = st.text_input("Correo Electrónico / Mail de Operaciones:", value=val_correo, placeholder="correo@proveedor.com")
        with c_con4: tipo_sujeto_sel = st.selectbox("Calificación Fiscal del Contribuyente:", ["Sujeto Pasivo Especial (Especial)", "Contribuyente Ordinario"])

        st.write("##### 3. Gestión Multi-Cuenta Financiera (Hasta 3 Canales de Transferencia)")
        st.markdown("**[CANAL BANCARIO N° 1 - Principal Obligatorio]**")
        cb1_1, cb1_2, cb1_3, cb1_4 = st.columns([1, 1, 0.8, 1.2])
        with cb1_1: bco_1 = st.selectbox("Banco Destino (C1):", BCOS_LISTA_REAL, index=BCOS_LISTA_REAL.index(val_cuentas.get("c1_bco")) if val_cuentas.get("c1_bco") in BCOS_LISTA_REAL else 0, key="bco1")
        with cb1_2: ben_1 = st.text_input("Nombre Beneficiario Pago (C1):", value=val_cuentas.get("c1_ben") if val_cuentas.get("c1_ben") else val_nombre, key="ben1")
        with cb1_3: t_ben_1 = st.selectbox("Tipo Documento (C1):", ["Empresa (RIF)", "Persona Natural (Cédula)"], index=0 if val_cuentas.get("c1_tipo") == "Empresa (RIF)" else 1, key="t_ben1")
        with cb1_4:
            if t_ben_1 == "Persona Natural (Cédula)": doc_1 = st.text_input("Cédula de Identidad del Beneficiario (C1):", value=val_cuentas.get("c1_doc"), placeholder="Ej: V-12345678", key="doc1")
            else: doc_1 = st.text_input("RIF Cuenta Beneficiario (C1):", value=r_prov if r_prov else val_cuentas.get("c1_doc"), key="doc1")
        n_cta_1 = st.text_input("N° Cuenta Nacional - 20 dígitos (C1):", value=val_cuentas.get("c1_num"), max_chars=20, key="n_cta1")

        st.write("---")
        activar_c2 = st.checkbox("➕ ¿Registrar Canal Bancario Adicional N° 2 para este Proveedor?", value=True if val_cuentas.get("c2_num") else False, key="chk_act_c2")
        bco_2, ben_2, t_ben_2, doc_2, n_cta_2 = "Otros", "", "Empresa (RIF)", "", ""
        if activar_c2:
            st.markdown("**[CANAL BANCARIO N° 2 Opcional]**")
            cb2_1, cb2_2, cb2_3, cb2_4 = st.columns([1, 1, 0.8, 1.2])
            with cb2_1: bco_2 = st.selectbox("Banco Destino (C2):", BCOS_LISTA_REAL, index=BCOS_LISTA_REAL.index(val_cuentas.get("c2_bco")) if val_cuentas.get("c2_bco") in BCOS_LISTA_REAL else 0, key="bco2")
            with cb2_2: ben_2 = st.text_input("Nombre Beneficiario Pago (C2):", value=val_cuentas.get("c2_ben"), key="ben2")
            with cb2_3: t_ben_2 = st.selectbox("Tipo Documento (C2):", ["Empresa (RIF)", "Persona Natural (Cédula)"], index=0 if val_cuentas.get("c2_tipo") == "Empresa (RIF)" else 1, key="t_ben2")
            with cb2_4:
                if t_ben_2 == "Persona Natural (Cédula)": doc_2 = st.text_input("Cédula de Identidad del Beneficiario (C2):", value=val_cuentas.get("c2_doc"), key="doc2")
                else: doc_2 = st.text_input("RIF Cuenta Beneficiario (C2):", value=val_cuentas.get("c2_doc"), key="doc2")
            n_cta_2 = st.text_input("N° Cuenta Nacional - 20 dígitos (C2):", value=val_cuentas.get("c2_num"), max_chars=20, key="n_cta2")

        st.write("---")
        activar_c3 = st.checkbox("➕ ¿Registrar Canal Bancario Adicional N° 3 para este Proveedor?", value=True if val_cuentas.get("c3_num") else False, key="chk_act_c3")
        bco_3, ben_3, t_ben_3, doc_3, n_cta_20_3 = "Otros", "", "Empresa (RIF)", "", ""
        if activar_c3:
            st.markdown("**[CANAL BANCARIO N° 3 Opcional]**")
            cb3_1, cb3_2, cb3_3, cb3_4 = st.columns([1, 1, 0.8, 1.2])
            with cb3_1: bco_3 = st.selectbox("Banco Destino (C3):", BCOS_LISTA_REAL, index=BCOS_LISTA_REAL.index(val_cuentas.get("c3_bco")) if val_cuentas.get("c3_bco") in BCOS_LISTA_REAL else 0, key="bco3")
            with cb3_2: ben_3 = st.text_input("Nombre Beneficiario Pago (C3):", value=val_cuentas.get("c3_ben"), key="ben3")
            with cb3_3: t_ben_3 = st.selectbox("Tipo Documento (C3):", ["Empresa (RIF)", "Persona Natural (Cédula)"], index=0 if val_cuentas.get("c3_tipo") == "Empresa (RIF)" else 1, key="t_ben3")
            with cb3_4:
                if t_ben_3 == "Persona Natural (Cédula)": doc_3 = st.text_input("Cédula de Identidad del Beneficiario (C3):", value=val_cuentas.get("c3_doc"), key="doc3")
                else: doc_3 = st.text_input("RIF Cuenta Beneficiario (C3):", value=val_cuentas.get("c3_doc"), key="doc3")
            n_cta_20_3 = st.text_input("N° Cuenta Nacional - 20 dígitos (C3):", value=val_cuentas.get("c3_num"), max_chars=20, key="n_cta3")

        st.write("##### 4. Checklist Contable y Notas de Soportes")
        chks = {}; notas_checks = {}
        for lbl, k in RECAUDOS_GLOBAL:
            c_col1, c_col2 = st.columns(2)
            with c_col1: chks[k] = st.checkbox(f"Entregó: {lbl}", value=val_soportes.get(k, False), key=f"chk_{k}")
            with c_col2: notas_checks[k] = st.text_input(f"Nota de planta para: {lbl[:20]}...", value=val_notas_marginales.get(k, ""), placeholder="Ej: (Enviaron 1)", key=f"not_{k}")

        obs_compras = st.text_area("Observaciones de Control Contable Marginales:", value=val_notas, key="obs_main")
        if st.button("⚙️ Procesar Certificación y Grabar Registro en Matriz", use_container_width=True, key="btn_grabar_matriz"):
            n_cta_cleaned = "".join(n_cta_1.split()).replace("-", "")
            if len(n_cta_cleaned) != 20: st.error("❌ ERROR: La cuenta 1 debe poseer exactamente 20 dígitos.")
            else:
                ahora_str = datetime.now().strftime("%d/%m/%Y %I:%M %p")
                res_soportes = {k: chks[k] for k in chks}
                res_notas_marginales = {k: notas_checks[k].strip() for k in notas_checks}
                txt_faltantes = ", ".join([lbl for lbl, k in RECAUDOS_GLOBAL if not chks[k]]) if [lbl for lbl, k in RECAUDOS_GLOBAL if not chks[k]] else "Ninguno"
                estatus_final = "Pendiente por Soportes" if txt_faltantes != "Ninguno" else "Aprobado"
                
                cuentas_dict = {"c1_bco": bco_1, "c1_ben": ben_1, "c1_tipo": t_ben_1, "c1_doc": doc_1, "c1_num": n_cta_cleaned, "c2_bco": bco_2, "c2_ben": ben_2, "n_cta_2": n_cta_2, "c3_bco": bco_3, "c3_ben": ben_3, "n_cta_3": n_cta_3}
                ret_iva_val = "75%" if tipo_sujeto_sel == "Sujeto Pasivo Especial (Especial)" else "0%"
                ret_islr_val = "2.0%" if tipo_sujeto_sel == "Sujeto Pasivo Especial (Especial)" else "1.0%"
                
                # Inyección binaria persistente en la matriz de la bitácora
                nuevo_registro = {"Fecha/Hora": ahora_str, "Código": int(c_prov), "Proveedor": n_prov.upper(), "Rif_Prov": r_prov.upper(), "Contacto": p_cont, "Correo": e_prov, "Teléfono": t_prov, "Tipo": tipo_prov, "Elaborado Por": persona_elabora, "Soportes": res_soportes, "Notas_Marginales": res_notas_marginales, "Notas": obs_compras, "Faltantes": txt_faltantes, "Estatus": estatus_final, "Cuentas_Bancarias": cuentas_dict, "Ret_Iva": ret_iva_val, "Ret_Islr": ret_islr_val, "Contribuyente": tipo_sujeto_sel}
                
                match_existente = next((idx for idx, item in enumerate(st.session_state["bitacora_db"]) if item["Código"] == int(c_prov)), None)
                if match_existente is not None: st.session_state["bitacora_db"][match_existente] = nuevo_registro
                else: st.session_state["bitacora_db"].append(nuevo_registro)

                # RENDERIZADO DE LA PLANILLA FISCAL CALCADA EN PANTALLA (FORMATO REAL TERMO SERVICIOS 792)
                html_rep_inf_temp = f"""
                <div style="background-color:#FFFFFF; padding:35px; border:2px solid #1E5A34; max-width:750px; margin:10px auto; color:#000000; font-family:Arial, sans-serif;">
                    <div style="width:100%; border-bottom:3px solid #1E5A34; padding-bottom:10px; margin-bottom:20px; text-align:center;">
                        <h2 style="color:#1E5A34; margin:0; font-size:24px; font-weight:bold; letter-spacing:-0.5px;">FRIGORÍFICO INDUSTRIAL TURMERO C.A.</h2>
                        <p style="margin:4px 0 0 0; font-size:12px; color:#4B5563; font-style:italic;">Carne de excelente calidad a precio justo...</p>
                    </div>
                    <h4 style="text-align:center; font-weight:bold; text-transform:uppercase; margin-top:25px; margin-bottom:25px; font-size:14px; color:#111827; letter-spacing:0.5px;">PLANILLA DE RECAUDOS PARA LA CREACIÓN O REGISTRO DEL PROVEEDORES.</h4>
                    <div style="background-color:#F9FAFB; padding:15px; border:1px solid #E5E7EB; border-radius:4px; font-size:13px; line-height:1.6; margin-bottom:25px;">
                        <b>Nombre del Proveedor:</b> {n_prov.upper()}<br/>
                        <b>Código del Proveedor:</b> {c_prov}<br/>
                        <b>RIF Comercial:</b> {r_prov.upper()}<br/>
                        <b>Calificación Fiscal:</b> {tipo_sujeto_sel}
                    </div>
                    <table style="width:100%; border-collapse:collapse; margin-top:15px; font-size:12px;">
                        <tbody>
                """
                for lbl, k in RECAUDOS_GLOBAL:
                    marca_status = ""
                    if res_soportes.get(k):
                        # Lógica estricta de marcas de tu hoja: fila IVA estampa ✓ verde, el resto estampa X negra
                        marca_status = '<span style="color:#1E5A34; font-weight:bold; font-size:16px;">✓</span>' if k == "d_iva" else '<span style="color:#000000; font-weight:bold; font-size:13px;">X</span>'
                    
                    nota_marginal_txt = f" <span style='color:#000000; font-style:normal; font-weight:bold; font-size:12px; margin-left:8px;'>({res_notas_marginales.get(k)})</span>" if res_notas_marginales.get(k) else ""
                    
                    html_rep_inf_temp += f"""
                            <tr>
                                <td style="border:1px solid #000000; padding:8px; text-align:center; width:8%; font-size:14px; background-color:#FFFFFF;">{marca_status}</td>
                                <td style="border:1px solid #000000; padding:8px; color:#000000; font-size:13px;">{lbl}{nota_marginal_txt}</td>
                            </tr>
                    """
                html_rep_inf_temp += f"""
                        </tbody>
                    </table>
                    <div style="margin-top:60px; text-align:right; font-size:14px; font-family: Arial, sans-serif; color:#000000; line-height:1.6;">
                        Registrado por:<br/>
                        <span style="font-weight:bold; font-size:15px; border-bottom:1px solid #000000; padding-bottom:2px;">{persona_elabora}</span><br/>
                        Fecha: {datetime.now().strftime('%d/%m/%Y')}<br/>
                        Hora: {datetime.now().strftime('%I:%M %p')}
                    </div>
                </div>
                """
                st.session_state["reporte_html_temp"] = html_rep_inf_temp
                st.session_state["codigo_temp"] = c_prov; st.session_state["mostrar_botones_cierre"] = True
                st.success("✅ REGISTRO MAESTRO PROCESADO CON ÉXITO.")
                st.rerun()

        if st.session_state.get("mostrar_botones_cierre") and st.session_state.get("reporte_html_temp"):
            st.write("---")
            st.markdown(st.session_state["reporte_html_temp"], unsafe_allow_html=True)
            c_bl1, c_b2 = st.columns(2)
            pdf_bytes_reporte_directo = io.BytesIO(st.session_state["reporte_html_temp"].encode('utf-8')).getvalue()
            c_bl1.download_button("📥 DESCARGAR COMPROBANTE DE PLANILLA (.PDF)", data=pdf_bytes_reporte_directo, file_name=f"FITCA_CHECKLIST_{st.session_state['codigo_temp']}.pdf", mime="application/pdf", use_container_width=True, key="dl_directa_v5")
            if c_b2.button("🖨️ EMITIR IMPRESIÓN FÍSICA DIRECTA", use_container_width=True, key="print_direct_final_btn"): st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

    elif opcion_menu == "📊 Informes":
        st.write("#### 📊 CONSULTA DE REPORTES Y AUDITORÍA INTEGRAL DE EXPEDIENTES")
        if len(st.session_state.get("bitacora_db", [])) > 0:
            df_provs = pd.DataFrame(st.session_state["bitacora_db"])
            st.dataframe(df_provs[["Código", "Proveedor", "Rif_Prov", "Faltantes", "Estatus"]], use_container_width=True, hide_index=True)
            list_options = df_provs.apply(lambda row: f"{row['Código']} - {row['Proveedor']}", axis=1).tolist()
            selected_prov = st.selectbox("📋 Seleccione el Expediente a Consultar:", list_options, key="select_prov_informe")
            codigo_sel = int(selected_prov.split(" - ").strip()) if selected_prov else None
            reg_sel = next((item for item in st.session_state["bitacora_db"] if item["Código"] == codigo_sel), None) if codigo_sel else None

            if reg_sel:
                st.markdown(f"**Proveedor:** {reg_sel['Proveedor']} | **RIF:** {reg_sel['Rif_Prov']} | **Calificación SENIAT:** `{reg_sel.get('Contribuyente')}`")
                c_maps = reg_sel.get('Cuentas_Bancarias', {})
                st.markdown(f"**C1 Principal:** Banco: {c_maps.get('c1_bco')} | Beneficiario: {c_maps.get('c1_ben')} | N° Cuenta: `{c_maps.get('c1_num')}`")
                st.markdown(f"""<div style="background-color:#FFF3CD; padding:12px; border-left:5px solid #FFA000; color:#856404; font-family:monospace; font-size:12px;">⚠️ <b>DOCUMENTOS RECAUDOS FALTANTES DETECTADOS:</b> {reg_sel['Faltantes']}</div>""", unsafe_allow_html=True)

                st.write("---")
                st.write("##### 📄 Planilla Calcada de Formato de Planta (Modelo Termo Servicios)")
                
                html_rep_inf = f"""
                <div style="background-color:#FFFFFF; padding:35px; border:2px solid #1E5A34; max-width:750px; margin:10px auto; color:#000000; font-family:Arial, sans-serif;">
                    <div style="width:100%; border-bottom:3px solid #1E5A34; padding-bottom:10px; margin-bottom:20px; text-align:center;">
                        <h2 style="color:#1E5A34; margin:0; font-size:24px; font-weight:bold; letter-spacing:-0.5px;">FRIGORÍFICO INDUSTRIAL TURMERO C.A.</h2>
                        <p style="margin:4px 0 0 0; font-size:12px; color:#4B5563; font-style:italic;">Carne de excelente calidad a precio justo...</p>
                    </div>
                    <h4 style="text-align:center; font-weight:bold; text-transform:uppercase; margin-top:20px; margin-bottom:25px; font-size:14px; color:#111827; letter-spacing:0.5px;">PLANILLA DE RECAUDOS PARA LA CREACIÓN O REGISTRO DEL PROVEEDORES.</h4>
                    <div style="background-color:#F9FAFB; padding:15px; border:1px solid #E5E7EB; border-radius:4px; font-size:13px; line-height:1.6; margin-bottom:25px;">
                        <b>Nombre del Proveedor:</b> {reg_sel['Proveedor']}<br/>
                        <b>Código del Proveedor:</b> {reg_sel['Código']}<br/>
                        <b>RIF Comercial:</b> {reg_sel['Rif_Prov']}<br/>

