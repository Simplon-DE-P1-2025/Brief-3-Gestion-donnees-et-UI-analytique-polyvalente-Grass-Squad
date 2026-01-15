# -*- coding: utf-8 -*-
"""
Module d'analyse pour les dashboards
Contient toutes les fonctions d'analyse SQL séparées des vues
"""

from .dashboard_analytics import (
    get_global_kpis,
    get_operations_map_data,
    get_database_info
)

from .date_analysis import (
    get_global_kpis as get_date_global_kpis,
    get_day_of_week_analysis,
    get_vacation_summer_analysis
)

from .zone_analysis import (
    get_geographic_kpis,
    get_map_coordinates,
    get_top_zones_cross
)

from .flotteurs_analysis import (
    get_operations_coverage,
    get_flotteurs_coverage,
    get_operations_by_category,
    get_charge_humaine_by_category,
    get_criticite_by_category,
    get_top_categories_for_outcomes,
    get_outcomes_by_category,
    get_pavillons_stats
)

from .meteo_analysis import (
    get_wind_force_analysis,
    get_sea_force_analysis,
    get_gravity_by_sea_force,
    get_sea_categories_distribution,
    get_tide_analysis
)

from .resultats_humain_analysis import (
    get_human_pipeline_kpis,
    get_profiles_analysis,
    get_human_outcomes_global,
    get_human_outcomes_by_profile
)

__all__ = [
    # Dashboard analytics
    'get_global_kpis',
    'get_operations_map_data',
    'get_database_info',
    
    # Date analysis
    'get_date_global_kpis',
    'get_day_of_week_analysis',
    'get_vacation_summer_analysis',
    
    # Zone analysis
    'get_geographic_kpis',
    'get_map_coordinates',
    'get_top_zones_cross',
    
    # Flotteurs analysis
    'get_operations_coverage',
    'get_flotteurs_coverage',
    'get_operations_by_category',
    'get_charge_humaine_by_category',
    'get_criticite_by_category',
    'get_top_categories_for_outcomes',
    'get_outcomes_by_category',
    'get_pavillons_stats',
    
    # Meteo analysis
    'get_wind_force_analysis',
    'get_sea_force_analysis',
    'get_gravity_by_sea_force',
    'get_sea_categories_distribution',
    'get_tide_analysis',
    
    # Resultats humain analysis
    'get_human_pipeline_kpis',
    'get_profiles_analysis',
    'get_human_outcomes_global',
    'get_human_outcomes_by_profile',
]
