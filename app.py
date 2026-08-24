import streamlit as st
import io, os, pandas as pd
from datetime import datetime
import base64

st.set_page_config(page_title="FITCA - Gestión de Proveedores v5.0", page_icon="🏢", layout="wide")

st.markdown("<style>.stApp { background-color: #F4F5F7 !important; font-family: sans-serif !important; }.login-container { max-width: 320px; margin: 100px auto; background-color: #FFFFFF; padding: 25px; border-radius: 4px; border-top: 5px solid #1E5A34; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #D1D5DB; }.fitca-header-box { background-color: #FFFFFF !important; padding: 12px 20px !important; border-radius: 3px !important; border-left: 6px solid #1E5A34 !important; border-bottom: 1px solid #E5E7EB !important; margin-bottom: 20px !important; }.main-title { font-size:20px !important; font-weight:700 !important; color:#1E5A34 !important; text-transform: uppercase; }.sub-title { font-size:11px !important; color:#4B5563 !important; font-family: monospace !important; font-weight: 600; }div.stButton > button:first-child { background-color: #1E5A34 !important; color: #FFFFFF !important; border: 1px solid #1E5A34 !important; font-weight: 600 !important; border-radius: 3px !important; width: 100% !important; }.sidebar-user { background-color:#F9FAFB; padding:10px 12px; border-radius:3px; border-left:4px solid #1E5A34; font-size:12px; color:#1E5A34; font-family: monospace; }</style>", unsafe_allow_html=True)

BCOS_LISTA_REAL = ["0102 - Banco de Venezuela (BDV)", "0163 - Banco del Tesoro", "0175 - Banco Digital de los Trabajadores (BDT)", "0134 - Banesco Banco Universal", "0105 - Mercantil Banco", "0108 - BBVA Provincial", "0191 - Banco Nacional de Crédito (BNC)", "0172 - Bancamiga Banco Universal", "Otros"]
RECAUDOS_GLOBAL = [("Copia del Registro Mercantil", "mer"), ("Copia del Registro de Información Fiscal (RIF)", "rif"), ("Copia de la Cédula de Identidad", "ced"), ("Licencia de Actividades Económicas", "lic"), ("Suministros de Datos Bancarios", "db"), ("Declaración de IVA", "d_iva"), ("Declaración de ISLR", "d_islr")]

if "usuarios_db" not in st.session_state: st.session_state["usuarios_db"] = [{"nombre": "Juan Carlos", "apellido": "Reyes", "usuario": "supervisor", "clave": "fitca2026", "rol": "Contabilidad"}]
if "empresa_db" not in st.session_state: st.session_state["empresa_db"] = {"rs": "FRIGORÍFICO INDUSTRIAL TURMERO C.A. (FITCA)", "rif": "J-00015198-9", "dir": "Calle Las Industrias, Turmero, Edo. Aragua.", "tel": "0244-3214567", "logo_bytes": None}
if "bitacora_db" not in st.session_state: st.session_state["bitacora_db"] = []
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 12px; font-weight: 700; color: #1E5A34; text-align: center; font-family:monospace;">FITCA — SGP v5.0</p>', unsafe_allow_html=True)
    u_ing = st.text_input("Usuario Master:", key="u_log_input")
    c_ing = st.text_input("Clave Sistema:", type="password", key="p_log_input")
    if st.button("🔒 Autenticar Firma"):
        u_f = next((u for u in st.session_state["usuarios_db"] if u["usuario"] == u_ing and u["clave"] == c_ing), None)
        if u_f: st.session_state["autenticado"] = True; st.session_state["usuario_actual"] = u_f; st.rerun()
        else: st.error("❌ Credenciales inválidas.")
    st.markdown('</div>', unsafe_allow_html=True)
else:
    emp, u_info = st.session_state["empresa_db"], st.session_state["usuario_actual"]
    persona_elabora = f"{u_info['nombre']} {u_info['apellido']}"
    
    with st.sidebar:
        st.markdown(f'<div class="sidebar-user"><b>⚙️ ERP CONTROL:</b><br/>{persona_elabora}<br/><b>Rol:</b> {u_info["rol"]}</div>', unsafe_allow_html=True)
        opcion_menu = st.selectbox("📂 Módulos", ["Planilla de Solicitudes", "📊 Informes", "⚙️ Configuración"])
        if st.button("🚪 Cerrar Sesión Segura"): st.session_state["autenticado"] = False; st.rerun()
            
    st.markdown(f'<div class="fitca-header-box"><p class="main-title">{emp["rs"]}</p><p class="sub-title">RIF: {emp["rif"]} | PLANTA: {emp["dir"]}</p></div>', unsafe_allow_html=True)

    if opcion_menu == "⚙️ Configuración":
        st.write("#### ⚙️ PANEL DE CONFIGURACIÓN")
        new_rs = st.text_input("Razón Social:", value=emp["rs"])
        new_rif = st.text_input("RIF:", value=emp["rif"])
        if st.button("💾 Guardar Parámetros de Planta"):
            emp["rs"], emp["rif"] = new_rs, new_rif
            st.success("✅ Guardado."); st.rerun()

    elif opcion_menu == "Planilla de Solicitudes":
        st.write("#### 📝 PLANILLA DE REGISTRO PREVIO")
        c_prov = st.number_input("Código Maestro Proveedor Interno:", value=820, step=1)
        n_prov = st.text_input("Nombre o Razón Social Comercial Completa:")
        r_prov = st.text_input("Número de RIF Comercial:")
        tipo_sujeto_sel = st.selectbox("Calificación Fiscal:", ["Sujeto Pasivo Especial (Especial)", "Contribuyente Ordinario"])
        venc_rif_date = st.date_input("Fecha de Vencimiento Legal del RIF:")
        
        st.markdown("**[CANAL BANCARIO N° 1]**")
        bco_1 = st.selectbox("Banco Destino (C1):", BCOS_LISTA_REAL)
        ben_1 = st.text_input("Nombre Beneficiario Pago (C1):")
        n_cta_1 = st.text_input("N° Cuenta Nacional - 20 dígitos (C1):", max_chars=20)
        
        st.write("##### 4. Checklist Contable y Soportes")
        chks = {}; files_bytes = {}; documentos_faltantes = []
        for lbl, k in RECAUDOS_GLOBAL:
            chks[k] = st.checkbox(f"Entregó: {lbl}", key=f"chk_{k}")
            f_up = st.file_uploader(f"Cargar {lbl}:", type=["pdf","png","jpg","jpeg"], key=f"f_{k}")
            if chks[k] and f_up: files_bytes[f"{k}_b"] = f_up.read(); files_bytes[f"{k}_n"] = f_up.name
            if not chks[k]: documentos_faltantes.append(lbl)

        if st.button("⚙️ Procesar Certificación y Grabar Registro en Matriz"):
            n_cta_cleaned = "".join(n_cta_1.split()).replace("-", "")
            if len(n_cta_cleaned) != 20: st.error("❌ La cuenta 1 debe poseer exactamente 20 dígitos.")
            else:
                ahora_str = datetime.now().strftime("%d/%m/%Y %I:%M %p")
                es_rif_vencido = venc_rif_date < datetime.now().date()
                estatus_final = "Alerta Fiscal" if es_rif_vencido else ("Pendiente por Soportes" if documentos_faltantes else "Aprobado")
                ret_iva_val = "75%" if tipo_sujeto_sel == "Sujeto Pasivo Especial (Especial)" else "0%"
                ret_islr_val = "2.0%" if tipo_sujeto_sel == "Sujeto Pasivo Especial (Especial)" else "1.0%"
                
                nuevo_registro = {"Fecha/Hora": ahora_str, "Código": int(c_prov), "Proveedor": n_prov.upper(), "Rif_Prov": r_prov.upper(), "Vencimiento_Rif": str(venc_rif_date), "Soportes": {k: chks[k] for k in chks}, "Faltantes": ", ".join(documentos_faltantes) if documentos_faltantes else "Ninguno", "Estatus": estatus_final, "Cuentas_Bancarias": {"c1_bco": bco_1, "c1_ben": ben_1, "c1_num": n_cta_cleaned}, "Ret_Iva": ret_iva_val, "Ret_Islr": ret_islr_val, "Contribuyente": tipo_sujeto_sel, "Elaborado Por": persona_elabora}
                st.session_state["bitacora_db"].append(nuevo_registro)
                
                html_rep = f'<div style="background-color:#FFFFFF; padding:25px; border:2px solid #1E5A34; color:#000000; font-family:Arial;"><h3 style="color:#1E5A34; margin:0;">FRIGORÍFICO INDUSTRIAL TURMERO C.A.</h3><h4>PLANILLA DE RECAUDOS PROVEEDOR</h4><b>Proveedor:</b> {n_prov.upper()}<br/><b>Código:</b> {c_prov}<br/><b>RIF:</b> {r_prov.upper()}<br/><b>Estatus:</b> {estatus_final.upper()}<br/><b>Calificación:</b> {tipo_sujeto_sel}<br/><br/><table style="width:100%; border-collapse:collapse;">'
                for lbl, k in RECAUDOS_GLOBAL:
                    m = "✓" if (k == "d_iva" and chks[k]) else ("X" if chks[k] else " ")
                    html_rep += f'<tr><td style="border:1px solid #D1D5DB; text-align:center; font-weight:bold; width:10%; font-size:14px;">{m}</td><td style="border:1px solid #D1D5DB; padding:5px;">{lbl}</td></tr>'
                html_rep += f'</table><br/><p style="font-size:11px;">Registrado por: {persona_elabora} | Firma Analista: ___________________ | Firma Gerencia: ___________________</p></div>'
                st.session_state["reporte_html_temp"] = html_rep; st.success("✅ PROCESADO CON ÉXITO."); st.rerun()

        if st.session_state.get("reporte_html_temp"):
            st.write("---"); st.markdown(st.session_state["reporte_html_temp"], unsafe_allow_html=True)
            pdf_bytes = io.BytesIO(st.session_state["reporte_html_temp"].encode('utf-8')).getvalue()
            st.download_button("📥 DESCARGAR COMPROBANTE (.PDF)", data=pdf_bytes, file_name="FITCA_COMPROBANTE.pdf", mime="application/pdf", use_container_width=True)

    elif opcion_menu == "📊 Informes":
        st.write("#### 📊 CONSULTA DE REPORTES Y AUDITORÍA INTEGRAL")
        if len(st.session_state["bitacora_db"]) > 0:
            df_provs = pd.DataFrame(st.session_state["bitacora_db"])
            st.dataframe(df_provs[["Código", "Proveedor", "Rif_Prov", "Faltantes", "Estatus"]], use_container_width=True, hide_index=True)
            list_options = df_provs.apply(lambda row: f"{row['Código']} - {row['Proveedor']}", axis=1).tolist()
            selected_prov = st.selectbox("🔍 Seleccione Acreedor:", list_options)
            codigo_sel = int(selected_prov.split(" - ")[0])
            reg_sel = next((item for item in st.session_state["bitacora_db"] if item["Código"] == codigo_sel), None)
            
            if reg_sel:
                if reg_sel['Estatus'] == "Alerta Fiscal": st.error(f"⚠️ **ALERTA FISCAL CRÍTICA:** RIF vencido ({reg_sel.get('Vencimiento_Rif')}).")
                st.markdown(f"**Proveedor:** {reg_sel['Proveedor']} | **RIF:** {reg_sel['Rif_Prov']} | **Calificación SENIAT:** {reg_sel.get('Contribuyente')}")
                st.markdown(f"⚠️ **PENDIENTES AUDITORÍA:** {reg_sel['Faltantes']}")
                
                html_rep_inf = f"""
                <div style="background-color:#FFFFFF; padding:35px; border:2px solid #1E5A34; max-width:750px; margin:10px auto; color:#000000; font-family:Arial, sans-serif;">
                    <div style="width:100%; border-bottom:3px solid #1E5A34; padding-bottom:10px; margin-bottom:20px; overflow:hidden;">
                        <h2 style="color:#1E5A34; margin:0; font-size:22px; font-weight:bold; letter-spacing:-0.5px;">FRIGORÍFICO INDUSTRIAL TURMERO C.A.</h2>
                        <p style="margin:2px 0 0 0; font-size:11px; color:#4B5563; font-family:monospace;">Carne de excelente calidad a precio justo...</p>
                    </div>
                    <h4 style="text-align:center; font-weight:bold; text-transform:uppercase; margin-top:25px; margin-bottom:25px; font-size:14px; color:#111827;">PLANILLA DE RECAUDOS PARA LA CREACIÓN O REGISTRO DEL PROVEEDOR</h4>
                    <div style="background-color:#F9FAFB; padding:15px; border:1px solid #E5E7EB; border-radius:4px; font-size:13px; line-height:1.6; margin-bottom:25px;">
                        <b>Nombre del Proveedor:</b> {reg_sel['Proveedor']}<br/>
                        <b>Código del Proveedor:</b> {reg_sel['Código']}<br/>
                        <b>RIF Comercial:</b> {reg_sel['Rif_Prov']}<br/>
                        <b>Estatus Legal de Planta:</b> {reg_sel['Estatus'].upper()}<br/>
                        <b>Calificación Fiscal:</b> {reg_sel.get('Contribuyente', 'Sujeto Pasivo Especial')}
                    </div>
                    <table style="width:100%; border-collapse:collapse; margin-top:15px; font-size:12px;">
                        <thead>
                            <tr style="background-color:#1E5A34; color:#FFFFFF; text-transform:uppercase; font-size:11px;">
                                <th style="border:1px solid #1E5A34; padding:8px; width:12%; text-align:center;">ESTATUS</th>
                                <th style="border:1px solid #1E5A34; padding:8px; text-align:left;">RECAUDO CONTABLE OBLIGATORIO</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                for lbl, k in RECAUDOS_GLOBAL:
                    m_inf = ""
                    if reg_sel.get('Soportes', {}).get(k): 
                        m_inf = "✓" if k == "d_iva" else "X"
                    
                    html_rep_inf += f"""
                            <tr>
                                <td style="border:1px solid #D1D5DB; padding:7px; text-align:center; font-weight:bold; color:{"#1E5A34" if reg_sel.get('Soportes', {}).get(k) and k=='d_iva' else "#000000"}; background-color:{"#F3FBF7" if reg_sel.get('Soportes', {}).get(k) else "#FFFFFF"}; font-size:14px;">{m_inf}</td>
                                <td style="border:1px solid #D1D5DB; padding:7px; color:#111827;">{lbl}</td>
                            </tr>
                    """
                html_rep_inf += f"""
                        </tbody>
                    </table>
                    <table style="width:100%; margin-top:60px; border-collapse:collapse; font-size:11px; font-family:monospace; color:#4B5563;">
                        <tr>
                            <td style="width:45%; vertical-align:top; border-top:1px solid #9CA3AF; padding-top:8px;">
                                Registrado por: <br/><b>{reg_sel['Elaborado Por']}</b><br/>Firma Analista: _____________________<br/>Fecha/Hora: {reg_sel['Fecha/Hora']}
                            </td>
                            <td style="width:10%;"></td>
                            <td style="width:45%; vertical-align:top; border-top:1px solid #9CA3AF; padding-top:8px; text-align:right;">
                                Aprobado por: <br/><br/>Firma de Gerencia de Planta: _____________________
                            </td>
                        </tr>
                    </table>
                </div>
                """
                st.markdown(html_rep_inf, unsafe_allow_html=True)
                pdf_bytes_inf = io.BytesIO(html_rep_inf.encode('utf-8')).getvalue()
                st.download_button("📥 DESCARGAR REPORTE FISCAL COMPLETADO (.PDF)", data=pdf_bytes_inf, file_name=f"FITCA_CHECKLIST_{codigo_sel}.pdf", mime="application/pdf", use_container_width=True)
        else:
            st.info("📭 Base de datos vacía.")

    elif opcion_menu == "📊 Bitácora de Auditoría":
        st.title("📊 Traza e Indicadores de Auditoría (SGP)")
        if u_info["rol"] == "Contabilidad":
            if len(st.session_state.get("bitacora_db", [])) > 0:
                df_m = pd.DataFrame(st.session_state["bitacora_db"])
                b1, b2 = st.columns(2)
                b1.metric("📁 TOTAL EXPEDIENTES PROCESADOS", len(df_m))
                b2.metric("🟢 CERTIFICACIONES EMITIDAS", len(df_m[df_m["Estatus"]=="Aprobado"]))
                st.write("---")
                st.dataframe(df_m[["Fecha/Hora", "Código", "Proveedor", "Rif_Prov", "Estatus", "Elaborado Por"]], use_container_width=True, hide_index=True)
            else:
                st.info("📭 Vacía.")
        else:
            st.error("🔒 ACCESO RESTRINGIDO: Reclama nivel de Supervisor Contable.")

try:
    host_verificador = os.environ.get("HOSTNAME", "FITCA_MAIN_SERVER")
    token_autenticidad = base64.b64encode(host_verificador.encode()).decode()
    if not token_autenticidad:
        st.error("🔒 VIOLACIÓN DE LICENCIA: Aplicación bloqueada.")
        st.stop()
except Exception:
    pass
