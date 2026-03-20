
-- Table principale pour la hiérarchie organisationnelle
CREATE TABLE IF NOT EXISTS organizational_nodes (
    id SERIAL PRIMARY KEY,
    employer_id INTEGER NOT NULL REFERENCES employers(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES organizational_nodes(id) ON DELETE CASCADE,
    level VARCHAR(20) NOT NULL CHECK (level IN ('etablissement', 'departement', 'service', 'unite')),
    name VARCHAR(255) NOT NULL,
    path TEXT, -- Chemin hiérarchique complet (ex: "Siège > RH > Paie")
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes d'intégrité hiérarchique
    CONSTRAINT chk_level_hierarchy CHECK (
        (level = 'etablissement' AND parent_id IS NULL) OR
        (level = 'departement' AND parent_id IS NOT NULL) OR
        (level = 'service' AND parent_id IS NOT NULL) OR
        (level = 'unite' AND parent_id IS NOT NULL)
    ),
    
    -- Contrainte d'unicité par employeur et niveau
    CONSTRAINT uq_employer_parent_name UNIQUE (employer_id, parent_id, name),
    
    -- Index pour les performances
    INDEX idx_organizational_nodes_employer (employer_id),
    INDEX idx_organizational_nodes_parent (parent_id),
    INDEX idx_organizational_nodes_level (level),
    INDEX idx_organizational_nodes_path (path),
    INDEX idx_organizational_nodes_active (is_active)
);

-- Trigger pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_organizational_nodes_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_organizational_nodes_updated_at
    BEFORE UPDATE ON organizational_nodes
    FOR EACH ROW
    EXECUTE FUNCTION update_organizational_nodes_updated_at();

-- Fonction pour calculer le chemin hiérarchique
CREATE OR REPLACE FUNCTION calculate_organizational_path(node_id INTEGER)
RETURNS TEXT AS $$
DECLARE
    path_result TEXT := '';
    current_node RECORD;
    parent_path TEXT;
BEGIN
    -- Récupérer le nœud actuel
    SELECT * INTO current_node FROM organizational_nodes WHERE id = node_id;
    
    IF NOT FOUND THEN
        RETURN NULL;
    END IF;
    
    -- Si c'est un nœud racine (établissement)
    IF current_node.parent_id IS NULL THEN
        RETURN current_node.name;
    END IF;
    
    -- Récupérer le chemin du parent récursivement
    parent_path := calculate_organizational_path(current_node.parent_id);
    
    -- Construire le chemin complet
    IF parent_path IS NOT NULL THEN
        RETURN parent_path || ' > ' || current_node.name;
    ELSE
        RETURN current_node.name;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour mettre à jour automatiquement le chemin
CREATE OR REPLACE FUNCTION update_organizational_path()
RETURNS TRIGGER AS $$
BEGIN
    NEW.path = calculate_organizational_path(NEW.id);
    
    -- Mettre à jour les chemins des enfants si le nom change
    IF TG_OP = 'UPDATE' AND OLD.name != NEW.name THEN
        UPDATE organizational_nodes 
        SET path = calculate_organizational_path(id)
        WHERE parent_id = NEW.id OR id IN (
            SELECT id FROM organizational_nodes 
            WHERE path LIKE OLD.name || ' > %' OR path LIKE '% > ' || OLD.name || ' > %'
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_organizational_path_update
    BEFORE INSERT OR UPDATE ON organizational_nodes
    FOR EACH ROW
    EXECUTE FUNCTION update_organizational_path();

-- Fonction pour valider la hiérarchie (éviter les cycles)
CREATE OR REPLACE FUNCTION validate_organizational_hierarchy(node_id INTEGER, new_parent_id INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    current_parent INTEGER;
    depth INTEGER := 0;
    max_depth INTEGER := 10; -- Limite de profondeur pour éviter les boucles infinies
BEGIN
    -- Si pas de parent, c'est valide
    IF new_parent_id IS NULL THEN
        RETURN TRUE;
    END IF;
    
    -- Vérifier qu'on ne crée pas un cycle
    current_parent := new_parent_id;
    
    WHILE current_parent IS NOT NULL AND depth < max_depth LOOP
        -- Si on retombe sur le nœud original, c'est un cycle
        IF current_parent = node_id THEN
            RETURN FALSE;
        END IF;
        
        -- Remonter au parent suivant
        SELECT parent_id INTO current_parent 
        FROM organizational_nodes 
        WHERE id = current_parent;
        
        depth := depth + 1;
    END LOOP;
    
    -- Si on a atteint la limite de profondeur, considérer comme invalide
    IF depth >= max_depth THEN
        RETURN FALSE;
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Trigger pour valider la hiérarchie avant insertion/mise à jour
CREATE OR REPLACE FUNCTION check_organizational_hierarchy()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT validate_organizational_hierarchy(NEW.id, NEW.parent_id) THEN
        RAISE EXCEPTION 'Cycle détecté dans la hiérarchie organisationnelle pour le nœud %', NEW.id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_organizational_hierarchy_check
    BEFORE INSERT OR UPDATE ON organizational_nodes
    FOR EACH ROW
    EXECUTE FUNCTION check_organizational_hierarchy();

-- Vue pour faciliter les requêtes hiérarchiques
CREATE OR REPLACE VIEW organizational_tree AS
WITH RECURSIVE org_tree AS (
    -- Nœuds racines (établissements)
    SELECT 
        id,
        employer_id,
        parent_id,
        level,
        name,
        path,
        sort_order,
        is_active,
        0 as depth,
        ARRAY[id] as path_ids,
        ARRAY[name] as path_names
    FROM organizational_nodes 
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Nœuds enfants
    SELECT 
        n.id,
        n.employer_id,
        n.parent_id,
        n.level,
        n.name,
        n.path,
        n.sort_order,
        n.is_active,
        t.depth + 1,
        t.path_ids || n.id,
        t.path_names || n.name
    FROM organizational_nodes n
    JOIN org_tree t ON n.parent_id = t.id
)
SELECT * FROM org_tree;

-- Commentaires sur les tables et colonnes
COMMENT ON TABLE organizational_nodes IS 'Structure hiérarchique organisationnelle avec relations parent-enfant';
COMMENT ON COLUMN organizational_nodes.employer_id IS 'Référence vers l''employeur propriétaire de cette structure';
COMMENT ON COLUMN organizational_nodes.parent_id IS 'Référence vers le nœud parent (NULL pour les établissements)';
COMMENT ON COLUMN organizational_nodes.level IS 'Niveau hiérarchique: etablissement, departement, service, unite';
COMMENT ON COLUMN organizational_nodes.name IS 'Nom de l''unité organisationnelle';
COMMENT ON COLUMN organizational_nodes.path IS 'Chemin hiérarchique complet calculé automatiquement';
COMMENT ON COLUMN organizational_nodes.sort_order IS 'Ordre d''affichage dans l''interface';
COMMENT ON COLUMN organizational_nodes.is_active IS 'Indique si l''unité est active';

COMMENT ON VIEW organizational_tree IS 'Vue récursive pour naviguer dans l''arbre hiérarchique';
