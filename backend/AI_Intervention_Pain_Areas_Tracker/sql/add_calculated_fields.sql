-- =============================================================================
-- Calculated fields for ai_intervention_pain_areas_tracker (Supabase / PostgreSQL)
--
-- Adds four read-only (calculated) columns as Postgres GENERATED ALWAYS AS
-- (STORED) columns. They are recomputed automatically by the database on every
-- INSERT/UPDATE and can never be written directly by the app.
--
-- Existing values are derived from the editable source columns:
--
--   priority_score    High=3, Medium=2, Low=1            (from priority)
--   feasibility_score High=3, Medium=2, Low=1            (from feasibility)
--   impact_score      3 if time_spent_hrs >= 40,
--                     2 if time_spent_hrs >= 10,
--                     1 otherwise                        (from time_spent_hrs)
--   quadrant          2x2 impact x feasibility matrix:
--                     impact >= 2 & feasibility >= 2 -> 'Quick Win'
--                     impact >= 2                     -> 'Strategic'
--                     feasibility >= 2                -> 'Fill In'
--                     otherwise                       -> 'Revisit'
--
-- The score logic lives in two IMMUTABLE helper functions because Postgres
-- does not allow a generated column to reference another generated column.
--
-- This script is idempotent: it drops any pre-existing plain versions of the
-- columns first. Dropping is safe because the values are fully computed.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1) Score helpers (must exist before the generated columns are declared)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION pain_area_impact_score(time_spent_hrs double precision)
RETURNS integer
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT CASE
        WHEN time_spent_hrs IS NULL THEN 1
        WHEN time_spent_hrs >= 40 THEN 3
        WHEN time_spent_hrs >= 10 THEN 2
        ELSE 1
    END
$$;

CREATE OR REPLACE FUNCTION pain_area_level_score(level text)
RETURNS integer
LANGUAGE sql
IMMUTABLE
PARALLEL SAFE
AS $$
    SELECT CASE level
        WHEN 'High' THEN 3
        WHEN 'Medium' THEN 2
        ELSE 1
    END
$$;

-- -----------------------------------------------------------------------------
-- 2) Calculated columns
-- -----------------------------------------------------------------------------
ALTER TABLE ai_intervention_pain_areas_tracker
    DROP COLUMN IF EXISTS impact_score,
    DROP COLUMN IF EXISTS feasibility_score,
    DROP COLUMN IF EXISTS priority_score,
    DROP COLUMN IF EXISTS quadrant;

ALTER TABLE ai_intervention_pain_areas_tracker
    ADD COLUMN impact_score INTEGER
        GENERATED ALWAYS AS (pain_area_impact_score(time_spent_hrs)) STORED;

ALTER TABLE ai_intervention_pain_areas_tracker
    ADD COLUMN feasibility_score INTEGER
        GENERATED ALWAYS AS (pain_area_level_score(feasibility)) STORED;

ALTER TABLE ai_intervention_pain_areas_tracker
    ADD COLUMN priority_score INTEGER
        GENERATED ALWAYS AS (pain_area_level_score(priority)) STORED;

ALTER TABLE ai_intervention_pain_areas_tracker
    ADD COLUMN quadrant VARCHAR(30)
        GENERATED ALWAYS AS (
            CASE
                WHEN pain_area_impact_score(time_spent_hrs) >= 2
                 AND pain_area_level_score(feasibility) >= 2 THEN 'Quick Win'
                WHEN pain_area_impact_score(time_spent_hrs) >= 2 THEN 'Strategic'
                WHEN pain_area_level_score(feasibility) >= 2 THEN 'Fill In'
                ELSE 'Revisit'
            END
        ) STORED;
