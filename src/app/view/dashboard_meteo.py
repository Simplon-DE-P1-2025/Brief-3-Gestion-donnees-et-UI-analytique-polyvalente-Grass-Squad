import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.database.load_database import engine


def render(engine):
        
    st.title("🌦️ Météo — Vent, mer et lien avec la gravité")
    st.caption("Objectif : identifier si la météo augmente l’activité et si elle rend les opérations plus “lourdes” humainement.")

    st.markdown("### ❓ Questions métier")
    st.markdown(
        "- Les opérations augmentent-elles avec la **force du vent** / la **force de la mer** ?\n"
        "- Les conditions dégradées sont-elles associées à plus de **personnes impliquées** ?\n"
        "- Existe-t-il un seuil à partir duquel la **gravité** augmente nettement ?\n"
        "- Les **marées** influencent-elles le volume d’opérations et la charge humaine ?"
    )
    st.divider()

    # Pas de filtres
    where_sql = "1=1"
    params = {}


    if st.button("⬅️ Retour au dashboard"):
        st.session_state.action = 'dashboard'
        st.rerun()
  

    # ======================================================
    # 1 & 2) Vent + Mer : volume d'opérations (CÔTE À CÔTE)
    # ======================================================
    st.subheader("🌬️🌊 Volume d’opérations selon le vent et la mer")
    st.caption("Lecture : comparer rapidement l’évolution du volume selon la force du vent (gauche) et de la mer (droite).")

    col_wind, col_sea = st.columns(2)

    with col_wind:
        st.markdown("#### 🌬️ Vent")
        q_wind = f"""
        SELECT
        FLOOR(o.vent_force)::int AS vent_force,
        COUNT(DISTINCT o.operation_id) AS operations
        FROM operations o
        WHERE {where_sql}
        AND o.vent_force IS NOT NULL
        AND FLOOR(o.vent_force) >= 1
        GROUP BY 1
        ORDER BY 1;
        """
        df_wind = pd.read_sql(q_wind, engine, params=params)

        if df_wind.empty:
            st.info("Pas de données vent_force ≥ 1.")
        else:
            chart_wind = (
                alt.Chart(df_wind)
                .mark_line(point=True)
                .encode(
                    x=alt.X("vent_force:O", title="Force du vent", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("operations:Q", title="Opérations"),
                    tooltip=[
                        alt.Tooltip("vent_force:O", title="Vent"),
                        alt.Tooltip("operations:Q", title="Opérations", format=","),
                    ],
                )
            )
            st.altair_chart(chart_wind, use_container_width=True)

    with col_sea:
        st.markdown("#### 🌊 Mer")
        q_sea = f"""
        SELECT
        FLOOR(o.mer_force)::int AS mer_force,
        COUNT(DISTINCT o.operation_id) AS operations
        FROM operations o
        WHERE {where_sql}
        AND o.mer_force IS NOT NULL
        AND FLOOR(o.mer_force) >= 1
        GROUP BY 1
        ORDER BY 1;
        """
        df_sea = pd.read_sql(q_sea, engine, params=params)

        if df_sea.empty:
            st.info("Pas de données mer_force ≥ 1.")
        else:
            chart_sea = (
                alt.Chart(df_sea)
                .mark_line(point=True)
                .encode(
                    x=alt.X("mer_force:O", title="Force de la mer", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("operations:Q", title="Opérations"),
                    tooltip=[
                        alt.Tooltip("mer_force:O", title="Mer"),
                        alt.Tooltip("operations:Q", title="Opérations", format=","),
                    ],
                )
            )
            st.altair_chart(chart_sea, use_container_width=True)

    st.divider()

    # ======================================================
    # 3) Gravité humaine (ROBUSTE) — total personnes impliquées par force de mer (BAR)
    # ======================================================
    st.subheader("📊 Gravité humaine — Personnes impliquées selon la force de la mer")
    st.caption(
        "Lecture simple : plus la barre est haute, plus ce niveau de mer concentre de charge humaine "
        "(personnes impliquées au total)."
    )

    q_gravite = """
    SELECT
    FLOOR(o.mer_force)::int AS mer_force,
    SUM(COALESCE(os.nombre_personnes_impliquees,0)) AS personnes_impliquees
    FROM operations o
    JOIN operations_stats os USING(operation_id)
    WHERE o.mer_force IS NOT NULL
    AND FLOOR(o.mer_force) >= 1
    AND FLOOR(o.mer_force) <= 12
    GROUP BY 1
    ORDER BY 1;
    """
    df_grav = pd.read_sql(q_gravite, engine)

    grav_top_mer = None
    grav_top_pct = None

    if df_grav.empty:
        st.info("Aucune donnée météo mer_force exploitable.")
    else:
        df_grav["mer_force"] = df_grav["mer_force"].astype(int)
        df_grav["personnes_impliquees"] = df_grav["personnes_impliquees"].fillna(0).astype(int)

        chart_grav = (
            alt.Chart(df_grav)
            .mark_bar()
            .encode(
                x=alt.X("mer_force:O", title="Force de la mer", axis=alt.Axis(labelAngle=0)),
                y=alt.Y("personnes_impliquees:Q", title="Personnes impliquées (total)"),
                tooltip=[
                    alt.Tooltip("mer_force:O", title="Force de la mer"),
                    alt.Tooltip("personnes_impliquees:Q", title="Personnes impliquées", format=","),
                ],
            )
        )
        st.altair_chart(chart_grav, use_container_width=True)

        top = df_grav.sort_values("personnes_impliquees", ascending=False).iloc[0]
        total = df_grav["personnes_impliquees"].sum()
        pct = (top["personnes_impliquees"] / total * 100) if total else 0

        grav_top_mer = int(top["mer_force"])
        grav_top_pct = float(pct)

        st.markdown(
            f"✅ **Lecture simple :** la force de mer qui concentre le plus de charge humaine est **{grav_top_mer}** "
            f"avec **{int(top['personnes_impliquees']):,}** personnes impliquées (**{pct:.1f}%** du total)."
        )

    st.divider()

    # ======================================================
    # 4) Pie chart “manager” : calme / modéré / difficile
    # ======================================================
    st.subheader("Répartition des opérations selon la mer")
    st.caption("On regroupe l’état de la mer en 3 classes pour une lecture instantanée.")

    q_pie3 = f"""
    SELECT
    CASE
        WHEN FLOOR(o.mer_force) BETWEEN 1 AND 2 THEN 'Calme (1-2)'
        WHEN FLOOR(o.mer_force) BETWEEN 3 AND 4 THEN 'Modéré (3-4)'
        WHEN FLOOR(o.mer_force) >= 5 THEN 'Difficile (>=5)'
        ELSE NULL
    END AS categorie_mer,
    COUNT(DISTINCT o.operation_id) AS operations
    FROM operations o
    WHERE {where_sql}
    AND o.mer_force IS NOT NULL
    AND FLOOR(o.mer_force) >= 1
    GROUP BY 1
    HAVING CASE
        WHEN FLOOR(o.mer_force) BETWEEN 1 AND 2 THEN 'Calme (1-2)'
        WHEN FLOOR(o.mer_force) BETWEEN 3 AND 4 THEN 'Modéré (3-4)'
        WHEN FLOOR(o.mer_force) >= 5 THEN 'Difficile (>=5)'
        ELSE NULL
    END IS NOT NULL;
    """
    df_pie3 = pd.read_sql(q_pie3, engine)

    pie_top_cat = None
    pie_top_pct = None

    if df_pie3.empty:
        st.info("Pas assez de données pour la répartition en 3 catégories.")
    else:
        total_ops_pie = df_pie3["operations"].sum() if "operations" in df_pie3.columns else 0
        top_cat = df_pie3.sort_values("operations", ascending=False).iloc[0]
        pie_top_cat = str(top_cat["categorie_mer"])
        pie_top_pct = float((top_cat["operations"] / total_ops_pie * 100) if total_ops_pie else 0)

        pie3 = (
            alt.Chart(df_pie3)
            .mark_arc()
            .encode(
                theta=alt.Theta("operations:Q", title="Opérations"),
                color=alt.Color("categorie_mer:N", title="Catégorie"),
                tooltip=[
                    alt.Tooltip("categorie_mer:N", title="Catégorie"),
                    alt.Tooltip("operations:Q", title="Opérations", format=","),
                ],
            )
        )
        st.altair_chart(pie3, use_container_width=True)

    st.divider()

    # ======================================================
    # 5) Marées : volume d'opérations + charge humaine par catégorie de marée
    # ======================================================
    st.subheader("🌙 Marées — Impact sur l’activité et la charge humaine")
    st.caption("On compare les catégories de marée : volume d’opérations et personnes impliquées.")

    q_maree = """
    SELECT
    maree_categorie,
    COUNT(*) AS operations,
    SUM(COALESCE(nombre_personnes_impliquees, 0)) AS personnes_impliquees
    FROM operations_stats
    WHERE maree_categorie IS NOT NULL
    AND maree_categorie <> 'moyenne'
    GROUP BY 1
    ORDER BY operations DESC;
    """



    # ✅ IMPORTANT : on exécute la requête
    df_maree = pd.read_sql(q_maree, engine)

    # ✅ Pour éviter un crash dans la section "Analyse" plus bas
    maree_top_cat = None
    maree_top_ops = None

    if df_maree.empty:
        st.info("Aucune donnée de marée exploitable (maree_categorie est vide).")
    else:
        # On trace UNIQUEMENT le volume d'opérations (pas de double mesure affichée)
        df_maree_plot = df_maree[["maree_categorie", "operations"]].copy()

        chart_maree = (
            alt.Chart(df_maree_plot)
            .mark_bar()
            .encode(
                x=alt.X("maree_categorie:N", title="Catégorie de marée", sort="-y"),
                y=alt.Y("sum(operations):Q", title="Nombre d’opérations"),
                tooltip=[
                    alt.Tooltip("maree_categorie:N", title="Marée"),
                    alt.Tooltip("operations:Q", title="Opérations", format=","),
                ],
            )
        )
        st.altair_chart(chart_maree, use_container_width=True)

        # Lecture simple automatique
        top_m = df_maree.iloc[0]
        maree_top_cat = str(top_m["maree_categorie"])
        maree_top_ops = int(top_m["operations"])

        st.markdown(
            f"✅ **Lecture simple :** la catégorie de marée la plus associée à l’activité est **{maree_top_cat}** "
            f"avec **{maree_top_ops:,}** opérations et **{int(top_m['personnes_impliquees']):,}** personnes impliquées."
        )


    # ------------------------------------------------------
    # 🧠 Analyse automatique (style Zone)
    # ------------------------------------------------------
    st.markdown("### 🧠 Analyse")

    lines = []

    # Vent : niveau le plus actif
    if not df_wind.empty:
        w_max = df_wind.sort_values("operations", ascending=False).iloc[0]
        lines.append(
            f"- Vent : le niveau le plus actif est **{int(w_max['vent_force'])}** "
            f"({int(w_max['operations']):,} opérations)."
        )

    # Mer : niveau le plus actif
    if not df_sea.empty:
        s_max = df_sea.sort_values("operations", ascending=False).iloc[0]
        lines.append(
            f"- Mer : le niveau le plus actif est **{int(s_max['mer_force'])}** "
            f"({int(s_max['operations']):,} opérations)."
        )

    # Gravité : niveau mer qui concentre le plus de charge
    if grav_top_mer is not None:
        lines.append(
            f"- Charge humaine : la mer **{grav_top_mer}** concentre la plus forte part de personnes impliquées "
            f"(**{grav_top_pct:.1f}%** du total)."
        )

    # Répartition 3 classes mer
    if pie_top_cat is not None:
        lines.append(
            f"- Répartition (3 classes) : la catégorie dominante est **{pie_top_cat}** "
            f"(**{pie_top_pct:.1f}%** des opérations dans ce regroupement)."
        )

    # Marées : catégorie la plus associée à l’activité
    if maree_top_cat is not None:
        lines.append(
            f"- Marées : la catégorie la plus associée à l’activité est **{maree_top_cat}** "
            f"({maree_top_ops:,} opérations)."
        )

    if not lines:
        st.info("Pas assez de données pour produire une analyse automatique.")
    else:
        st.markdown("\n".join(lines))

    # ------------------------------------------------------
    # ✅ Conclusion (style Zone)
    # ------------------------------------------------------
    st.markdown("### ✅ Conclusion")
    st.markdown(
        "Cette page explique **comment la météo pèse sur l’activité et la charge humaine** :\n"
        "- Les courbes Vent/Mer montrent **si le volume d’opérations augmente** avec des conditions plus fortes.\n"
        "- La gravité met en évidence **les niveaux de mer qui concentrent le plus de personnes impliquées**.\n"
        "- Les regroupements (3 classes) et les **marées** donnent une lecture rapide des situations les plus fréquentes.\n\n"
        "Suite logique : croiser ces résultats avec **Zone** (où) et **Alerte** (déclencheurs) pour comprendre les pics."
    )

   