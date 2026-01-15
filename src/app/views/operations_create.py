"""
Création d'une nouvelle opération
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
from src.database.load_database import engine
from src.crud.operations_crud import insert_operation
from src.crud.flotteurs_crud import insert_flotteur
from src.crud.resultat_humain_crud import insert_resultat_humain
from src.crud.operations_stats_crud import insert_operations_stats
from src.app.utils.queries import OperationsQueries
from src.app.utils.data_loader import get_reference_list_cached




def create_operation():
    st.subheader("➕ Créer une nouvelle opération")
    
    if st.button("⬅️ Retour à la liste"):
        st.session_state.action = 'list'
        st.rerun()
    
    try:
        next_operation_id = OperationsQueries.get_next_operation_id(engine)
    except:
        next_operation_id = 1
    
    with st.form("form_create_operation"):
        st.markdown("### 🚢 Informations essentielles")
        st.caption("Champs obligatoires marqués par *")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.number_input("ID Opération", value=next_operation_id, disabled=True, 
                          help="Auto-généré - Prochain ID disponible")
        with col2:
            cross_options = get_reference_list_cached('cross')
            cross = st.selectbox("CROSS*", cross_options,
                                key="create_cross",
                                format_func=lambda x: "Sélectionner..." if x is None else x,
                                help="Obligatoire")
        with col3:
            type_operation_options = get_reference_list_cached('type_operation')
            type_operation = st.selectbox("Type d'opération", type_operation_options,
                                         key="create_type_operation",
                                         format_func=lambda x: "Non spécifié" if x is None else x,
                                         help="SAR: vie humaine en danger, MAS: assistance navires, SUR: sûreté, POL: pollutions, DIV: autres")
        with col4:
            pass
        
        col1, col2, col3 = st.columns(3)
        with col1:
            date_alerte = st.date_input("Date de l'alerte*", value=date.today(), help="Obligatoire")
            heure_alerte = st.time_input("Heure de l'alerte*", value=datetime.now().time(), help="Obligatoire")
        with col2:
            date_fin = st.date_input("Date de fin", value=None, help="Optionnel")
            heure_fin = st.time_input("Heure de fin", value=None, help="Optionnel")
        with col3:
            fuseau_horaire = st.text_input("Fuseau horaire", value="Europe/Paris")
        
        # ===========================================
        # SECTION 2: ÉVÉNEMENT
        # ===========================================
        st.markdown("### 📋 Événement")
        
        col1, col2 = st.columns(2)
        with col1:
            evenement = st.text_input("Événement", placeholder="Ex: Naufrage, Avarie")
        with col2:
            categorie_evenement = st.text_input("Catégorie", placeholder="Ex: Accident, Assistance")
        
        # ===========================================
        # SECTION 3: ALERTE
        # ===========================================
        st.markdown("### 🚨 Détails de l'alerte")
        
        pourquoi_alerte = st.text_area("Raison de l'alerte", placeholder="Description détaillée de la situation", height=100)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            moyen_alerte = st.text_input("Moyen d'alerte", placeholder="Ex: VHF canal 16, Téléphone")
        with col2:
            qui_alerte = st.text_input("Qui donne l'alerte", placeholder="Ex: Pêcheur, SNSM, Plaisancier")
        with col3:
            categorie_qui_alerte = st.text_input("Catégorie émetteur", placeholder="Ex: Professionnel, Particulier")
        
        # ===========================================
        # SECTION 4: LOCALISATION
        # ===========================================
        st.markdown("### 📍 Localisation géographique")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            latitude = st.number_input("Latitude (WGS84)", value=0.0, format="%.6f", step=0.000001, 
                                      help="Exemple: 43.296482 (format décimal)")
            departement = st.text_input("Département", placeholder="Ex: 06, 13")
        with col2:
            longitude = st.number_input("Longitude (WGS84)", value=0.0, format="%.6f", step=0.000001,
                                       help="Exemple: 5.369780 (format décimal)")
            zone_responsabilite = st.text_input("Zone de responsabilité", placeholder="Ex: Atlantique, Méditerranée")
        with col3:
            fuseau_horaire = st.text_input("Fuseau horaire", placeholder="Ex: UTC+1, Europe/Paris")
            est_metropolitain = st.selectbox("Zone métropolitaine", [None, True, False], 
                                            key="create_est_metropolitain",
                                            format_func=lambda x: "Non spécifié" if x is None else ("Oui" if x else "Non"))
        
        # ===========================================
        # SECTION 5: CONDITIONS MÉTÉO/MER
        # ===========================================
        st.markdown("### 🌊 Conditions météorologiques et maritimes")
        
        col1, col2 = st.columns(2)
        with col1:
            st.caption("🌬️ Vent")
            vent_direction = st.number_input("Direction (degrés)", min_value=0, max_value=360, value=0, step=1,
                                            help="0-360° (0=Nord, 90=Est, 180=Sud, 270=Ouest)")
            vent_direction_options = get_reference_list_cached('vent_direction_categorie')
            vent_direction_categorie = st.selectbox("Direction (cardinal)", vent_direction_options,
                                                   key="create_vent_direction_categorie",
                                                   format_func=lambda x: "Non spécifié" if x is None else x)
            vent_force = st.number_input("Force (Beaufort)", min_value=0, max_value=12, value=0, step=1,
                                        help="Échelle de Beaufort: 0-12")
        with col2:
            st.caption("🌊 Mer")
            mer_force = st.number_input("État de la mer (Douglas)", min_value=0, max_value=9, value=0, step=1,
                                       help="Échelle Douglas: 0-9")
        
        # ===========================================
        # SECTION 6: AUTORITÉS IMPLIQUÉES
        # ===========================================
        st.markdown("### 👮 Autorités et coordination")
        
        col1, col2 = st.columns(2)
        with col1:
            autorite = st.text_input("Autorité principale", placeholder="Ex: Préfecture maritime Méditerranée")
        with col2:
            seconde_autorite = st.text_input("Autorité secondaire", placeholder="Ex: Gendarmerie maritime")
        
        # ===========================================
        # SECTION 7: RAPPORTS ET SYSTÈME
        # ===========================================
        st.markdown("### 📄 Rapports et système")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            numero_sitrep = st.number_input("Numéro SITREP", min_value=0, value=0,
                                           help="Numéro de rapport de situation")
        with col2:
            cross_sitrep = st.text_input("CROSS SITREP", placeholder="Ex: Med-SITREP-2024-001")
        with col3:
            systeme_source_options = get_reference_list_cached('systeme_source')
            systeme_source = st.selectbox("Système source", systeme_source_options,
                                         key="create_systeme_source",
                                         format_func=lambda x: "Non spécifié" if x is None else x)
        
        st.divider()
        
        # ===========================================
        # SECTION 8: FLOTTEUR (OPTIONNEL - EXPANDER)
        # ===========================================
        with st.expander("⛵ Flotteur impliqué (optionnel)", expanded=False):
            st.markdown("*Remplir les informations du flotteur (si applicable)*")
            col1, col2, col3 = st.columns(3)
            with col1:
                pavillon_options = get_reference_list_cached('pavillon')
                pavillon = st.selectbox("Pavillon", pavillon_options,
                                       key="create_pavillon",
                                       format_func=lambda x: "Non spécifié" if x is None else x)
                type_flotteur = st.text_input("Type de flotteur", placeholder="Ex: Voilier, Chalutier, Planche à voile")
            with col2:
                categorie_flotteur_options = get_reference_list_cached('categorie_flotteur')
                categorie_flotteur = st.selectbox("Catégorie", categorie_flotteur_options,
                                                 key="create_categorie_flotteur",
                                                 format_func=lambda x: "Non spécifié" if x is None else x)
                resultat_flotteur_options = get_reference_list_cached('resultat_flotteur')
                resultat_flotteur = st.selectbox("Résultat", resultat_flotteur_options,
                    key="create_resultat_flotteur",
                    format_func=lambda x: "Non spécifié" if x is None else x)
            with col3:
                numero_immat = st.text_input("N° immatriculation", placeholder="Ex: ABC123")
                numero_ordre = st.number_input("Numéro d'ordre", min_value=1, value=1, help="Ordre du flotteur dans l'opération")
            
            add_flotteur = bool(pavillon or type_flotteur or categorie_flotteur or resultat_flotteur or numero_immat)
        
        # ===========================================
        # SECTION 9: RÉSULTATS HUMAINS (OPTIONNEL - EXPANDER)
        # ===========================================
        with st.expander("👥 Résultats humains (optionnel)", expanded=False):
            st.markdown("*Remplir les résultats humains de l'opération (si applicable)*")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                categorie_personne_options = get_reference_list_cached('categorie_personne')
                categorie_personne = st.selectbox("Catégorie de personne", categorie_personne_options,
                    key="create_categorie_personne",
                    format_func=lambda x: "Non spécifié" if x is None else x)
            with col2:
                resultat_humain_options = get_reference_list_cached('resultat_humain')
                resultat_humain = st.selectbox("Résultat", resultat_humain_options,
                    key="create_resultat_humain",
                    format_func=lambda x: "Non spécifié" if x is None else x)
            with col3:
                nombre = st.number_input("Nombre", min_value=1, value=1, help="Nombre de personnes")
            with col4:
                dont_nombre_blesse = st.number_input("Dont blessés", min_value=0, value=0)
            
            add_humain = bool(categorie_personne or resultat_humain or nombre > 0)
        
        # ===========================================
        # SECTION 10: STATISTIQUES (OPTIONNELLES)
        # ===========================================
        with st.expander("📊 Statistiques de l'opération (optionnel)", expanded=False):
            st.markdown("### Indicateurs humains")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                nb_impliques = st.number_input("Nb impliqués", min_value=0, value=0, help="Nombre total de personnes impliquées")
                nb_secourues = st.number_input("Nb secourus", min_value=0, value=0, help="Personnes secourues")
                nb_assistees = st.number_input("Nb assistées", min_value=0, value=0, help="Personnes assistées")
            with col2:
                nb_deces = st.number_input("Nb décès", min_value=0, value=0, help="Nombre total de décès")
                nb_deces_accidentel = st.number_input("Décès accidentels", min_value=0, value=0)
                nb_deces_naturel = st.number_input("Décès naturels", min_value=0, value=0)
            with col3:
                nb_blesses = st.number_input("Nb blessés", min_value=0, value=0, help="Nombre de blessés")
                nb_disparues = st.number_input("Nb disparus", min_value=0, value=0, help="Personnes disparues")
                nb_retrouvees = st.number_input("Nb retrouvées", min_value=0, value=0, help="Personnes retrouvées")
            with col4:
                nb_tirees_affaire = st.number_input("Tirées d'affaire seules", min_value=0, value=0)
                nb_fausse_alerte = st.number_input("Fausse alerte", min_value=0, value=0)
                nb_deces_disparues = st.number_input("Décès ou disparus", min_value=0, value=0)
            
            st.markdown("##### 🚤 Informations flotteurs")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                nb_flotteurs_commerce = st.number_input("Commerce", min_value=0, value=0)
                nb_flotteurs_peche = st.number_input("Pêche", min_value=0, value=0)
            with col2:
                nb_flotteurs_plaisance = st.number_input("Plaisance", min_value=0, value=0)
                nb_flotteurs_loisirs = st.number_input("Loisirs nautiques", min_value=0, value=0)
            with col3:
                nb_aeronefs = st.number_input("Aéronefs", min_value=0, value=0)
                nb_flotteurs_autre = st.number_input("Autre", min_value=0, value=0)
            with col4:
                st.caption("Détails plaisance")
                nb_plaisance_voile = st.number_input("Voile", min_value=0, value=0)
                nb_plaisance_moteur = st.number_input("Moteur", min_value=0, value=0)
            
            st.markdown("##### 🌊 Contexte et localisation")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                concerne_plongee = st.checkbox("Concerne la plongée")
                implique_wingfoil = st.checkbox("Implique wingfoil")
                avec_clandestins = st.checkbox("Avec clandestins")
            with col2:
                est_dans_stm = st.checkbox("Dans STM (Séparation du Trafic Maritime)")
                nom_stm = st.text_input("Nom STM", placeholder="Ex: Ouessant")
            with col3:
                est_dans_dst = st.checkbox("Dans DST (Dispositif de Séparation du Trafic)")
                nom_dst = st.text_input("Nom DST", placeholder="Ex: Pas-de-Calais")
            with col4:
                distance_cote_metres = st.number_input("Distance côte (m)", min_value=0, value=0)
                distance_cote_milles = st.number_input("Distance côte (NM)", min_value=0.0, value=0.0, format="%.2f")
            
            st.markdown("##### 🌊 Marée et contexte")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                maree_port = st.text_input("Port de marée", placeholder="Ex: Brest, Le Havre")
            with col2:
                maree_coefficient = st.number_input("Coefficient", min_value=20, max_value=120, value=70,
                                                   help="Coefficient de marée: 20-120")
            with col3:
                maree_categorie_options = get_reference_list_cached('maree_categorie')
                maree_categorie = st.selectbox("Catégorie marée", maree_categorie_options,
                                              key="create_maree_categorie",
                                              format_func=lambda x: "Non spécifié" if x is None else x)
            with col4:
                prefecture_maritime_options = get_reference_list_cached('prefecture_maritime')
                prefecture_maritime = st.selectbox("Préfecture maritime", prefecture_maritime_options,
                                                  key="create_prefecture_maritime",
                                                  format_func=lambda x: "Non spécifié" if x is None else x)
            
            add_stats = bool(nb_impliques > 0 or nb_secourues > 0 or nb_deces > 0 or nb_blesses > 0 or 
                           nb_flotteurs_commerce > 0 or nb_flotteurs_peche > 0 or nb_flotteurs_plaisance > 0)
        
        st.divider()
        
        submitted = st.form_submit_button("✅ Créer l'opération", type="primary", use_container_width=True)
        
        if submitted:
            if not cross:
                st.error("❌ Le champ CROSS est obligatoire")
            else:
                try:
                    date_heure_alerte = datetime.combine(date_alerte, heure_alerte)
                    date_heure_fin = None
                    if date_fin and heure_fin:
                        date_heure_fin = datetime.combine(date_fin, heure_fin)
                    
                    operation_data = {
                        "cross": cross,
                        "date_heure_reception_alerte": date_heure_alerte,
                        "date_heure_fin_operation": date_heure_fin,
                        "type_operation": type_operation if type_operation else None,
                        "evenement": evenement if evenement else None,
                        "categorie_evenement": categorie_evenement if categorie_evenement else None,
                        "departement": departement if departement else None,
                        "est_metropolitain": est_metropolitain,
                        "pourquoi_alerte": pourquoi_alerte if pourquoi_alerte else None,
                        "moyen_alerte": moyen_alerte if moyen_alerte else None,
                        "qui_alerte": qui_alerte if qui_alerte else None,
                        "categorie_qui_alerte": categorie_qui_alerte if categorie_qui_alerte else None,
                        "latitude": latitude if latitude != 0.0 else None,
                        "longitude": longitude if longitude != 0.0 else None,
                        "zone_responsabilite": zone_responsabilite if zone_responsabilite else None,
                        "fuseau_horaire": fuseau_horaire if fuseau_horaire else None,
                        "autorite": autorite if autorite else None,
                        "seconde_autorite": seconde_autorite if seconde_autorite else None,
                        "vent_direction": vent_direction if vent_direction != 0.0 else None,
                        "vent_direction_categorie": vent_direction_categorie if vent_direction_categorie else None,
                        "vent_force": vent_force if vent_force != 0.0 else None,
                        "mer_force": mer_force if mer_force != 0.0 else None,
                        "numero_sitrep": numero_sitrep if numero_sitrep != 0 else None,
                        "cross_sitrep": cross_sitrep if cross_sitrep else None,
                        "systeme_source": systeme_source if systeme_source else None,
                    }
                    
                    with st.spinner("Création en cours..."):
                        operation_id = insert_operation(operation_data)
                        
                        if operation_id:
                            st.success(f"✅ Opération créée ! ID: {operation_id}")
                            
                            if add_flotteur:
                                flotteur_data = {
                                    "operation_id": operation_id,
                                    "numero_ordre": numero_ordre,
                                    "pavillon": pavillon if pavillon else None,
                                    "type_flotteur": type_flotteur if type_flotteur else "Non spécifié",
                                    "categorie_flotteur": categorie_flotteur if categorie_flotteur else "Non spécifié",
                                    "resultat_flotteur": resultat_flotteur if resultat_flotteur else "Non spécifié",
                                    "numero_immatriculation": numero_immat if numero_immat else None,
                                }
                                insert_flotteur(flotteur_data)
                                st.success("✅ Flotteur ajouté")
                            
                            if add_humain:
                                humain_data = {
                                    "operation_id": operation_id,
                                    "categorie_personne": categorie_personne if categorie_personne else "Non spécifié",
                                    "resultat_humain": resultat_humain if resultat_humain else "Non spécifié",
                                    "nombre": nombre,
                                    "dont_nombre_blesse": dont_nombre_blesse if dont_nombre_blesse else 0,
                                }
                                insert_resultat_humain(humain_data)
                                st.success("✅ Résultat humain ajouté")
                            
                            if add_stats:
                                from datetime import date as date_type
                                operation_date = date_alerte
                                
                                stats_data = {
                                    "operation_id": operation_id,
                                    "date": operation_date,
                                    "annee": operation_date.year,
                                    "mois": operation_date.month,
                                    "jour": operation_date.day,
                                    "mois_texte": operation_date.strftime("%B"),
                                    "semaine": operation_date.isocalendar()[1],
                                    "annee_semaine": f"{operation_date.year}-W{operation_date.isocalendar()[1]:02d}",
                                    "jour_semaine": operation_date.strftime("%A"),
                                    "est_weekend": operation_date.weekday() >= 5,
                                    "est_jour_ferie": False,
                                    "est_vacances_scolaires": None,
                                    "phase_journee": None,
                                    "concerne_plongee": concerne_plongee,
                                    "implique_wingfoil": implique_wingfoil,
                                    "avec_clandestins": avec_clandestins,
                                    "distance_cote_metres": distance_cote_metres if distance_cote_metres > 0 else None,
                                    "distance_cote_milles_nautiques": distance_cote_milles if distance_cote_milles > 0 else None,
                                    "est_dans_stm": est_dans_stm,
                                    "nom_stm": nom_stm if nom_stm else None,
                                    "est_dans_dst": est_dans_dst,
                                    "nom_dst": nom_dst if nom_dst else None,
                                    "prefecture_maritime": prefecture_maritime if prefecture_maritime else None,
                                    "maree_port": maree_port if maree_port else None,
                                    "maree_coefficient": maree_coefficient if maree_coefficient else None,
                                    "maree_categorie": maree_categorie if maree_categorie else None,
                                    
                                    # Indicateurs humains
                                    "nombre_personnes_blessees": nb_blesses,
                                    "nombre_personnes_assistees": nb_assistees,
                                    "nombre_personnes_decedees": nb_deces,
                                    "nombre_personnes_decedees_accidentellement": nb_deces_accidentel,
                                    "nombre_personnes_decedees_naturellement": nb_deces_naturel,
                                    "nombre_personnes_disparues": nb_disparues,
                                    "nombre_personnes_impliquees_dans_fausse_alerte": nb_fausse_alerte,
                                    "nombre_personnes_retrouvees": nb_retrouvees,
                                    "nombre_personnes_secourues": nb_secourues,
                                    "nombre_personnes_tirees_daffaire_seule": nb_tirees_affaire,
                                    "nombre_personnes_tous_deces": nb_deces,
                                    "nombre_personnes_tous_deces_ou_disparues": nb_deces_disparues,
                                    "nombre_personnes_impliquees": nb_impliques,
                                    
                                    # Sans clandestins (mêmes valeurs si pas de clandestins)
                                    "nombre_personnes_blessees_sans_clandestins": nb_blesses if not avec_clandestins else 0,
                                    "nombre_personnes_assistees_sans_clandestins": nb_assistees if not avec_clandestins else 0,
                                    "nombre_personnes_decedees_sans_clandestins": nb_deces if not avec_clandestins else 0,
                                    "nombre_personnes_decedees_accidentellement_sans_clandestins": nb_deces_accidentel if not avec_clandestins else 0,
                                    "nombre_personnes_decedees_naturellement_sans_clandestins": nb_deces_naturel if not avec_clandestins else 0,
                                    "nombre_personnes_disparues_sans_clandestins": nb_disparues if not avec_clandestins else 0,
                                    "nombre_personnes_impliquees_dans_fausse_alerte_sans_clandestins": nb_fausse_alerte if not avec_clandestins else 0,
                                    "nombre_personnes_retrouvees_sans_clandestins": nb_retrouvees if not avec_clandestins else 0,
                                    "nombre_personnes_secourues_sans_clandestins": nb_secourues if not avec_clandestins else 0,
                                    "nombre_personnes_tirees_daffaire_seule_sans_clandestins": nb_tirees_affaire if not avec_clandestins else 0,
                                    "nombre_personnes_tous_deces_sans_clandestins": nb_deces if not avec_clandestins else 0,
                                    "nombre_personnes_tous_deces_ou_disparues_sans_clandestins": nb_deces_disparues if not avec_clandestins else 0,
                                    "nombre_personnes_impliquees_sans_clandestins": nb_impliques if not avec_clandestins else 0,
                                    
                                    # Flotteurs
                                    "nombre_flotteurs_commerce_impliques": nb_flotteurs_commerce,
                                    "nombre_flotteurs_peche_impliques": nb_flotteurs_peche,
                                    "nombre_flotteurs_plaisance_impliques": nb_flotteurs_plaisance,
                                    "nombre_flotteurs_loisirs_nautiques_impliques": nb_flotteurs_loisirs,
                                    "nombre_aeronefs_impliques": nb_aeronefs,
                                    "nombre_flotteurs_autre_impliques": nb_flotteurs_autre,
                                    "nombre_flotteurs_annexe_impliques": 0,
                                    "nombre_flotteurs_autre_loisir_nautique_impliques": 0,
                                    "nombre_flotteurs_canoe_kayak_aviron_impliques": 0,
                                    "nombre_flotteurs_engin_de_plage_impliques": 0,
                                    "nombre_flotteurs_kitesurf_impliques": 0,
                                    "nombre_flotteurs_plaisance_voile_legere_impliques": 0,
                                    "nombre_flotteurs_plaisance_a_moteur_impliques": nb_plaisance_moteur,
                                    "nombre_flotteurs_plaisance_a_moteur_moins_8m_impliques": 0,
                                    "nombre_flotteurs_plaisance_a_moteur_plus_8m_impliques": 0,
                                    "nombre_flotteurs_plaisance_a_voile_impliques": nb_plaisance_voile,
                                    "nombre_flotteurs_planche_a_voile_impliques": 0,
                                    "nombre_flotteurs_ski_nautique_impliques": 0,
                                    "nombre_flotteurs_surf_impliques": 0,
                                    "nombre_flotteurs_vehicule_nautique_a_moteur_impliques": 0,
                                    
                                    # Sans flotteur
                                    "sans_flotteur_implique": not add_flotteur,
                                }
                                insert_operations_stats(stats_data)
                                st.success("✅ Statistiques ajoutées")
                            
                            st.balloons()
                            st.success("🎉 Création terminée ! Retour à la liste dans 3 secondes...")
                            import time
                            time.sleep(3)
                            st.session_state.action = 'list'
                            st.rerun()
                        else:
                            st.error("❌ Erreur lors de la création")
                
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
                    st.exception(e)
