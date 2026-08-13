-- =============================================================================
-- Pain Areas CSV import pipeline (Supabase / PostgreSQL)
--
-- Run this SQL once against the database (or apply the matching Django
-- migration AI_Intervention_Pain_Areas_Tracker/migrations/0002_...).
--
-- Flow: Django validates the uploaded CSV and stages the valid rows into
-- ai_pain_area_csv_staging, then calls process_pain_area_csv_import(batch_id),
-- which transforms the staged rows and inserts the final records into
-- ai_intervention_pain_areas_tracker before purging the batch.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1) Staging table
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_pain_area_csv_staging (
    id               BIGSERIAL PRIMARY KEY,
    batch_id         UUID NOT NULL,
    row_number       INTEGER,
    date             DATE,
    department       TEXT,
    process_activity TEXT,
    pain_area        TEXT,
    current_method   TEXT,
    frequency        TEXT,
    time_spent_hrs   DOUBLE PRECISION,
    impact_area      TEXT,
    ai_intervention  TEXT,
    expected_benefit TEXT,
    priority         TEXT,
    feasibility      TEXT,
    owner            TEXT,
    target_date      DATE,
    status           TEXT,
    remarks          TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ai_pain_area_csv_staging_batch_idx
    ON ai_pain_area_csv_staging (batch_id);

-- -----------------------------------------------------------------------------
-- 2) Transform + insert procedure
-- -----------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION process_pain_area_csv_import(p_batch uuid)
RETURNS TABLE (inserted bigint, skipped bigint, warnings text[])
LANGUAGE plpgsql
AS $$
DECLARE
    v_row      record;
    v_inserted bigint := 0;
    v_skipped  bigint := 0;
    v_warnings text[] := '{}';
BEGIN
    FOR v_row IN
        SELECT * FROM ai_pain_area_csv_staging
        WHERE batch_id = p_batch
        ORDER BY id
    LOOP
        -- Skip fully empty rows.
        IF COALESCE(
            NULLIF(btrim(COALESCE(v_row.process_activity, '')), ''),
            NULLIF(btrim(COALESCE(v_row.pain_area, '')), '')
        ) IS NULL THEN
            v_skipped := v_skipped + 1;
            CONTINUE;
        END IF;

        BEGIN
            INSERT INTO ai_intervention_pain_areas_tracker (
                date, department, process_activity, pain_area, current_method,
                frequency, time_spent_hrs, impact_area, ai_intervention,
                expected_benefit, priority, feasibility, owner, target_date,
                status, remarks, created_at, updated_at
            ) VALUES (
                COALESCE(v_row.date, CURRENT_DATE),
                btrim(COALESCE(v_row.department, '')),
                btrim(COALESCE(v_row.process_activity, '')),
                btrim(COALESCE(v_row.pain_area, '')),
                btrim(COALESCE(v_row.current_method, '')),
                btrim(COALESCE(v_row.frequency, '')),
                v_row.time_spent_hrs,
                btrim(COALESCE(v_row.impact_area, '')),
                btrim(COALESCE(v_row.ai_intervention, '')),
                btrim(COALESCE(v_row.expected_benefit, '')),
                COALESCE(NULLIF(btrim(COALESCE(v_row.priority, '')), ''), 'Medium'),
                COALESCE(NULLIF(btrim(COALESCE(v_row.feasibility, '')), ''), 'Medium'),
                btrim(COALESCE(v_row.owner, '')),
                v_row.target_date,
                COALESCE(NULLIF(btrim(COALESCE(v_row.status, '')), ''), 'Open'),
                btrim(COALESCE(v_row.remarks, '')),
                now(), now()
            );
            v_inserted := v_inserted + 1;
        EXCEPTION WHEN OTHERS THEN
            v_skipped := v_skipped + 1;
            v_warnings := v_warnings || format(
                'row %s: %s', v_row.row_number, SQLERRM
            );
        END;
    END LOOP;

    DELETE FROM ai_pain_area_csv_staging WHERE batch_id = p_batch;

    RETURN QUERY SELECT v_inserted, v_skipped, v_warnings;
END;
$$;
