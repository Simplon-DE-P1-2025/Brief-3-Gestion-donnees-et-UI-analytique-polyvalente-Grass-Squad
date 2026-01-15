import streamlit as st
import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.database.load_database import engine



def render(engine):
    st.title("🗓️ Date — Saison, vacances et jours à risque")
    st.caption("Objectif : comprendre d’où viennent les alertes, qui alerte, et l’impact humain associé.")

    # Pas de filtres
    where_sql = "1=1"
    params = {}


    if st.button("⬅️ Retour au dashboard"):
        st.session_state.action = 'dashboard'
        st.rerun()
    # --------------
    # ------------------------------------------------------
    # 0) Questions métier (novice-friendly)
    # ------------------------------------------------------
    st.markdown("### ❓ Questions métier")
    st.markdown(
        "- Y a-t-il plus d’opérations pendant les **vacances scolaires** ?\n"
        "- Y a-t-il plus d’opérations en **été (juillet–août)** ?\n"
        "- Quels **jours de la semaine** concentrent le plus d’activité et de charge humaine ?\n"
        "- Les périodes “à risque” sont-elles plus graves (plus de personnes impliquées par opération) ?"
    )

    st.divider()


    # ------------------------------------------------------
    # 2) KPI globaux simples
    # ------------------------------------------------------
    st.subheader("📌 Vue globale ")

    q_kpi = f"""
    SELECT
    COUNT(DISTINCT os.operation_id) AS operations,
    COALESCE(SUM(os.nombre_personnes_impliquees),0) AS personnes_impliquees,
    COALESCE(SUM(os.nombre_personnes_secourues),0) AS personnes_secourues,
    COALESCE(SUM(os.nombre_personnes_decedees),0) AS personnes_decedees,
    ROUND(
        COALESCE(SUM(os.nombre_personnes_impliquees),0)::numeric
        / NULLIF(COUNT(DISTINCT os.operation_id),0),
        2
    ) AS impliquees_par_operation
    FROM operations_stats os
    WHERE {where_sql};
    """
    k = pd.read_sql(q_kpi, engine, params=params).iloc[0]

    ops_total = int(k.operations or 0)
    impl_total = int(k.personnes_impliquees or 0)
    sec_total = int(k.personnes_secourues or 0)
    dec_total = int(k.personnes_decedees or 0)
    impl_par_op = float(k.impliquees_par_operation or 0)

    taux_sauvetage = (sec_total / impl_total * 100) if impl_total else 0.0
    taux_deces = (dec_total / impl_total * 100) if impl_total else 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🚢 Opérations", f"{ops_total:,}")
    c2.metric("👥 Personnes impliquées", f"{impl_total:,}")
    c3.metric("✅ Secourues", f"{sec_total:,}", f"{taux_sauvetage:.2f}%")
    c3.caption(f"Part des personnes secourues parmi toutes les personnes impliquées **{taux_sauvetage:.2f}%** ")
    c4.metric("⚫ Décès", f"{dec_total:,}", f"{taux_deces:.2f}%")
    c4.caption(f"Part des personnes décédées parmi toutes les personnes impliquées **{taux_deces:.2f}%** ")
    c5.metric("📦 Impliquées / opération", f"{impl_par_op:.2f}")

    st.markdown("### 🧠 Lecture simple")
    st.markdown(
        "- **Opérations** = le volume d’activité.\n"
        "- **Personnes impliquées** = la charge humaine totale.\n"
        "- **Impliquées / opération** = une mesure simple de “gravité moyenne”."
    )

    st.divider()

    # ======================================================
    # SECTION A — REQUÊTE + GRAPHIQUE #1 : Jour de semaine
    # ======================================================
    st.subheader("📅 Jour de la semaine — activité & charge")

    # ⚠️ On recalcule le jour depuis la date (pour éviter Wednesday / mélange FR-EN)
    q_day = f"""
    SELECT
    CASE EXTRACT(DOW FROM os.date::date)
        WHEN 0 THEN 'Dimanche'
        WHEN 1 THEN 'Lundi'
        WHEN 2 THEN 'Mardi'
        WHEN 3 THEN 'Mercredi'
        WHEN 4 THEN 'Jeudi'
        WHEN 5 THEN 'Vendredi'
        WHEN 6 THEN 'Samedi'
    END AS jour_semaine,
    EXTRACT(DOW FROM os.date::date)::int AS ordre,
    COUNT(DISTINCT os.operation_id) AS operations,
    COALESCE(SUM(os.nombre_personnes_impliquees),0) AS personnes_impliquees,
    ROUND(
        COALESCE(SUM(os.nombre_personnes_impliquees),0)::numeric
        / NULLIF(COUNT(DISTINCT os.operation_id),0),
        2
    ) AS impliquees_par_operation
    FROM operations_stats os
    WHERE {where_sql}
    AND os.date IS NOT NULL
    GROUP BY 1,2
    ORDER BY ordre;
    """
    df_day = pd.read_sql(q_day, engine, params=params)

    colA, colB = st.columns([2, 1])
    with colA:
        if not df_day.empty:
            st.bar_chart(df_day.set_index("jour_semaine")[["operations", "personnes_impliquees"]])
        else:
            st.info("Pas de données disponibles sur la période.")
    with colB:
        if not df_day.empty:
            st.dataframe(df_day.drop(columns=["ordre"]), use_container_width=True)

    # Analyse automatique (basée sur les chiffres affichés)
    if not df_day.empty:
        top_ops = df_day.sort_values("operations", ascending=False).iloc[0]
        top_impl = df_day.sort_values("personnes_impliquees", ascending=False).iloc[0]

        st.markdown("### 🧠 Analyse automatique")
        st.markdown(
            f"- Jour avec **le plus d’opérations** : **{top_ops['jour_semaine']}** "
            f"({int(top_ops['operations']):,} opérations).\n"
            f"- Jour avec **la plus forte charge humaine** : **{top_impl['jour_semaine']}** "
            f"({int(top_impl['personnes_impliquees']):,} personnes impliquées).\n"
            "👉 Cela aide à planifier des moyens renforcés sur les jours les plus chargés."
        )

    st.divider()

    q_vac_ete = f"""
    WITH base AS (
    SELECT
        os.operation_id,
        COALESCE(os.nombre_personnes_impliquees,0) AS impliquees,
        (os.est_vacances_scolaires = TRUE) AS est_vacances,
        (os.mois IN (7,8)) AS est_ete
    FROM operations_stats os
    WHERE {where_sql}
    )
    SELECT
    est_vacances,
    est_ete,
    COUNT(DISTINCT operation_id) AS operations,
    SUM(impliquees) AS personnes_impliquees,
    ROUND(SUM(impliquees)::numeric / NULLIF(COUNT(DISTINCT operation_id),0), 2) AS impliquees_par_operation
    FROM base
    GROUP BY est_vacances, est_ete
    ORDER BY est_vacances, est_ete;
    """
    df = pd.read_sql(q_vac_ete, engine, params=params)

    if df.empty:
        st.info("Pas de données pour la période.")
    else:
        # -----------------------------
        # Vue 1 : Vacances vs Hors vacances
        # -----------------------------
        df_vac = (
            df.groupby("est_vacances", as_index=False)
            .agg(operations=("operations","sum"),
                personnes_impliquees=("personnes_impliquees","sum"))
        )
        df_vac["impliquees_par_operation"] = (
            df_vac["personnes_impliquees"] / df_vac["operations"]
        ).round(2)
        df_vac["periode"] = df_vac["est_vacances"].map({True:"Vacances scolaires", False:"Hors vacances"})
        df_vac = df_vac[["periode","operations","personnes_impliquees","impliquees_par_operation"]].sort_values("periode")

        st.markdown("### 🏖️ Vacances scolaires vs Hors vacances")
        colA, colB = st.columns([2,1])
        with colA:
            st.bar_chart(df_vac.set_index("periode")[["operations","personnes_impliquees"]])
        with colB:
            st.dataframe(df_vac, use_container_width=True)

        # Analyse auto vacances
        vac = df_vac.set_index("periode")
        ops_vac = int(vac.loc["Vacances scolaires","operations"])
        ops_hv  = int(vac.loc["Hors vacances","operations"])
        implop_vac = float(vac.loc["Vacances scolaires","impliquees_par_operation"])
        implop_hv  = float(vac.loc["Hors vacances","impliquees_par_operation"])
        total = ops_vac + ops_hv
        part_vac = (ops_vac/total*100) if total else 0.0
        diff = implop_vac - implop_hv

        st.markdown("#### 🧠 Analyse automatique (Vacances)")
        st.markdown(
            f"- Vacances : **{ops_vac:,} ops** (**{part_vac:.1f}%**), **{implop_vac:.2f}** pers/op\n"
            f"- Hors vacances : **{ops_hv:,} ops**, **{implop_hv:.2f}** pers/op"
        )
        seuil = 0.05
        if abs(diff) < seuil:
            st.markdown(f"✅ Conclusion : gravité moyenne **quasi identique** (écart {diff:+.2f}).")
        elif diff > 0:
            st.markdown(f"✅ Conclusion : vacances **un peu plus lourdes** (écart {diff:+.2f}).")
        else:
            st.markdown(f"✅ Conclusion : vacances **un peu moins lourdes** (écart {diff:+.2f}).")

        st.divider()

        # -----------------------------
        # Vue 2 : Été (Juil-Août) vs reste
        # -----------------------------
        df_ete = (
            df.groupby("est_ete", as_index=False)
            .agg(operations=("operations","sum"),
                personnes_impliquees=("personnes_impliquees","sum"))
        )
        df_ete["impliquees_par_operation"] = (
            df_ete["personnes_impliquees"] / df_ete["operations"]
        ).round(2)
        df_ete["periode"] = df_ete["est_ete"].map({True:"Été (Juillet–Août)", False:"Reste de l’année"})
        df_ete = df_ete[["periode","operations","personnes_impliquees","impliquees_par_operation"]].sort_values("periode")

        st.markdown("### ☀️ Été (Juillet–Août) vs reste de l’année")
        colA, colB = st.columns([2,1])
        with colA:
            st.bar_chart(df_ete.set_index("periode")[["operations","personnes_impliquees"]])
        with colB:
            st.dataframe(df_ete, use_container_width=True)

        # Analyse auto été
        ete = df_ete.set_index("periode")
        ops_ete = int(ete.loc["Été (Juillet–Août)","operations"])
        ops_rest = int(ete.loc["Reste de l’année","operations"])
        implop_ete = float(ete.loc["Été (Juillet–Août)","impliquees_par_operation"])
        implop_rest = float(ete.loc["Reste de l’année","impliquees_par_operation"])
        total2 = ops_ete + ops_rest
        part_ete = (ops_ete/total2*100) if total2 else 0.0
        diff2 = implop_ete - implop_rest

        st.markdown("#### 🧠 Analyse automatique (Été)")
        st.markdown(
            f"- Été : **{ops_ete:,} ops** (**{part_ete:.1f}%**), **{implop_ete:.2f}** pers/op\n"
            f"- Reste : **{ops_rest:,} ops**, **{implop_rest:.2f}** pers/op"
        )
        if abs(diff2) < seuil:
            st.markdown(f"✅ Conclusion : gravité moyenne **quasi identique** (écart {diff2:+.2f}).")
        elif diff2 > 0:
            st.markdown(f"✅ Conclusion : été **un peu plus lourd** (écart {diff2:+.2f}).")
        else:
            st.markdown(f"✅ Conclusion : été **un peu moins lourd** (écart {diff2:+.2f}).")

        st.divider()

        # -----------------------------
        # Bonus pro : Croisement Vacances × Été (story)
        # -----------------------------
        st.markdown("### 🔎 Croisement Vacances × Été (pour raconter l’histoire)")
        df_cross = df.copy()
        df_cross["vacances"] = df_cross["est_vacances"].map({True:"Vacances", False:"Hors vacances"})
        df_cross["ete"] = df_cross["est_ete"].map({True:"Été", False:"Hors été"})
        df_cross = df_cross[["vacances","ete","operations","personnes_impliquees","impliquees_par_operation"]]
        st.dataframe(df_cross, use_container_width=True)

        # Petite lecture auto (ligne la plus chargée en ops)
        worst = df_cross.sort_values("operations", ascending=False).iloc[0]
        st.markdown(
            f"✅ Point clé : le plus fréquent est **{worst['vacances']} + {worst['ete']}** "
            f"avec **{int(worst['operations']):,} opérations**."
        )

        st.set_page_config(
        layout="wide",
        initial_sidebar_state="collapsed"
    )
        
    