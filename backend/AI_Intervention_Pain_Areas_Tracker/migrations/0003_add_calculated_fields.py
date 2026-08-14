from django.db import migrations

# Mirrors AI_Intervention_Pain_Areas_Tracker/sql/add_calculated_fields.sql.
# Applied only against PostgreSQL (Supabase); the columns are GENERATED
# ALWAYS AS ... STORED so they are computed by the database and never writable.
SQL_APPLY = r"""
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
"""

SQL_REVERSE = r"""
ALTER TABLE ai_intervention_pain_areas_tracker
    DROP COLUMN IF EXISTS impact_score,
    DROP COLUMN IF EXISTS feasibility_score,
    DROP COLUMN IF EXISTS priority_score,
    DROP COLUMN IF EXISTS quadrant;

DROP FUNCTION IF EXISTS pain_area_impact_score(double precision);
DROP FUNCTION IF EXISTS pain_area_level_score(text);
"""


def apply_calculated_fields(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT to_regclass('public.ai_intervention_pain_areas_tracker')"
        )
        if cursor.fetchone()[0] is None:
            return
        cursor.execute(SQL_APPLY)


def drop_calculated_fields(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT to_regclass('public.ai_intervention_pain_areas_tracker')"
        )
        if cursor.fetchone()[0] is None:
            return
        cursor.execute(SQL_REVERSE)


class Migration(migrations.Migration):

    dependencies = [
        ("AI_Intervention_Pain_Areas_Tracker", "0002_pain_area_csv_import"),
    ]

    operations = [
        migrations.RunPython(apply_calculated_fields, drop_calculated_fields),
    ]
