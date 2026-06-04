WITH jobs AS (
    SELECT * FROM {{ ref('stg_jobs') }}
),
skill_counts AS (
    SELECT
        search_role,
        search_location,
        CASE
            WHEN LOWER(description) LIKE '%python%' THEN 'Python'
            WHEN LOWER(description) LIKE '%sql%' THEN 'SQL'
            WHEN LOWER(description) LIKE '%snowflake%' THEN 'Snowflake'
            WHEN LOWER(description) LIKE '%dbt%' THEN 'dbt'
            WHEN LOWER(description) LIKE '%spark%' THEN 'Spark'
            WHEN LOWER(description) LIKE '%airflow%' THEN 'Airflow'
            WHEN LOWER(description) LIKE '%azure%' THEN 'Azure'
            WHEN LOWER(description) LIKE '%aws%' THEN 'AWS'
            WHEN LOWER(description) LIKE '%tableau%' THEN 'Tableau'
            WHEN LOWER(description) LIKE '%power bi%' THEN 'Power BI'
            WHEN LOWER(description) LIKE '%databricks%' THEN 'Databricks'
            WHEN LOWER(description) LIKE '%kafka%' THEN 'Kafka'
            ELSE 'Other'
        END AS skill,
        COUNT(*) AS job_count,
        AVG(salary_avg) AS avg_salary
    FROM jobs
    WHERE description IS NOT NULL
    GROUP BY 1, 2, 3
)
SELECT * FROM skill_counts
WHERE skill != 'Other'
ORDER BY job_count DESC