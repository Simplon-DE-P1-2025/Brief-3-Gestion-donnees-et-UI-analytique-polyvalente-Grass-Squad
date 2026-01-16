import streamlit as st
import pandas as pd
import altair as alt
import sys
from pathlib import Path

# ----------------------------------
# Setup projet
# ----------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.database.load_database import engine
from src.analysis.flotteurs_analysis import (
    get_operations_coverage,
    get_flotteurs_coverage,
    get_operations_by_category,
    get_charge_humaine_by_category,
    get_criticite_by_category,
    get_top_categories_for_outcomes,
    get_outcomes_by_category,
    get_pavillons_stats
)


def render(engine):
    st.title("🚤 Flotteurs — Quels matériels génèrent le plus d’interventions et de risque ?")
    st.caption("Objectif : relier le matériel (flotteurs) à l’activité opérationnelle, à la charge humaine, à la criticité et à l’issue matérielle.")

    # ----------------------------------
    # Filtres (PostgreSQL safe)
    # ----------------------------------

    where_sql = "1=1"
    params = {}
    topn = 15
    min_ops = 30
    params["topn"] = topn
    params["min_ops"] = min_ops



    
    # ----------------------------------
    # Questions métier
    # ----------------------------------
    st.markdown("### ❓ Questions métier")
    st.markdown(
        "- Quels types de flotteurs **déclenchent le plus d’opérations** ?\n"
        "- Quels flotteurs sont associés aux opérations les plus **lourdes humainement** ?\n"
        "- Quels flotteurs ont la plus forte **criticité** ?\n"
        "- Quels flotteurs “coûtent” le plus **matériellement** ?\n"
        "- Quels **pavillons** apparaissent le plus ?"
    )
    st.divider()

    
    # ======================================================
    # 1) KPI : Couverture flotteur + volume flotteurs
    # ======================================================
    st.subheader("📌 Indicateurs clés")

    cov = get_operations_coverage(engine)
    ops_total = int(cov.ops_total or 0)
    ops_sans_flotteur = int(cov.ops_sans_flotteur or 0)
    pct_sf = (ops_sans_flotteur / ops_total * 100) if ops_total else 0.0

    fl = get_flotteurs_coverage(engine, where_sql, params)
    flotteurs_total = int(fl.flotteurs_total or 0)
    ops_avec_flotteur = int(fl.operations_avec_flotteur or 0)
    avg_flotteurs_par_op = (flotteurs_total / ops_avec_flotteur) if ops_avec_flotteur else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🚢 Total Opérations", f"{ops_total:,}")
    c2.metric("🚢 Opérations sans flotteur", f"{ops_sans_flotteur:,}", f"{pct_sf:.1f}%")
    c2.caption("Environ 1 opération sur 5 n’a aucun flotteur associé")
    c3.metric("⚓ Flotteurs enregistrés", f"{flotteurs_total:,}")
    c4.metric("⚓ Flotteurs / opération (moy.)", f"{avg_flotteurs_par_op:.2f}")

    st.markdown("### 🧠 Lecture simple")
    st.markdown(
        "- Si **Ops sans flotteur** est élevé : la dimension flotteur ne couvre pas toutes les opérations (recherche, fausse alerte, ou données manquantes).\n"
        "- **Flotteurs / opération** donne une idée du niveau de “multi-matériel” dans une intervention."
    )
    st.divider()

    # ======================================================
    # 2) Flotteurs qui déclenchent le plus d'opérations (fréquence réelle)
    # ======================================================
    st.subheader("⚓ Quels flotteurs déclenchent le plus d’opérations ?")
    st.caption("Ici on ne compte pas seulement les flotteurs : on compte les **opérations distinctes** associées à chaque catégorie.")

    df_ops_cat = get_operations_by_category(engine, where_sql, params)

    if df_ops_cat.empty:
        st.info("Aucune donnée catégorie flotteur pour ce filtre.")
    else:
        left, right = st.columns([2, 1])
        with left:
            chart_ops = (
                alt.Chart(df_ops_cat)
                .mark_bar()
                .encode(
                    x=alt.X("categorie_flotteur:N", sort="-y", title="Catégorie flotteur"),
                    y=alt.Y("operations:Q", title="Nombre d’opérations"),
                    tooltip=[
                        alt.Tooltip("categorie_flotteur:N", title="Catégorie"),
                        alt.Tooltip("operations:Q", title="Ops", format=","),
                        alt.Tooltip("flotteurs_impliques:Q", title="Flotteurs", format=","),
                    ],
                )
            )
            st.altair_chart(chart_ops, use_container_width=True)
        with right:
            st.dataframe(df_ops_cat, use_container_width=True)

        top = df_ops_cat.iloc[0]
        st.markdown("### 🧠 Analyse")
        st.markdown(
            f"- Catégorie la plus génératrice d’activité : **{top['categorie_flotteur']}** "
            f"avec **{int(top['operations']):,} opérations**."
        )

    st.divider()

    # ======================================================
    # 3) Charge humaine : personnes/opération par catégorie
    # ======================================================
    st.subheader("👥 Quels flotteurs sont associés aux opérations les plus lourdes ?")
    st.caption("On mesure la **charge humaine moyenne** par opération pour chaque catégorie. (Filtre volume min pour éviter l’effet petits nombres)")

    df_charge = get_charge_humaine_by_category(engine, where_sql, params)

    if df_charge.empty:
        st.info("Pas assez de volume pour calculer une charge humaine stable sur les catégories (augmente la période ou baisse le seuil min).")
    else:
        left, right = st.columns([2, 1])
        with left:
            # ⚠️ une seule unité sur l’axe : personnes / opération
            chart_charge = (
                alt.Chart(df_charge)
                .mark_bar()
                .encode(
                    x=alt.X("categorie_flotteur:N", sort="-y", title="Catégorie flotteur"),
                    y=alt.Y("impliquees_par_operation:Q", title="Personnes impliquées / opération (moyenne)"),
                    tooltip=[
                        alt.Tooltip("categorie_flotteur:N", title="Catégorie"),
                        alt.Tooltip("operations:Q", title="Ops (n)", format=","),
                        alt.Tooltip("personnes_impliquees:Q", title="Impliquées (total)", format=","),
                        alt.Tooltip("impliquees_par_operation:Q", title="Impliquées/op", format=".2f"),
                    ],
                )
            )
            st.altair_chart(chart_charge, use_container_width=True)
        with right:
            st.dataframe(df_charge, use_container_width=True)

        top = df_charge.iloc[0]
        st.markdown("### 🧠 Analyse")
        st.markdown(
            f"- Catégorie la plus “lourde” humainement : **{top['categorie_flotteur']}** "
            f"avec **{float(top['impliquees_par_operation']):.2f}** personnes/op "
            f"(sur **{int(top['operations']):,} opérations**)."
        )

    st.divider()

    # ======================================================
    # 4) Criticité : taux de décès par catégorie
    # ======================================================
    st.subheader("⚫ Quels flotteurs sont les plus critiques ?")
    st.caption("On compare la proportion de décès parmi les personnes impliquées, par catégorie. (Filtre volume min)")

    df_fatal = get_criticite_by_category(engine, where_sql, params)

    if df_fatal.empty:
        st.info("Pas assez de volume pour comparer la criticité de façon stable (augmente la période ou baisse le seuil min).")
    else:
        left, right = st.columns([2, 1])
        with left:
            # ⚠️ une seule unité : taux (%)
            chart_fatal = (
                alt.Chart(df_fatal)
                .mark_bar()
                .encode(
                    x=alt.X("categorie_flotteur:N", sort="-y", title="Catégorie flotteur"),
                    y=alt.Y("taux_deces_pct:Q", title="Taux de décès (%)"),
                    tooltip=[
                        alt.Tooltip("categorie_flotteur:N", title="Catégorie"),
                        alt.Tooltip("operations:Q", title="Ops (n)", format=","),
                        alt.Tooltip("deces:Q", title="Décès", format=","),
                        alt.Tooltip("personnes_impliquees:Q", title="Impliquées", format=","),
                        alt.Tooltip("taux_deces_pct:Q", title="Taux décès (%)", format=".2f"),
                    ],
                )
            )
            st.altair_chart(chart_fatal, use_container_width=True)
        with right:
            st.dataframe(df_fatal, use_container_width=True)

        top = df_fatal.iloc[0]
        st.markdown("### 🧠 Analyse")
        st.markdown(
            f"- Catégorie avec le **taux de décès** le plus élevé : **{top['categorie_flotteur']}** "
            f"(**{float(top['taux_deces_pct']):.2f}%** sur **{int(top['operations']):,}** opérations)."
        )

    st.divider()

    # ======================================================
    # 5) Coût matériel : issue matérielle par catégorie (perdu/détruit/...)
    # ======================================================
    st.subheader("🏁 Issue matérielle : que devient le flotteur ? (par catégorie)")
    st.caption("On visualise le “coût matériel” : catégories le plus souvent **perdues/détruites** ou récupérées. (Top catégories par volume)")

    # D'abord : top catégories par volume de flotteurs (pour limiter le tableau)
    df_top_cat = get_top_categories_for_outcomes(engine, where_sql, params)

    if df_top_cat.empty:
        st.info("Aucune catégorie disponible pour l’analyse des issues matérielles.")
    else:
        top_cats = df_top_cat["categorie_flotteur"].dropna().tolist()
        if not top_cats:
            st.info("Pas de catégories exploitables.")
        else:
            df_out = get_outcomes_by_category(engine, where_sql, params, top_cats)

            if df_out.empty:
                st.info("Aucune donnée d’issue matérielle pour ces catégories.")
            else:
                # Graph empilé en % pour comparer la structure des issues par catégorie
                df_out_tot = df_out.groupby("categorie_flotteur", as_index=False)["nb"].sum().rename(columns={"nb":"total"})
                df_out2 = df_out.merge(df_out_tot, on="categorie_flotteur", how="left")
                df_out2["pct"] = (df_out2["nb"] / df_out2["total"] * 100).round(1)

                left, right = st.columns([2, 1])
                with left:
                    chart_out = (
                        alt.Chart(df_out2)
                        .mark_bar()
                        .encode(
                            x=alt.X("categorie_flotteur:N", title="Catégorie flotteur", sort="-y"),
                            y=alt.Y("pct:Q", title="Répartition des issues (%)", stack="normalize"),
                            color=alt.Color("resultat_flotteur:N", title="Issue matérielle"),
                            tooltip=[
                                alt.Tooltip("categorie_flotteur:N", title="Catégorie"),
                                alt.Tooltip("resultat_flotteur:N", title="Issue"),
                                alt.Tooltip("nb:Q", title="Nombre", format=","),
                                alt.Tooltip("pct:Q", title="Part (%)", format=".1f"),
                            ],
                        )
                    )
                    st.altair_chart(chart_out, use_container_width=True)
                with right:
                    st.dataframe(df_out.sort_values(["categorie_flotteur", "nb"], ascending=[True, False]), use_container_width=True)

                st.markdown("### 🧠 Analyse")
                st.markdown(
                    "- Ce graphique montre la **structure des issues matérielles** par catégorie.\n"
                    "- Les catégories avec une grande part de *perdu/détruit* sont candidates à des actions de prévention/équipement."
                )

    st.divider()

    # ======================================================
    # 6) Pavillons (dimension internationale)
    # ======================================================
    st.subheader("🌍 Pavillons — dimension internationale (Top 15)")
    st.caption("Quels pavillons reviennent le plus souvent parmi les flotteurs impliqués ?")

    df_flag = get_pavillons_stats(engine, where_sql, params)

    if df_flag.empty:
        st.info("Aucune donnée pavillon exploitable pour ce filtre.")
    else:
        chart_flag = (
            alt.Chart(df_flag)
            .mark_bar()
            .encode(
                x=alt.X("pavillon:N", sort="-y", title="Pavillon"),
                y=alt.Y("flotteurs:Q", title="Nombre de flotteurs"),
                tooltip=[
                    alt.Tooltip("pavillon:N", title="Pavillon"),
                    alt.Tooltip("flotteurs:Q", title="Nombre", format=","),
                ],
            )
        )
        st.altair_chart(chart_flag, use_container_width=True)

    st.divider()

    # ------------------------------------------------------
    # 🧠 Synthèse automatique (pro, orientée décision)
    # ------------------------------------------------------
    st.markdown("### 🧠 Analyse")

    bullets = []

    if not df_ops_cat.empty:
        top = df_ops_cat.iloc[0]
        bullets.append(
            f"- **Catégorie la plus génératrice d’opérations** : **{top['categorie_flotteur']}** "
            f"({int(top['operations']):,} opérations)."
        )

    if not df_charge.empty:
        top = df_charge.iloc[0]
        bullets.append(
            f"- **Catégorie la plus lourde humainement** : **{top['categorie_flotteur']}** "
            f"({float(top['impliquees_par_operation']):.2f} personnes/op)."
        )

    if not df_fatal.empty:
        top = df_fatal.iloc[0]
        bullets.append(
            f"- **Catégorie la plus critique (taux de décès)** : **{top['categorie_flotteur']}** "
            f"({float(top['taux_deces_pct']):.2f}%)."
        )

    if not df_flag.empty:
        top = df_flag.iloc[0]
        bullets.append(
            f"- **Pavillon le plus représenté** : **{top['pavillon']}** ({int(top['flotteurs']):,} flotteurs)."
        )

    if bullets:
        st.markdown("\n".join(bullets))
    else:
        st.info("Pas assez de données pour produire une synthèse automatique (essaie sans filtre pavillon).")

    # ------------------------------------------------------
    # ✅ Conclusion
    # ------------------------------------------------------
    st.markdown("### ✅ Conclusion")
    st.markdown(
        "Cette page ne décrit pas seulement les flotteurs : elle montre **leur impact opérationnel**.\n"
        "- D’abord **quels flotteurs génèrent le plus d’interventions**.\n"
        "- Ensuite **quels flotteurs sont associés à des opérations plus lourdes**.\n"
        "- Puis **quels flotteurs sont les plus critiques**.\n"
        "- Enfin, l’**issue matérielle** par catégorie révèle le coût matériel (perdu/détruit/récupéré).\n\n"
        "Suite logique : croiser ces résultats avec **Météo** (conditions), **Zone** (exposition) et **Alerte** (déclencheurs)."
    )

    