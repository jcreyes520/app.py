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
    .stApp { background-color: #F4F5F7 !important; font-family: 'Segoe UI', sans-serif !important; }
    .login-container { max-width: 320px; margin: 100px auto; background-color: #FFFFFF; padding: 25px; border-radius: 4px; border-top: 5px solid #1E5A34; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #D1D5DB; }
    .fitca-header-box { background-color: #FFFFFF !important; padding: 12px 20px !important; border-radius: 3px !important; border-left: 6px solid #1E5A34 !important; border-bottom: 1px solid #E5E7EB !important; margin-bottom: 20px !important; width: 100% !important; }
    .main-title { font-size:20px !important; font-weight:700 !important; color:#1E5A34 !important; text-transform: uppercase; margin:0px !important; }
    .sub-title { font-size:11px !important; color:#4B5563 !important; margin-top:3px !important; font-family: monospace !important; font-weight: 600; }
    div.stButton > button:first-child { background-color: #1E5A34 !important; color: #FFFFFF !important; border: 1px solid #1E5A34 !important; font-weight: 600 !important; font-size: 12.5px !important; border-radius: 3px !important; width: 100% !important; }
    div.stButton > button:first-child:hover { background-color: #153E20 !important; border-color: #153E20 !important; }
    .sidebar-user { background-color:#F9FAFB; padding:10px 12px; border-radius:3px; border-left:4px solid #1E5A34; font-size:12px; color:#1E5A34; font-family: monospace; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #FFFFFF !important; border: 1px solid #C4C7CC !important; border-radius: 3px !important; padding: 3px 6px !important; font-size: 12.5px !important; }
    div[data-testid='stSelectbox'] { width: 100% !important; }
    </style>
""", unsafe_allow_html=True)

# 📑 LISTA MAESTRA DE LAS ENTIDADES BANCARIAS VENEZOLANAS CON SINTAXIS REVISADA
BCOS_LISTA_REAL = [
    "0102 - Banco de Venezuela (BDV)", "0163 - Banco del Tesoro", "0175 - Banco Digital de los Trabajadores (BDT)",
    "0177 - Banco de la Fuerza Armada Nacional Bolivariana (BANFANB)", "0166 - Banco Agrícola de Venezuela",
    "0134 - Banesco Banco Universal", "0105 - Mercantil Banco", "0108 - BBVA Provincial", "0191 - Banco Nacional de Crédito (BNC)",
    "0172 - Bancamiga Banco Universal", "0114 - BanCaribe", "0115 - Banco Exterior", "0138 - Banco Plaza", 
    "0151 - Banco Fondo Común (BFC)", "0174 - Banplus", "0104 - Banco Venezolano de Crédito (BVC)", "0128 - Banco Caroní",
    "0157 - Banco del Sur", "0171 - Banco Activo", "0137 - Banco Sofitasa", "0156 - 100% Banco", 
    "0001 - Banco Central de Venezuela (BCV)", "0146 - Bangente", "0168 - Bancrecer", "0169 - Mi Banco", 
    "0182 - N58 Banco Digital", "Otros (Internacional / Cuenta Extranjera)"
]

# 📑 LISTA MAESTRA DE LOS 12 RECAUDOS EXHAUSTIVOS DE LA PLANILLA FÍSICA IMPRESA
RECAUDOS_GLOBAL = [
    ("Copia del Registro Mercantil.", "mer"), ("Copia del Registro de Información Fiscal (RIF).", "rif"),
    ("Copia de la Cédula de Identidad del Accionista.", "ced"), ("Licencia de Actividades Económicas.", "lic"),
    ("Cartas de Referencias Comerciales (Mínimo 2).", "ref_c"), ("Cartas de Referencias Bancarias (Mínimo 2).", "ref_b"),
    ("Suministros de Datos Bancarios para realizar pagos en cuentas nacionales.", "db"), ("Persona Contacto.", "p_cont"),
    ("Correo Electrónico.", "email"), ("Permiso sanitario y/o INSAI de los productos (Si aplica)", "san"),
    ("Declaración de IVA del 16-03-2026 al 31-03-2026.", "d_iva"), ("Declaración Definitiva de ISLR del 01-01-2025 al 31-12-2025.", "d_islr")
]

if "usuarios_db" not in st.session_state:
    st.session_state["usuarios_db"] = [{"nombre": "Juan Carlos", "apellido": "Reyes", "usuario": "supervisor", "clave": "fitca2026", "rol": "Contabilidad"}]
if "empresa_db" not in st.session_state: st.session_state["empresa_db"] = {"rs": "FRIGORÍFICO INDUSTRIAL TURMERO C.A. (FITCA)", "rif": "J-00015198-9", "dir": "Calle Las Industrias, Turmero, Edo. Aragua.", "tel": "0244-3214567", "logo_bytes": None}
if "bitacora_db" not in st.session_state: st.session_state["bitacora_db"] = []
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 12px; font-weight: 700; color: #1E5A34; text-align: center; font-family:monospace;">FITCA — SGP v5.0</p>', unsafe_allow_html=True)
    u_ing = st.text_input("Usuario Master:", key="u_ing_usr")
    c_ing = st.text_input("Clave Sistema:", type="password", key="c_ing_clv")
    if st.button("🔒 Autenticar Firma"):
        u_f = next((u for u in st.session_state["usuarios_db"] if u["usuario"] == u_ing and u["clave"] == c_ing), None)
        if u_f: st.session_state["autenticado"] = True; st.session_state["usuario_actual"] = u_f; st.rerun()
        else: st.error("❌ Credenciales inválidas.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    emp = st.session_state["empresa_db"]
    persona_elabora = f"{st.session_state['usuario_actual']['nombre']} {st.session_state['usuario_actual']['apellido']}"
    
    with st.sidebar:
        st.markdown(f'<div class="sidebar-user"><b>⚙️ ERP CONTROL:</b><br/>{persona_elabora}</div>', unsafe_allow_html=True)
        opcion_menu = st.selectbox("📂 Módulos del Sistema Central", ["Planilla de Solicitudes", "📊 Informes", "⚙️ Configuración"])
        if st.button("🚪 Cerrar Sesión Segura"): st.session_state["autenticado"] = False; st.rerun()
            
    st.markdown(f'<div class="fitca-header-box"><p class="main-title">{emp["rs"]}</p><p class="sub-title">RIF: {emp["rif"]} | PLANTA: {emp["dir"]}</p></div>', unsafe_allow_html=True)

    if opcion_menu == "⚙️ Configuración":
        st.write("#### ⚙️ PANEL DE CONFIGURACIÓN ADMINISTRATIVA")
        emp["rs"] = st.text_input("Razón Social:", value=emp["rs"])
        emp["rif"] = st.text_input("RIF:", value=emp["rif"])
        st.success("✅ Parámetros de planta actualizados.")

    elif opcion_menu == "Planilla de Solicitudes":
        st.write("#### 📝 PLANILLA DE REGISTRO PREVIO (ENTRADA DE DATOS)")
        c_prov = st.number_input("Código Maestro Proveedor Interno:", value=792, step=1)
        n_prov = st.text_input("Nombre o Razón Social Comercial Completa:", value="TERMO SERVICIOS R.W, C.A.")
        r_prov = st.text_input("Número de RIF Comercial:", value="J-31641325-1")
        tipo_sujeto_sel = st.selectbox("Calificación Fiscal:", ["Sujeto Pasivo Especial (Especial)", "Contribuyente Ordinario"])
        
        st.markdown("**[CANAL BANCARIO N° 1 - Principal Obligatorio]**")
        bco_1 = st.selectbox("Banco Destino (C1):", BCOS_LISTA_REAL)
        ben_1 = st.text_input("Nombre Beneficiario Pago (C1):", value="TERMO SERVICIOS R.W, C.A.")
        n_cta_1 = st.text_input("N° Cuenta Nacional - 20 dígitos (C1):", max_chars=20)
        
        st.write("##### 4. Checklist Contable y Notas de Soportes")
        chks = {}; notas_checks = {}; documentos_faltantes = []
        for lbl, k in RECAUDOS_GLOBAL:
            col1, col2 = st.columns(2)
            with col1: chks[k] = st.checkbox(f"Entregó: {lbl}", key=f"chk_{k}")
            with col2: notas_checks[k] = st.text_input(f"Nota para: {lbl[:20]}...", value="Enviaron 1" if k=="ref_b" else "", key=f"not_{k}")
            if not chks[k]: documentos_faltantes.append(lbl)

        obs_compras = st.text_area("Observaciones Generales de Control Contable:")

        if st.button("⚙️ Procesar Certificación y Grabar Registro en Matriz", use_container_width=True):
            n_cta_cleaned = "".join(n_cta_1.split()).replace("-", "")
            if len(n_cta_cleaned) != 20: st.error("❌ ERROR: La cuenta 1 debe poseer exactamente 20 dígitos.")
            else:
                ahora_str = datetime.now().strftime("%d/%m/%Y %I:%M %p")
                nuevo_registro = {"Fecha/Hora": ahora_str, "Código": int(c_prov), "Proveedor": n_prov.upper(), "Rif_Prov": r_prov.upper(), "Elaborado Por": persona_elabora, "Soportes": {k: chks[k] for k in chks}, "Notas_Marginales": {k: notas_checks[k].strip() for k in notas_checks}, "Faltantes": ", ".join(documentos_faltantes) if documentos_faltantes else "Ninguno", "Estatus": "Pendiente por Soportes" if documentos_faltantes else "Aprobado", "Cuentas_Bancarias": {"c1_bco": bco_1, "c1_ben": ben_1, "c1_num": n_cta_cleaned}}
                st.session_state["bitacora_db"].append(nuevo_registro)
                st.success("✅ PROCESADO CON ÉXITO Y REGISTRADO EN LA BITÁCORA CONTABLE.")

    elif opcion_menu == "📊 Informes":
        st.write("#### 📊 CONSULTA DE REPORTES Y AUDITORÍA INTEGRAL")
        if len(st.session_state["bitacora_db"]) > 0:
            df_provs = pd.DataFrame(st.session_state["bitacora_db"])
            st.dataframe(df_provs[["Código", "Proveedor", "Rif_Prov", "Faltantes", "Estatus"]], use_container_width=True, hide_index=True)
            
            list_options = df_provs.apply(lambda row: f"{row['Código']} - {row['Proveedor']}", axis=1).tolist()
            selected_prov = st.selectbox("📋 Seleccione el Expediente a Consultar:", list_options)
            codigo_sel = int(selected_prov.split(" - ")[0])
            reg_sel = next((item for item in st.session_state["bitacora_db"] if item["Código"] == codigo_sel), None)
            
            if reg_sel:
                st.markdown(f"**Proveedor:** {reg_sel['Proveedor']} | **RIF:** {reg_sel['Rif_Prov']}")

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

