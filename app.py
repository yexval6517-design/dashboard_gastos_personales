# -*- coding: utf-8 -*-
"""
DASHBOARD DE GASTOS PERSONALES - Versión Streamlit
Registra gastos y visualiza un dashboard con gráficos.
"""

from datetime import date, timedelta
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="Mi Dashboard de Gastos", page_icon="💰", layout="wide")

CATEGORIAS = ["Comida", "Transporte", "Compras_Hogar", "Entretenimiento",
              "Servicios", "Educación", "Otros"]
EMOJI = {'Comida': "🥝", "Transporte": "🚖", "Compras_Hogar": "🛒", "Entretenimiento": "🎵",
         "Servicios": "💰", "Educación": "📓", "Otros": "✔️"}

# ---------- Estado: usamos session_state para que los datos persistan entre acciones ----------
if "gastos" not in st.session_state:
    st.session_state.gastos = []

st.title("💰 Mi Dashboard de Gastos")
st.caption("Registra tus gastos o carga datos de ejemplo para explorar el dashboard.")

tab_registrar, tab_dashboard = st.tabs(["📝 Registrar gastos", "📊 Dashboard"])

# ============================================================
# PESTAÑA 1: REGISTRAR GASTOS
# ============================================================
with tab_registrar:
    col_form, col_tabla = st.columns([1, 2])

    with col_form:
        with st.form("form_gasto", clear_on_submit=True):
            fecha = st.date_input("Fecha", value=date.today())
            categoria = st.selectbox("Categoría", CATEGORIAS)
            monto = st.number_input("Monto ($)", min_value=0.0, step=1000.0)
            descripcion = st.text_input("Descripción (opcional)")
            enviado = st.form_submit_button("➕ Agregar gasto", use_container_width=True)

            if enviado:
                if monto <= 0:
                    st.warning("⚠️ Escribe un monto mayor a 0")
                else:
                    st.session_state.gastos.append({
                        "fecha": fecha.isoformat(),
                        "categoria": categoria,
                        "descripcion": descripcion.strip(),
                        "monto": float(monto)
                    })
                    st.success(f"✅ Agregado: ${monto:,.2f} en {categoria}")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📦 Cargar datos de ejemplo", use_container_width=True):
                rangos = {
                    "Comida": (60, 400), "Transporte": (15, 90), "Compras_Hogar": (100, 600),
                    "Entretenimiento": (60, 400), "Servicios": (150, 900),
                    "Educación": (50, 500), "Otros": (20, 200)
                }
                prob = [0.30, 0.20, 0.15, 0.13, 0.10, 0.07, 0.05]
                rng = np.random.default_rng(7)
                st.session_state.gastos.clear()
                dia = date.today() - timedelta(days=90)
                while dia <= date.today():
                    for _ in range(rng.integers(0, 3)):
                        cat = str(rng.choice(CATEGORIAS, p=prob))
                        val_min, val_max = rangos[cat]
                        st.session_state.gastos.append({
                            "fecha": dia.isoformat(), "categoria": cat,
                            "descripcion": "Simulación",
                            "monto": round(rng.uniform(val_min, val_max), 2)
                        })
                    dia += timedelta(days=1)
                st.rerun()
        with col_b:
            if st.button("🗑️ Borrar todo", use_container_width=True):
                st.session_state.gastos.clear()
                st.rerun()

    with col_tabla:
        st.subheader("Gastos registrados")
        if st.session_state.gastos:
            df_mostrar = pd.DataFrame(st.session_state.gastos).sort_values("fecha", ascending=False)
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
            csv = df_mostrar.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Descargar mis gastos (CSV)", csv, "mis_gastos.csv", "text/csv")
        else:
            st.info("👋 Agrega tu primer gasto o carga el ejemplo.")

# ============================================================
# PESTAÑA 2: DASHBOARD
# ============================================================
with tab_dashboard:
    if not st.session_state.gastos:
        st.info("📭 Sin datos todavía. Ve a la pestaña **Registrar** para agregar gastos.")
    else:
        df = pd.DataFrame(st.session_state.gastos)
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df = df.dropna(subset=["fecha"])
        df["mes"] = df["fecha"].dt.strftime("%Y-%m")

        total = df["monto"].sum()
        por_cat = df.groupby("categoria")["monto"].sum().sort_values(ascending=False)
        por_mes = df.groupby("mes")["monto"].sum().sort_index()
        top = por_cat.index[0]

        c1, c2, c3 = st.columns(3)
        c1.metric("💵 Total", f"${total:,.2f}")
        c2.metric("🧾 Gastos", len(df))
        c3.metric("📊 Promedio", f"${df['monto'].mean():,.2f}")

        st.markdown(
            f"🏆 Lo que más gastas: **{EMOJI.get(top, '')} {top}** "
            f"({100 * por_cat.iloc[0] / total:.0f}% del total) · "
            f"📅 Mes más caro: **{por_mes.idxmax()}** (${por_mes.max():,.2f})"
        )

        col1, col2 = st.columns(2)
        with col1:
            fig1, ax1 = plt.subplots(figsize=(6, 4.5))
            por_cat.plot.bar(ax=ax1, color="#4c72b0")
            ax1.set_title("Gasto por categoría")
            ax1.set_ylabel("$")
            ax1.tick_params(axis="x", rotation=30)
            fig1.tight_layout()
            st.pyplot(fig1)
        with col2:
            fig2, ax2 = plt.subplots(figsize=(6, 4.5))
            ax2.pie(por_cat, labels=por_cat.index, autopct="%1.0f%%", startangle=90,
                    colors=plt.cm.Set2.colors[:len(por_cat)])
            ax2.set_title("Distribución del gasto")
            fig2.tight_layout()
            st.pyplot(fig2)

        fig3, ax3 = plt.subplots(figsize=(10, 3.5))
        por_mes.plot(marker="o", ax=ax3, color="#dd8452")
        ax3.set_title("Evolución mes a mes")
        ax3.set_ylabel("$")
        fig3.tight_layout()
        st.pyplot(fig3)

        resumen = por_cat.round(2).reset_index()
        resumen.columns = ["Categoría", "Total ($)"]
        resumen["% del total"] = (100 * resumen["Total ($)"] / total).round(1)
        resumen["Categoría"] = [f"{EMOJI.get(c, '•')} {c}" for c in resumen["Categoría"]]
        st.subheader("Resumen por categoría")
        st.dataframe(resumen, use_container_width=True, hide_index=True)
