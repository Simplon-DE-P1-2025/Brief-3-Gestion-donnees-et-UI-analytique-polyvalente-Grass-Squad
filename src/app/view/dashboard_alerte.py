import streamlit as st
import pandas as pd


def render(engine):
    st.title("🚨 Alerte — Déclencheurs, canaux et “fausses alertes”")
    st.caption("Objectif : comprendre d’où viennent les alertes, qui alerte, et l’impact humain associé.")

    # Pas de filtres
    where_sql = "1=1"
    params = {}


    if st.button("⬅️ Retour au dashboard"):
        st.session_state.action = 'dashboard'
        st.rerun()
    # ------------------------------------------------------
    # Questions métier (claires)
    # ------------------------------------------------------
    st.markdown("### ❓ Questions métier")
    st.markdown(
        "- Quels **canaux d’alerte** génèrent le plus d’opérations ?\n"
        "- Quelles sont les **raisons d’alerte** les plus fréquentes ?\n"
        "- Qui alerte le plus ?\n"
        "- Où observe-t-on le plus de **fausses alertes** (au sens “personnes impliquées dans fausse alerte”) ?"
    )

    st.divider()

    # ------------------------------------------------------
    # 1) KPIs globaux (volume + impact + fausse alerte)
    # ------------------------------------------------------
    st.subheader("📌 Vue globale — volume & impact")

    q_kpi = f"""
    WITH base AS (
      SELECT
        o.operation_id,
        COALESCE(os.nombre_personnes_impliquees,0) AS impliquees,
        COALESCE(os.nombre_personnes_secourues,0) AS secourues,
        COALESCE(os.nombre_personnes_decedees,0) AS deces,
        COALESCE(os.nombre_personnes_impliquees_dans_fausse_alerte,0) AS fausse_alerte_personnes
      FROM operations o
      LEFT JOIN operations_stats os USING(operation_id)
      WHERE {where_sql}
    )
    SELECT
      COUNT(DISTINCT operation_id) AS operations,
      SUM(impliquees) AS impliquees,
      SUM(secourues) AS secourues,
      SUM(deces) AS deces,
      SUM(fausse_alerte_personnes) AS fausse_alerte_personnes,
      ROUND(100.0 * SUM(fausse_alerte_personnes)::numeric / NULLIF(SUM(impliquees),0), 2) AS taux_fausse_alerte_sur_personnes_pct
    FROM base;
    """
    k = pd.read_sql(q_kpi, engine, params=params).iloc[0]

    ops_total = int(k.operations or 0)
    impl_total = int(k.impliquees or 0)
    sec_total = int(k.secourues or 0)
    dec_total = int(k.deces or 0)
    fa_total = int(k.fausse_alerte_personnes or 0)
    fa_pct = float(k.taux_fausse_alerte_sur_personnes_pct or 0)

    taux_sauvetage = (sec_total / impl_total * 100) if impl_total else 0.0
    taux_deces = (dec_total / impl_total * 100) if impl_total else 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🚢 Opérations", f"{ops_total:,}")
    c2.metric("👥 Personnes impliquées", f"{impl_total:,}")
    c3.metric("✅ Secourues", f"{sec_total:,}", f"{taux_sauvetage:.2f}%")
    c3.caption(f"Environ une personne impliquée sur trois nécessite une action de sauvetage **{taux_sauvetage:.2f}%** ")

    c4.metric("⚫ Décès", f"{dec_total:,}", f"{taux_deces:.2f}%")
    c4.caption(f"Moins d’une personne impliquée sur 200 décède **{taux_deces:.2f}%**")

    c5.metric("🟠 Personnes (fausse alerte)", f"{fa_total:,}", f"{fa_pct:.2f}%")
    c5.caption(f"Environ 1 personne impliquée sur 15 relève d’une fausse alerte **{fa_pct:.2f}** ")

    st.markdown("### 🧠 Lecture simple")
    st.markdown(
        "- **moyen_alerte** / **pourquoi_alerte** : d’où vient l’activité.\n"
        "- **fausse_alerte_personnes** : charge “inutilisée” (process + moyens), à optimiser.\n"
    )

    st.divider()

    # ======================================================
    # 2) Canaux d’alerte (moyen_alerte)
    # ======================================================
    st.subheader("📟 Canaux d’alerte — Top 15")

    q_moyen = f"""
    SELECT
      NULLIF(TRIM(o.moyen_alerte),'') AS moyen_alerte,
      COUNT(DISTINCT o.operation_id) AS operations,
      COALESCE(SUM(os.nombre_personnes_impliquees),0) AS personnes_impliquees
    FROM operations o
    LEFT JOIN operations_stats os USING(operation_id)
    WHERE {where_sql}
      AND NULLIF(TRIM(o.moyen_alerte),'') IS NOT NULL
    GROUP BY 1
    ORDER BY operations DESC
    LIMIT 15;
    """
    df_moyen = pd.read_sql(q_moyen, engine, params=params)

    colA, colB = st.columns([2, 1])
    with colA:
        if not df_moyen.empty:
            st.bar_chart(df_moyen.set_index("moyen_alerte")[["operations", "personnes_impliquees"]])
        else:
            st.info("Aucune donnée moyen_alerte sur la période.")
    with colB:
        if not df_moyen.empty:
            st.dataframe(df_moyen, use_container_width=True)

    if not df_moyen.empty:
        top = df_moyen.iloc[0]
        st.markdown("### 🧠 Analyse")
        st.markdown(
            f"- Canal dominant : **{top['moyen_alerte']}** "
            f"avec **{int(top['operations']):,} opérations**.\n"
            f"- Ce canal représente un point d’entrée critique : qualité des infos / tri / standardisation."
        )

    st.divider()

    # ======================================================
    # 3) Raisons d’alerte (pourquoi_alerte)
    # ======================================================
    st.subheader("🧩 Raisons d’alerte — Top 15")

    q_pourquoi = f"""
    SELECT
      NULLIF(TRIM(o.pourquoi_alerte),'') AS pourquoi_alerte,
      COUNT(DISTINCT o.operation_id) AS operations,
      COALESCE(SUM(os.nombre_personnes_impliquees),0) AS personnes_impliquees,
      ROUND(
        COALESCE(SUM(os.nombre_personnes_impliquees),0)::numeric
        / NULLIF(COUNT(DISTINCT o.operation_id),0),
        2
      ) AS impliquees_par_operation
    FROM operations o
    LEFT JOIN operations_stats os USING(operation_id)
    WHERE {where_sql}
      AND NULLIF(TRIM(o.pourquoi_alerte),'') IS NOT NULL
    GROUP BY 1
    ORDER BY operations DESC
    LIMIT 15;
    """
    df_pq = pd.read_sql(q_pourquoi, engine, params=params)

    colA, colB = st.columns([2, 1])
    with colA:
        if not df_pq.empty:
            st.bar_chart(df_pq.set_index("pourquoi_alerte")[["operations", "personnes_impliquees"]])
        else:
            st.info("Aucune donnée pourquoi_alerte sur la période.")
    with colB:
        if not df_pq.empty:
            st.dataframe(df_pq, use_container_width=True)

    if not df_pq.empty:
        top_ops = df_pq.sort_values("operations", ascending=False).iloc[0]
        top_grav = df_pq.sort_values("impliquees_par_operation", ascending=False).iloc[0]

        st.markdown("### 🧠 Analyse (automatique)")
        st.markdown(
            f"- Raison la plus fréquente : **{top_ops['pourquoi_alerte']}** "
            f"({int(top_ops['operations']):,} opérations).\n"
            f"- Raison la plus “lourde” en moyenne (personnes/opération) : **{top_grav['pourquoi_alerte']}** "
            f"({float(top_grav['impliquees_par_operation']):.2f} personnes/opération).\n"
            "👉 On distingue bien : **ce qui arrive le plus** vs **ce qui coûte le plus humainement**."
        )

    st.divider()

    # ======================================================
    # 4) Fausse alerte par canal
    # ======================================================
    st.subheader("🟠 Où se concentrent les fausses alertes ?")

    q_fa = f"""
    SELECT
      NULLIF(TRIM(o.moyen_alerte),'') AS moyen_alerte,
      COUNT(DISTINCT o.operation_id) AS operations,
      COALESCE(SUM(os.nombre_personnes_impliquees),0) AS personnes_impliquees,
      COALESCE(SUM(os.nombre_personnes_impliquees_dans_fausse_alerte),0) AS personnes_fausse_alerte,
      ROUND(
        100.0 * COALESCE(SUM(os.nombre_personnes_impliquees_dans_fausse_alerte),0)::numeric
        / NULLIF(COALESCE(SUM(os.nombre_personnes_impliquees),0),0),
        2
      ) AS taux_fausse_alerte_sur_personnes_pct
    FROM operations o
    LEFT JOIN operations_stats os USING(operation_id)
    WHERE {where_sql}
      AND NULLIF(TRIM(o.moyen_alerte),'') IS NOT NULL
    GROUP BY 1
    HAVING COUNT(DISTINCT o.operation_id) >= 500
    ORDER BY taux_fausse_alerte_sur_personnes_pct DESC, operations DESC
    LIMIT 15;
    """
    df_fa = pd.read_sql(q_fa, engine, params=params)

    if df_fa.empty:
        st.info("Pas assez de volume (>=500 opérations par canal) pour une comparaison fiable.")
    else:
        st.dataframe(df_fa, use_container_width=True)

        worst = df_fa.iloc[0]
        st.markdown("### 🧠 Analyse")
        st.markdown(
            f"- Canal avec le plus fort taux de fausse alerte (sur personnes) : "
            f"**{worst['moyen_alerte']}** avec **{float(worst['taux_fausse_alerte_sur_personnes_pct']):.2f}%**.\n"
            "👉 C’est un bon candidat pour améliorer le tri (checklist, informations minimales, procédure)."
        )

    st.markdown("### ✅ Conclusion")
    st.markdown(
        "Cette page explique **d’où vient l’activité** (canal + raison) et met en évidence un sujet process : "
        "**les fausses alertes**.\n"
        "La suite logique : comprendre les **facteurs de risque** → pages **Météo** et **Zone géographique**, "
        "puis le matériel → page **Flotteurs**."
    )
    st.divider()

    