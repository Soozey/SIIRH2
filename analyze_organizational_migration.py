#!/usr/bin/env python3
"""
Script d'analyse pour la migration vers la structure organisationnelle hiérarchique.

Ce script analyse les données organisationnelles existantes pour :
1. Identifier les structures organisationnelles actuelles
2. Détecter les incohérences et conflits potentiels
3. Proposer une hiérarchie basée sur les combinaisons existantes
4. Générer un rapport de migration détaillé
"""

import psycopg2
import psycopg2.extras
import json
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass
from datetime import datetime


@dataclass
class OrganizationalCombination:
    """Représente une combinaison organisationnelle trouvée dans les données"""
    etablissement: Optional[str]
    departement: Optional[str]
    service: Optional[str]
    unite: Optional[str]
    worker_count: int
    worker_ids: List[int]


@dataclass
class HierarchyNode:
    """Nœud dans la hiérarchie proposée"""
    name: str
    level: str
    parent: Optional['HierarchyNode']
    children: List['HierarchyNode']
    worker_count: int
    
    def __post_init__(self):
        if not hasattr(self, 'children'):
            self.children = []


class OrganizationalMigrationAnalyzer:
    """Analyseur pour la migration organisationnelle"""
    
    def __init__(self, db_config: Dict = None):
        self.db_config = db_config or {
            'host': '127.0.0.1',
            'port': 5432,
            'database': 'db_siirh_app',
            'user': 'postgres',
            'password': 'tantely123'
        }
        self.employers = {}
        self.organizational_combinations = defaultdict(list)
        self.hierarchy_proposals = {}
        self.conflicts = []
        self.statistics = {}
    
    def connect_db(self):
        """Connexion à la base de données PostgreSQL"""
        conn = psycopg2.connect(**self.db_config)
        conn.autocommit = True
        return conn
    
    def analyze_all_employers(self) -> Dict:
        """Analyse complète de tous les employeurs"""
        print("🔍 Analyse des données organisationnelles existantes...")
        
        with self.connect_db() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                # Récupérer tous les employeurs
                cursor.execute("""
                    SELECT id, raison_sociale, etablissements, departements, services, unites
                    FROM employers
                """)
                employers = cursor.fetchall()
                
                for employer in employers:
                    print(f"\n📊 Analyse de l'employeur: {employer['raison_sociale']} (ID: {employer['id']})")
                    self.analyze_employer(conn, employer)
        
        # Générer les statistiques globales
        self.generate_global_statistics()
        
        return {
            'employers': self.employers,
            'combinations': dict(self.organizational_combinations),
            'hierarchy_proposals': self.hierarchy_proposals,
            'conflicts': self.conflicts,
            'statistics': self.statistics
        }
    
    def analyze_employer(self, conn, employer):
        """Analyse d'un employeur spécifique"""
        employer_id = employer['id']
        employer_name = employer['raison_sociale']
        
        # Parser les listes organisationnelles JSON
        etablissements = json.loads(employer['etablissements'] or '[]')
        departements = json.loads(employer['departements'] or '[]')
        services = json.loads(employer['services'] or '[]')
        unites = json.loads(employer['unites'] or '[]')
        
        print(f"  📋 Listes définies:")
        print(f"    - Établissements: {len(etablissements)} ({etablissements})")
        print(f"    - Départements: {len(departements)} ({departements})")
        print(f"    - Services: {len(services)} ({services})")
        print(f"    - Unités: {len(unites)} ({unites})")
        
        # Analyser les combinaisons utilisées par les travailleurs
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("""
                SELECT id, matricule, nom, prenom, etablissement, departement, service, unite
                FROM workers
                WHERE employer_id = %s
            """, (employer_id,))
            workers = cursor.fetchall()
        
        print(f"  👥 Travailleurs: {len(workers)}")
        
        # Collecter les combinaisons uniques
        combinations = defaultdict(list)
        for worker in workers:
            combo_key = (
                worker['etablissement'],
                worker['departement'], 
                worker['service'],
                worker['unite']
            )
            combinations[combo_key].append({
                'id': worker['id'],
                'matricule': worker['matricule'],
                'nom': worker['nom'],
                'prenom': worker['prenom']
            })
        
        print(f"  🔗 Combinaisons uniques trouvées: {len(combinations)}")
        
        # Analyser chaque combinaison
        employer_combinations = []
        for combo_key, workers_list in combinations.items():
            etablissement, departement, service, unite = combo_key
            
            combination = OrganizationalCombination(
                etablissement=etablissement,
                departement=departement,
                service=service,
                unite=unite,
                worker_count=len(workers_list),
                worker_ids=[w['id'] for w in workers_list]
            )
            employer_combinations.append(combination)
            
            print(f"    • {etablissement or 'N/A'} → {departement or 'N/A'} → {service or 'N/A'} → {unite or 'N/A'} ({len(workers_list)} travailleurs)")
        
        # Détecter les conflits et incohérences
        conflicts = self.detect_conflicts(employer_id, employer_name, etablissements, departements, services, unites, employer_combinations)
        
        # Proposer une hiérarchie
        hierarchy = self.propose_hierarchy(employer_id, employer_name, employer_combinations)
        
        # Stocker les résultats
        self.employers[employer_id] = {
            'name': employer_name,
            'defined_lists': {
                'etablissements': etablissements,
                'departements': departements,
                'services': services,
                'unites': unites
            },
            'combinations': employer_combinations,
            'conflicts': conflicts,
            'proposed_hierarchy': hierarchy,
            'worker_count': len(workers)
        }
        
        self.organizational_combinations[employer_id] = employer_combinations
        self.hierarchy_proposals[employer_id] = hierarchy
        self.conflicts.extend(conflicts)
    
    def detect_conflicts(self, employer_id: int, employer_name: str, 
                        etablissements: List[str], departements: List[str], 
                        services: List[str], unites: List[str],
                        combinations: List[OrganizationalCombination]) -> List[Dict]:
        """Détecte les conflits et incohérences"""
        conflicts = []
        
        # Collecter toutes les valeurs utilisées
        used_etablissements = set()
        used_departements = set()
        used_services = set()
        used_unites = set()
        
        for combo in combinations:
            if combo.etablissement:
                used_etablissements.add(combo.etablissement)
            if combo.departement:
                used_departements.add(combo.departement)
            if combo.service:
                used_services.add(combo.service)
            if combo.unite:
                used_unites.add(combo.unite)
        
        # Conflit 1: Valeurs utilisées mais non définies dans les listes
        undefined_etablissements = used_etablissements - set(etablissements)
        undefined_departements = used_departements - set(departements)
        undefined_services = used_services - set(services)
        undefined_unites = used_unites - set(unites)
        
        if undefined_etablissements:
            conflicts.append({
                'type': 'undefined_values',
                'level': 'etablissement',
                'employer_id': employer_id,
                'employer_name': employer_name,
                'values': list(undefined_etablissements),
                'description': f"Établissements utilisés mais non définis dans la liste: {undefined_etablissements}"
            })
        
        if undefined_departements:
            conflicts.append({
                'type': 'undefined_values',
                'level': 'departement',
                'employer_id': employer_id,
                'employer_name': employer_name,
                'values': list(undefined_departements),
                'description': f"Départements utilisés mais non définis dans la liste: {undefined_departements}"
            })
        
        if undefined_services:
            conflicts.append({
                'type': 'undefined_values',
                'level': 'service',
                'employer_id': employer_id,
                'employer_name': employer_name,
                'values': list(undefined_services),
                'description': f"Services utilisés mais non définis dans la liste: {undefined_services}"
            })
        
        if undefined_unites:
            conflicts.append({
                'type': 'undefined_values',
                'level': 'unite',
                'employer_id': employer_id,
                'employer_name': employer_name,
                'values': list(undefined_unites),
                'description': f"Unités utilisées mais non définies dans la liste: {undefined_unites}"
            })
        
        # Conflit 2: Valeurs définies mais jamais utilisées
        unused_etablissements = set(etablissements) - used_etablissements
        unused_departements = set(departements) - used_departements
        unused_services = set(services) - used_services
        unused_unites = set(unites) - used_unites
        
        if unused_etablissements:
            conflicts.append({
                'type': 'unused_values',
                'level': 'etablissement',
                'employer_id': employer_id,
                'employer_name': employer_name,
                'values': list(unused_etablissements),
                'description': f"Établissements définis mais jamais utilisés: {unused_etablissements}"
            })
        
        # Conflit 3: Combinaisons incohérentes (ex: même département dans plusieurs établissements)
        dept_to_etablissements = defaultdict(set)
        service_to_departements = defaultdict(set)
        unite_to_services = defaultdict(set)
        
        for combo in combinations:
            if combo.etablissement and combo.departement:
                dept_to_etablissements[combo.departement].add(combo.etablissement)
            if combo.departement and combo.service:
                service_to_departements[combo.service].add(combo.departement)
            if combo.service and combo.unite:
                unite_to_services[combo.unite].add(combo.service)
        
        # Départements dans plusieurs établissements
        for dept, etablissements_set in dept_to_etablissements.items():
            if len(etablissements_set) > 1:
                conflicts.append({
                    'type': 'multiple_parents',
                    'level': 'departement',
                    'employer_id': employer_id,
                    'employer_name': employer_name,
                    'child': dept,
                    'parents': list(etablissements_set),
                    'description': f"Département '{dept}' trouvé dans plusieurs établissements: {etablissements_set}"
                })
        
        # Services dans plusieurs départements
        for service, departements_set in service_to_departements.items():
            if len(departements_set) > 1:
                conflicts.append({
                    'type': 'multiple_parents',
                    'level': 'service',
                    'employer_id': employer_id,
                    'employer_name': employer_name,
                    'child': service,
                    'parents': list(departements_set),
                    'description': f"Service '{service}' trouvé dans plusieurs départements: {departements_set}"
                })
        
        # Unités dans plusieurs services
        for unite, services_set in unite_to_services.items():
            if len(services_set) > 1:
                conflicts.append({
                    'type': 'multiple_parents',
                    'level': 'unite',
                    'employer_id': employer_id,
                    'employer_name': employer_name,
                    'child': unite,
                    'parents': list(services_set),
                    'description': f"Unité '{unite}' trouvée dans plusieurs services: {services_set}"
                })
        
        return conflicts
    
    def propose_hierarchy(self, employer_id: int, employer_name: str, 
                         combinations: List[OrganizationalCombination]) -> Dict:
        """Propose une hiérarchie basée sur les combinaisons existantes"""
        
        # Construire l'arbre hiérarchique
        root_nodes = {}  # etablissement -> HierarchyNode
        
        for combo in combinations:
            # Créer ou récupérer le nœud établissement
            etablissement_name = combo.etablissement or "Non défini"
            if etablissement_name not in root_nodes:
                root_nodes[etablissement_name] = HierarchyNode(
                    name=etablissement_name,
                    level="etablissement",
                    parent=None,
                    children=[],
                    worker_count=0
                )
            
            etablissement_node = root_nodes[etablissement_name]
            etablissement_node.worker_count += combo.worker_count
            
            # Créer ou récupérer le nœud département
            if combo.departement:
                departement_name = combo.departement
                departement_node = None
                
                # Chercher si le département existe déjà
                for child in etablissement_node.children:
                    if child.name == departement_name and child.level == "departement":
                        departement_node = child
                        break
                
                if not departement_node:
                    departement_node = HierarchyNode(
                        name=departement_name,
                        level="departement",
                        parent=etablissement_node,
                        children=[],
                        worker_count=0
                    )
                    etablissement_node.children.append(departement_node)
                
                departement_node.worker_count += combo.worker_count
                
                # Créer ou récupérer le nœud service
                if combo.service:
                    service_name = combo.service
                    service_node = None
                    
                    # Chercher si le service existe déjà
                    for child in departement_node.children:
                        if child.name == service_name and child.level == "service":
                            service_node = child
                            break
                    
                    if not service_node:
                        service_node = HierarchyNode(
                            name=service_name,
                            level="service",
                            parent=departement_node,
                            children=[],
                            worker_count=0
                        )
                        departement_node.children.append(service_node)
                    
                    service_node.worker_count += combo.worker_count
                    
                    # Créer ou récupérer le nœud unité
                    if combo.unite:
                        unite_name = combo.unite
                        unite_node = None
                        
                        # Chercher si l'unité existe déjà
                        for child in service_node.children:
                            if child.name == unite_name and child.level == "unite":
                                unite_node = child
                                break
                        
                        if not unite_node:
                            unite_node = HierarchyNode(
                                name=unite_name,
                                level="unite",
                                parent=service_node,
                                children=[],
                                worker_count=0
                            )
                            service_node.children.append(unite_node)
                        
                        unite_node.worker_count += combo.worker_count
        
        # Convertir en dictionnaire pour sérialisation
        def node_to_dict(node: HierarchyNode) -> Dict:
            return {
                'name': node.name,
                'level': node.level,
                'worker_count': node.worker_count,
                'children': [node_to_dict(child) for child in node.children]
            }
        
        hierarchy_dict = {
            'employer_id': employer_id,
            'employer_name': employer_name,
            'roots': [node_to_dict(node) for node in root_nodes.values()],
            'total_nodes': self.count_nodes(list(root_nodes.values())),
            'max_depth': self.calculate_max_depth(list(root_nodes.values()))
        }
        
        return hierarchy_dict
    
    def count_nodes(self, nodes: List[HierarchyNode]) -> int:
        """Compte le nombre total de nœuds"""
        count = len(nodes)
        for node in nodes:
            count += self.count_nodes(node.children)
        return count
    
    def calculate_max_depth(self, nodes: List[HierarchyNode]) -> int:
        """Calcule la profondeur maximale"""
        if not nodes:
            return 0
        
        max_depth = 1
        for node in nodes:
            child_depth = self.calculate_max_depth(node.children)
            max_depth = max(max_depth, 1 + child_depth)
        
        return max_depth
    
    def generate_global_statistics(self):
        """Génère les statistiques globales"""
        total_employers = len(self.employers)
        total_workers = sum(emp['worker_count'] for emp in self.employers.values())
        total_combinations = sum(len(emp['combinations']) for emp in self.employers.values())
        total_conflicts = len(self.conflicts)
        
        # Statistiques par type de conflit
        conflict_types = Counter(conflict['type'] for conflict in self.conflicts)
        
        # Statistiques par niveau organisationnel
        level_usage = defaultdict(int)
        for employer_data in self.employers.values():
            for combo in employer_data['combinations']:
                if combo.etablissement:
                    level_usage['etablissement'] += combo.worker_count
                if combo.departement:
                    level_usage['departement'] += combo.worker_count
                if combo.service:
                    level_usage['service'] += combo.worker_count
                if combo.unite:
                    level_usage['unite'] += combo.worker_count
        
        self.statistics = {
            'total_employers': total_employers,
            'total_workers': total_workers,
            'total_combinations': total_combinations,
            'total_conflicts': total_conflicts,
            'conflict_types': dict(conflict_types),
            'level_usage': dict(level_usage),
            'analysis_date': datetime.now().isoformat()
        }
    
    def generate_report(self, output_file: str = "migration_analysis_report.md"):
        """Génère un rapport détaillé de l'analyse"""
        
        report = f"""# Rapport d'Analyse - Migration Structure Organisationnelle Hiérarchique

**Date d'analyse:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## 📊 Statistiques Globales

- **Employeurs analysés:** {self.statistics['total_employers']}
- **Travailleurs total:** {self.statistics['total_workers']}
- **Combinaisons organisationnelles uniques:** {self.statistics['total_combinations']}
- **Conflits détectés:** {self.statistics['total_conflicts']}

### Utilisation par Niveau Organisationnel
"""
        
        for level, count in self.statistics['level_usage'].items():
            percentage = (count / self.statistics['total_workers']) * 100 if self.statistics['total_workers'] > 0 else 0
            report += f"- **{level.capitalize()}:** {count} travailleurs ({percentage:.1f}%)\n"
        
        report += f"""
### Types de Conflits Détectés
"""
        
        for conflict_type, count in self.statistics['conflict_types'].items():
            report += f"- **{conflict_type}:** {count} occurrences\n"
        
        report += f"""

## 🏢 Analyse par Employeur

"""
        
        for employer_id, employer_data in self.employers.items():
            report += f"""
### {employer_data['name']} (ID: {employer_id})

**Travailleurs:** {employer_data['worker_count']}  
**Combinaisons uniques:** {len(employer_data['combinations'])}  
**Conflits:** {len(employer_data['conflicts'])}

#### Listes Organisationnelles Définies
- **Établissements:** {len(employer_data['defined_lists']['etablissements'])} → {employer_data['defined_lists']['etablissements']}
- **Départements:** {len(employer_data['defined_lists']['departements'])} → {employer_data['defined_lists']['departements']}
- **Services:** {len(employer_data['defined_lists']['services'])} → {employer_data['defined_lists']['services']}
- **Unités:** {len(employer_data['defined_lists']['unites'])} → {employer_data['defined_lists']['unites']}

#### Combinaisons Utilisées
"""
            
            for i, combo in enumerate(employer_data['combinations'], 1):
                report += f"{i}. **{combo.etablissement or 'N/A'}** → **{combo.departement or 'N/A'}** → **{combo.service or 'N/A'}** → **{combo.unite or 'N/A'}** ({combo.worker_count} travailleurs)\n"
            
            if employer_data['conflicts']:
                report += f"""
#### ⚠️ Conflits Détectés
"""
                for conflict in employer_data['conflicts']:
                    report += f"- **{conflict['type']}** ({conflict['level']}): {conflict['description']}\n"
            
            # Hiérarchie proposée
            hierarchy = employer_data['proposed_hierarchy']
            report += f"""
#### 🌳 Hiérarchie Proposée
**Nœuds total:** {hierarchy['total_nodes']}  
**Profondeur max:** {hierarchy['max_depth']}

"""
            
            def format_hierarchy(nodes, indent=0):
                result = ""
                for node in nodes:
                    prefix = "  " * indent + ("├─ " if indent > 0 else "")
                    result += f"{prefix}**{node['name']}** ({node['level']}) - {node['worker_count']} travailleurs\n"
                    if node['children']:
                        result += format_hierarchy(node['children'], indent + 1)
                return result
            
            report += format_hierarchy(hierarchy['roots'])
        
        # Section des recommandations
        report += f"""

## 🎯 Recommandations de Migration

### Actions Prioritaires

"""
        
        if self.statistics['total_conflicts'] > 0:
            report += f"""
#### 1. Résolution des Conflits ({self.statistics['total_conflicts']} conflits)
"""
            
            # Grouper les conflits par type
            conflicts_by_type = defaultdict(list)
            for conflict in self.conflicts:
                conflicts_by_type[conflict['type']].append(conflict)
            
            for conflict_type, conflicts in conflicts_by_type.items():
                report += f"""
**{conflict_type.replace('_', ' ').title()} ({len(conflicts)} occurrences):**
"""
                for conflict in conflicts[:5]:  # Limiter à 5 exemples
                    report += f"- {conflict['employer_name']}: {conflict['description']}\n"
                
                if len(conflicts) > 5:
                    report += f"- ... et {len(conflicts) - 5} autres\n"
        
        report += f"""
#### 2. Stratégie de Migration

1. **Phase 1 - Préparation**
   - Créer la nouvelle table `organizational_structures`
   - Implémenter les services de migration
   - Tester sur un employeur pilote

2. **Phase 2 - Migration des Données**
   - Migrer les structures organisationnelles
   - Créer les relations hiérarchiques
   - Mettre à jour les références des travailleurs

3. **Phase 3 - Validation**
   - Vérifier l'intégrité des données migrées
   - Tester les fonctionnalités de filtrage
   - Former les utilisateurs

#### 3. Points d'Attention

- **Conflits de hiérarchie:** Résoudre les cas où un même élément apparaît sous plusieurs parents
- **Données manquantes:** Traiter les valeurs NULL ou vides
- **Performance:** Optimiser les requêtes hiérarchiques avec des index appropriés
- **Rollback:** Prévoir un mécanisme de retour en arrière

## 📋 Prochaines Étapes

1. ✅ Analyse des données existantes (terminée)
2. 🔄 Résolution des conflits identifiés
3. 🔄 Création du modèle de données hiérarchique
4. 🔄 Développement des services de migration
5. 🔄 Tests sur environnement de développement
6. 🔄 Migration en production

---

*Rapport généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}*
"""
        
        # Écrire le rapport
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Rapport détaillé généré: {output_file}")
        
        return report


def main():
    """Fonction principale"""
    print("🚀 Démarrage de l'analyse de migration organisationnelle")
    print("=" * 60)
    
    analyzer = OrganizationalMigrationAnalyzer()
    
    try:
        # Analyser tous les employeurs
        results = analyzer.analyze_all_employers()
        
        # Générer le rapport
        report = analyzer.generate_report()
        
        print("\n" + "=" * 60)
        print("✅ Analyse terminée avec succès!")
        print(f"📊 {analyzer.statistics['total_employers']} employeurs analysés")
        print(f"👥 {analyzer.statistics['total_workers']} travailleurs")
        print(f"🔗 {analyzer.statistics['total_combinations']} combinaisons uniques")
        print(f"⚠️  {analyzer.statistics['total_conflicts']} conflits détectés")
        
        if analyzer.statistics['total_conflicts'] > 0:
            print("\n🔍 Types de conflits:")
            for conflict_type, count in analyzer.statistics['conflict_types'].items():
                print(f"  - {conflict_type}: {count}")
        
        print(f"\n📄 Rapport détaillé disponible: migration_analysis_report.md")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()