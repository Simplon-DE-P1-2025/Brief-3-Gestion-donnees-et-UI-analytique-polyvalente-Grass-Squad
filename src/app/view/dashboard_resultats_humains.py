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


def render(engine):
        
    st.title("👤 Résultats humains — Profils, blessures et issues")
    st.caption("Objectif : raconter le parcours humain d’une opération, identifier les profils les plus exposés, et comprendre les issues.")

    try:
        # ----------------------------------
        # Questions métier
        # ----------------------------------
        st.markdown("### ❓ Questions métier")
        st.markdown(
            "- Quel est le **pipeline humain** (impliquées → secourues → blessées → décédées) ?\n"
            "- Quels **profils** sont les plus touchés (volume) ?\n"
            "- Quels profils ont une **gravité plus forte** (taux de blessure) ?\n"
            "- Quelles **issues humaines** dominent, et pour quels profils ?"
        )
        st.divider()

        # ----------------------------------
        # Filtres (PostgreSQL safe) — SANS SIDEBAR
        # ----------------------------------
        where_os = "1=1"
        params = {}

        if st.button("⬅️ Retour au dashboard"):
            st.session_state.action = 'dashboard'
            st.rerun()

        # Constantes d’affichage (pas de slider)
        TOPN = 15
        MIN_PERSONNES = 300

        # ======================================================
        # 1) Pipeline humain (KPIs + Funnel)
        # ======================================================
        st.subheader("📌 Pipeline humain")

        q_kpi = f"""
        SELECT
        COALESCE(SUM(os.nombre_personnes_impliquees),0) AS impliquees,
        COALESCE(SUM(os.nombre_personnes_secourues),0) AS secourues,
        COALESCE(SUM(os.nombre_personnes_blessees),0) AS blessees,
        COALESCE(SUM(os.nombre_personnes_decedees),0) AS deces,
        COALESCE(SUM(os.nombre_personnes_impliquees_dans_fausse_alerte),0) AS fausse_alerte
        FROM operations_stats os
        WHERE {where_os};
        """
        k = pd.read_sql(q_kpi, engine, params=params).iloc[0]

        impl = int(k.impliquees or 0)
        sec = int(k.secourues or 0)
        ble = int(k.blessees or 0)
        dec = int(k.deces or 0)
        fa = int(k.fausse_alerte or 0)

        taux_sauvetage = (sec / impl * 100) if impl else 0.0
        taux_blessure = (ble / impl * 100) if impl else 0.0
        taux_deces = (dec / impl * 100) if impl else 0.0
        taux_fausse = (fa / impl * 100) if impl else 0.0

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("👥 Impliquées", f"{impl:,}")
        c2.metric("✅ Secourues", f"{sec:,}", f"{taux_sauvetage:.2f}%")
        c2.caption(f"Sur l’ensemble des personnes impliquées, environ **{taux_sauvetage:.2f}%** ont pu être secourues.")
        c3.metric("🩹 Blessées", f"{ble:,}", f"{taux_blessure:.2f}%")
        c3.caption(f"Environ **{taux_blessure:.2f}%** des personnes impliquées ressortent blessées (mesure simple de gravité).")
        c4.metric("⚫ Décédées", f"{dec:,}", f"{taux_deces:.2f}%")
        c4.caption(f"La proportion de décès est de **{taux_deces:.2f}%** des personnes impliquées (criticité).")
        c5.metric("🟠 Fausse alerte (personnes)", f"{fa:,}", f"{taux_fausse:.2f}%")
        c5.caption(f"Environ **{taux_fausse:.2f}%** des personnes sont liées à des fausses alertes (charge opérationnelle sans impact réel).")

        st.markdown("### 🧠 Analyse — Pipeline")
        if impl == 0:
            st.info("Aucune personne impliquée sur la période.")
        else:
            st.markdown(
                f"- **{taux_sauvetage:.2f}%** secourues : la majorité des situations aboutissent à une issue positive.\n"
                f"- **{taux_blessure:.2f}%** blessées : indicateur de gravité moyenne.\n"
                f"- **{taux_deces:.2f}%** décès : niveau de criticité.\n"
                f"- **{taux_fausse:.2f}%** fausse alerte : charge opérationnelle potentiellement optimisable."
            )

        st.markdown("### 📊 Funnel visuel")
        funnel = pd.DataFrame({
            "Étape": ["Impliquées", "Secourues", "Blessées", "Décédées"],
            "Personnes": [impl, sec, ble, dec]
        })
        funnel["Part_vs_impliquées_%"] = (funnel["Personnes"] / (impl if impl else 1) * 100).round(2)

        chart_funnel = (
            alt.Chart(funnel)
            .mark_bar()
            .encode(
                y=alt.Y("Étape:N", sort=["Impliquées", "Secourues", "Blessées", "Décédées"], title=""),
                x=alt.X("Personnes:Q", title="Nombre de personnes"),
                tooltip=[
                    alt.Tooltip("Étape:N"),
                    alt.Tooltip("Personnes:Q", format=","),
                    alt.Tooltip("Part_vs_impliquées_%:Q", title="Part vs impliquées (%)", format=".2f"),
                ],
            )
        )
        st.altair_chart(chart_funnel, use_container_width=True)

        st.divider()

        # ======================================================
        # 2) Profils : volume + taux de blessure
        # ======================================================
        st.subheader("🧑‍🤝‍🧑 Profils (categorie_personne) — volume & gravité")
        st.caption("On identifie les profils dominants (volume) et ceux qui ont une gravité plus forte (taux de blessure).")

        q_prof = f"""
        SELECT
        NULLIF(TRIM(rh.categorie_personne),'') AS categorie_personne,
        COALESCE(SUM(rh.nombre),0) AS personnes,
        COALESCE(SUM(rh.dont_nombre_blesse),0) AS blesses,
        ROUND(
            100.0 * COALESCE(SUM(rh.dont_nombre_blesse),0)::numeric
            / NULLIF(COALESCE(SUM(rh.nombre),0),0),
            2
        ) AS taux_blessure_pct
        FROM resultats_humain rh
        JOIN operations_stats os
        ON os.operation_id = rh.operation_id
        WHERE {where_os}
        AND NULLIF(TRIM(rh.categorie_personne),'') IS NOT NULL
        GROUP BY 1
        ORDER BY personnes DESC;
        """
        df_prof = pd.read_sql(q_prof, engine, params=params)

        if df_prof.empty:
            st.info("Aucune donnée profil disponible.")
        else:
            df_top = df_prof.head(TOPN).copy()

            left, right = st.columns([2, 1])
            with left:
                st.markdown("**Top profils par volume (personnes)**")
                chart_vol = (
                    alt.Chart(df_top)
                    .mark_bar()
                    .encode(
                        y=alt.Y("categorie_personne:N", sort="-x", title="Profil"),
                        x=alt.X("personnes:Q", title="Personnes (total)"),
                        tooltip=[
                            alt.Tooltip("categorie_personne:N", title="Profil"),
                            alt.Tooltip("personnes:Q", title="Personnes", format=","),
                            alt.Tooltip("blesses:Q", title="Blessés", format=","),
                            alt.Tooltip("taux_blessure_pct:Q", title="Taux blessure (%)", format=".2f"),
                        ],
                    )
                )
                st.altair_chart(chart_vol, use_container_width=True)
            with right:
                st.dataframe(df_top, use_container_width=True)

            top = df_prof.iloc[0]
            st.markdown("### 🧠 Analyse — Profils les plus touchés (volume)")
            st.markdown(
                f"- Profil dominant : **{top['categorie_personne']}** avec **{int(top['personnes']):,} personnes**.\n"
                "- Ce profil concentre l’essentiel du volume humain pris en charge."
            )

            st.divider()

            st.markdown("**Gravité : taux de blessure (%) — profils avec volume suffisant**")
            df_grav = df_prof[df_prof["personnes"] >= MIN_PERSONNES].copy()
            df_grav = df_grav.sort_values("taux_blessure_pct", ascending=False).head(TOPN)

            if df_grav.empty:
                st.info(f"Aucun profil n’atteint {MIN_PERSONNES:,} personnes : gravité difficile à comparer.")
            else:
                chart_grav = (
                    alt.Chart(df_grav)
                    .mark_bar()
                    .encode(
                        y=alt.Y("categorie_personne:N", sort="-x", title="Profil"),
                        x=alt.X("taux_blessure_pct:Q", title="Taux de blessure (%)"),
                        tooltip=[
                            alt.Tooltip("categorie_personne:N", title="Profil"),
                            alt.Tooltip("personnes:Q", title="Personnes", format=","),
                            alt.Tooltip("blesses:Q", title="Blessés", format=","),
                            alt.Tooltip("taux_blessure_pct:Q", title="Taux blessure (%)", format=".2f"),
                        ],
                    )
                )
                st.altair_chart(chart_grav, use_container_width=True)

                top_g = df_grav.iloc[0]
                st.markdown("### 🧠 Analyse — Profils les plus à risque")
                st.markdown(
                    f"- Profil le plus exposé (volume ≥ {MIN_PERSONNES:,}) : **{top_g['categorie_personne']}** "
                    f"avec **{float(top_g['taux_blessure_pct']):.2f}%**.\n"
                    "- C’est un candidat prioritaire pour prévention / formation ciblée."
                )

            st.divider()

            st.markdown("**Carte “volume vs gravité”**")
            df_sc = df_prof[df_prof["personnes"] > 0].copy()
            scatter = (
                alt.Chart(df_sc)
                .mark_circle()
                .encode(
                    x=alt.X("personnes:Q", title="Volume (personnes)"),
                    y=alt.Y("taux_blessure_pct:Q", title="Gravité (taux blessure %)"),
                    size=alt.Size("personnes:Q", legend=None),
                    tooltip=[
                        alt.Tooltip("categorie_personne:N", title="Profil"),
                        alt.Tooltip("personnes:Q", title="Personnes", format=","),
                        alt.Tooltip("blesses:Q", title="Blessés", format=","),
                        alt.Tooltip("taux_blessure_pct:Q", title="Taux blessure (%)", format=".2f"),
                    ],
                )
                .properties(height=350)
            )
            st.altair_chart(scatter, use_container_width=True)

            st.markdown("### 🧠 Analyse — Volume vs gravité")
            st.markdown(
                "- Les profils très volumineux dimensionnent la charge opérationnelle.\n"
                "- Les profils à forte gravité doivent être ciblés en prévention, même s’ils sont moins fréquents."
            )

        st.divider()

        # ======================================================
        # 3) Issues humaines : résultat global + par profil
        # ======================================================
        st.subheader("🏁 Issues humaines — que devient la personne ?")
        st.caption("On voit les issues dominantes, puis comment elles se répartissent selon les profils principaux.")

        q_out = f"""
        SELECT
        NULLIF(TRIM(rh.resultat_humain),'') AS resultat_humain,
        COALESCE(SUM(rh.nombre),0) AS personnes
        FROM resultats_humain rh
        JOIN operations_stats os
        ON os.operation_id = rh.operation_id
        WHERE {where_os}
        AND NULLIF(TRIM(rh.resultat_humain),'') IS NOT NULL
        GROUP BY 1
        ORDER BY personnes DESC;
        """
        df_out = pd.read_sql(q_out, engine, params=params)

        if df_out.empty:
            st.info("Aucune donnée d’issue humaine disponible.")
        else:
            left, right = st.columns([2, 1])
            with left:
                chart_out = (
                    alt.Chart(df_out.head(20))
                    .mark_bar()
                    .encode(
                        y=alt.Y("resultat_humain:N", sort="-x", title="Issue"),
                        x=alt.X("personnes:Q", title="Personnes"),
                        tooltip=[
                            alt.Tooltip("resultat_humain:N", title="Issue"),
                            alt.Tooltip("personnes:Q", title="Personnes", format=","),
                        ],
                    )
                )
                st.altair_chart(chart_out, use_container_width=True)
            with right:
                st.dataframe(df_out.head(25), use_container_width=True)

            top_issue = df_out.iloc[0]
            st.markdown("### 🧠 Analyse — Issue dominante")
            st.markdown(
                f"- Issue la plus fréquente : **{top_issue['resultat_humain']}** "
                f"avec **{int(top_issue['personnes']):,} personnes**.\n"
                "- Cette issue représente la trajectoire la plus courante observée."
            )

            st.divider()

            st.markdown("### 📊 Répartition des issues par profil (Top profils)")
            df_out_prof = pd.DataFrame()

            if "df_prof" in locals() and df_prof is not None and not df_prof.empty:
                top_profils = df_prof.head(TOPN)["categorie_personne"].tolist()
            else:
                top_profils = []

            if top_profils:
                q_out_prof = f"""
                SELECT
                NULLIF(TRIM(rh.categorie_personne),'') AS categorie_personne,
                NULLIF(TRIM(rh.resultat_humain),'') AS resultat_humain,
                COALESCE(SUM(rh.nombre),0) AS personnes
                FROM resultats_humain rh
                JOIN operations_stats os
                ON os.operation_id = rh.operation_id
                WHERE {where_os}
                AND NULLIF(TRIM(rh.categorie_personne),'') = ANY(%(top_profils)s::text[])
                AND NULLIF(TRIM(rh.resultat_humain),'') IS NOT NULL
                GROUP BY 1,2;
                """
                params2 = dict(params)
                params2["top_profils"] = top_profils

                df_out_prof = pd.read_sql(q_out_prof, engine, params=params2)

                if not df_out_prof.empty:
                    tot = df_out_prof.groupby("categorie_personne", as_index=False)["personnes"].sum().rename(columns={"personnes": "total"})
                    df_out_prof2 = df_out_prof.merge(tot, on="categorie_personne", how="left")
                    df_out_prof2["pct"] = (df_out_prof2["personnes"] / df_out_prof2["total"] * 100).round(1)

                    chart_stack = (
                        alt.Chart(df_out_prof2)
                        .mark_bar()
                        .encode(
                            x=alt.X("categorie_personne:N", title="Profil", sort="-y"),
                            y=alt.Y("pct:Q", title="Répartition des issues (%)", stack="normalize"),
                            color=alt.Color("resultat_humain:N", title="Issue"),
                            tooltip=[
                                alt.Tooltip("categorie_personne:N", title="Profil"),
                                alt.Tooltip("resultat_humain:N", title="Issue"),
                                alt.Tooltip("personnes:Q", title="Personnes", format=","),
                                alt.Tooltip("pct:Q", title="Part (%)", format=".1f"),
                            ],
                        )
                        .properties(height=350)
                    )
                    st.altair_chart(chart_stack, use_container_width=True)

                    st.markdown("### 🧠 Analyse — Issues par profil")
                    st.markdown(
                        "- Certaines issues sont beaucoup plus présentes pour certains profils.\n"
                        "- Cela aide à adapter la prise en charge selon le type de personne impliquée."
                    )
                else:
                    st.info("Pas assez de données pour détailler les issues par profil.")
            else:
                st.info("Impossible de construire la répartition par profil (profils manquants).")

            st.divider()

            st.markdown("### 🧩 Matrice Profil × Issue (heatmap)")
            if not df_out_prof.empty:
                heat = (
                    alt.Chart(df_out_prof)
                    .mark_rect()
                    .encode(
                        x=alt.X("categorie_personne:N", title="Profil", sort="-y"),
                        y=alt.Y("resultat_humain:N", title="Issue", sort="-x"),
                        color=alt.Color("personnes:Q", title="Personnes"),
                        tooltip=[
                            alt.Tooltip("categorie_personne:N", title="Profil"),
                            alt.Tooltip("resultat_humain:N", title="Issue"),
                            alt.Tooltip("personnes:Q", title="Personnes", format=","),
                        ],
                    )
                    .properties(height=450)
                )
                st.altair_chart(heat, use_container_width=True)
            else:
                st.info("Heatmap non disponible : pas assez de données profil × issue.")

        st.divider()

        st.markdown("### ✅ Conclusion")
        st.markdown(
            "On lit cette page comme une histoire humaine :\n"
            "- **Pipeline** : volume total et proportions secourues / blessées / décédées / fausse alerte.\n"
            "- **Profils** : qui représente le volume et qui présente le plus de gravité.\n"
            "- **Issues** : comment les situations se terminent et comment cela varie selon les profils."
        )

    except Exception as e:
        st.error(f"❌ Erreur : {e}")
        st.exception(e)


   