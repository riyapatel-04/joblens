WITH source AS (
    SELECT * FROM {{ source('raw', 'raw_jobs') }}
),
cleaned AS (
    SELECT
        ID                             AS job_id,
        TRIM(TITLE)                    AS job_title,
        TRIM(COMPANY)                  AS company_name,
        TRIM(LOCATION)                 AS location,
        SALARY_MIN                     AS salary_min,
        SALARY_MAX                     AS salary_max,
        (SALARY_MIN + SALARY_MAX) / 2  AS salary_avg,
        TRIM(DESCRIPTION)              AS description,
        TRIM(CATEGORY)                 AS category,
        TRIM(CONTRACT_TYPE)            AS contract_type,
        TRIM(SEARCH_ROLE)              AS search_role,
        TRIM(SEARCH_LOCATION)          AS search_location,
        INGESTED_AT                    AS ingested_at
    FROM source
    WHERE TITLE IS NOT NULL
    AND ID IS NOT NULL
)
SELECT * FROM cleaned