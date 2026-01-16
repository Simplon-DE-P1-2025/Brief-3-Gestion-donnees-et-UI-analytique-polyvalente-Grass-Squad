import streamlit as st
import pandas as pd
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))
from src.database.load_database import engine
from src.analysis.zone_analysis import (
    get_geographic_kpis,
    get_map_coordinates,
    get_top_zones_cross
)


def render(engine):

  st.title("🗺️ Zone Géographique — Où se concentrent l’activité et la gravité ?")
  st.caption("Objectif : localiser l’activité (volume), la charge humaine (impliqués) et la gravité (taux de décès).")

  # Filtre géographique global
  st.markdown("### 🌍 Filtre géographique")
  france_metro_only = st.checkbox(
      "🇫🇷 France métropolitaine uniquement",
      value=False,
      help="Affiche uniquement les opérations en France métropolitaine (exclut les DOM-TOM)",
      key="zone_geo_france_metro_filter"
  )
  
  if france_metro_only:
      st.info("📍 Filtre actif : France métropolitaine (latitudes 41-51.5°N, longitudes -5.5-10°E)")
  else:
      st.info("🌍 Affichage : Tous les territoires français (métropole + DOM-TOM)")


  # Pas de filtres temporels
  where_sql = "1=1"
  params = {}


  # ------------------------------------------------------
  # Questions métier (claires)
  # ------------------------------------------------------
  st.markdown("### ❓ Questions métier")
  st.markdown(
      "- Quelles zones (CROSS) concentrent le plus d’opérations ?\n"
      "- Quelles zones concentrent la plus forte **charge humaine** (personnes impliquées) ?\n"
      "- Certaines zones ont-elles un **taux de décès** plus élevé que la moyenne ?"
  )

  st.divider()


  # ------------------------------------------------------
  # 1) KPI : Couverture GPS + KPI globaux d’impact
  # ------------------------------------------------------
  st.subheader("📌 Indicateurs clés")

  k = get_geographic_kpis(engine, where_sql, params, france_metro_only=france_metro_only)

  ops_total = int(k.ops_total or 0)
  ops_geo = int(k.ops_geo or 0)
  gps_pct = float(k.gps_pct or 0)
  impl_total = int(k.impliquees_total or 0)
  deces_total = int(k.deces_total or 0)
  taux_deces_global = float(k.taux_deces_global_pct or 0)

  c1, c2, c3, c4, c5 = st.columns(5)
  c1.metric("🚢 Opérations", f"{ops_total:,}")
  c2.metric("📍 Ops géolocalisées", f"{ops_geo:,}", f"{gps_pct:.1f}%")
  c2.caption("Près de 9 opérations sur 10 sont correctement localisées")
  c3.metric("👥 Personnes impliquées", f"{impl_total:,}")
  c4.metric("⚫ Décès", f"{deces_total:,}")
  c5.metric("📉 Taux décès global", f"{taux_deces_global:.2f}%")

  st.markdown("### 🧠 Lecture simple")
  st.markdown(
      "- La **couverture GPS** indique la fiabilité de l’analyse cartographique.\n"
      "- Le **taux de décès global** sert de référence pour comparer les zones."
  )

  st.divider()

  # ======================================================
  # 2) REQUÊTE + VISUEL #1 : Carte (échantillon)
  # ======================================================
  st.subheader("🌍 Carte des opérations (échantillon géolocalisé)")

  df_map = get_map_coordinates(engine, where_sql, params, limit=3000, france_metro_only=france_metro_only)

  if df_map.empty:
      st.info("Aucune donnée GPS disponible sur la période sélectionnée.")
  else:
      st.map(df_map)
      territory_info = "France métropolitaine" if france_metro_only else "tous territoires français"
      st.caption(f"Carte : affichage limité à 3000 points ({territory_info}). Les coordonnées invalides sont automatiquement exclues.")

  st.divider()

  # ======================================================
  # 3) REQUÊTE + VISUEL #2 : Top zones CROSS (volume & charge)
  # ======================================================
  st.subheader("🏷️ Top zones (CROSS) — volume & charge humaine")

  df_top = get_top_zones_cross(engine, where_sql, params, limit=15, france_metro_only=france_metro_only)

  left, right = st.columns([2, 1])
  with left:
      if df_top.empty:
          st.info("Aucune zone CROSS exploitable sur la période.")
      else:
          # Graph novice-friendly : volume + charge
          st.bar_chart(df_top.set_index("cross")[["operations", "impliquees"]])
  with right:
      if not df_top.empty:
          st.dataframe(df_top, width="stretch")

  # ------------------------------------------------------
  # Analyse automatique (basée sur df_top)
  # ------------------------------------------------------
  if not df_top.empty:
      top_volume = df_top.sort_values("operations", ascending=False).iloc[0]
      top_charge = df_top.sort_values("impliquees", ascending=False).iloc[0]

      # zones “plus à risque” que la moyenne (taux décès > taux global)
      zones_risque = df_top[df_top["taux_deces_pct"] > taux_deces_global].copy()
      zones_risque = zones_risque.sort_values("taux_deces_pct", ascending=False)

      st.markdown("### 🧠 Analyse automatique")
      st.markdown(
          f"- Zone la plus active : **{top_volume['cross']}** "
          f"({int(top_volume['operations']):,} opérations).\n"
          f"- Zone avec la plus forte charge humaine : **{top_charge['cross']}** "
          f"({int(top_charge['impliquees']):,} personnes impliquées).\n"
          f"- Référence : taux de décès global = **{taux_deces_global:.2f}%**."
      )

      if zones_risque.empty:
          st.markdown(
              "✅ **Aucune zone du Top 15** n’a un taux de décès supérieur à la référence globale "
              "(sur la période sélectionnée)."
          )
      else:
          worst = zones_risque.iloc[0]
          st.markdown(
              f"⚠️ **Zone à surveiller** : **{worst['cross']}** "
              f"avec un taux de décès **{float(worst['taux_deces_pct']):.2f}%** "
              f"(au-dessus du global **{taux_deces_global:.2f}%**).\n"
              "👉 À interpréter avec prudence si le volume est faible, mais c’est un bon signal pour approfondir."
          )

  st.markdown("### ✅ Conclusion")
  st.markdown(
      "Cette page identifie **où** l’activité se concentre et où la gravité est potentiellement plus forte.\n"
      "Suite logique : expliquer **pourquoi** → croiser avec **Alerte** et **Météo**."
  )

  
