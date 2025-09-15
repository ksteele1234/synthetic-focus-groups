# Exports (v1)

All exports include `schema_version` and are reproducible (checksums). Weighted and unweighted metrics are both provided.

## CSV files
### messages.csv
`study_id,turn,persona_name,role,content,tokens,cost,topics,sentiment,ts`

### personas.csv
`persona_id,study_id,persona_name,weight,traits_json,created_at`

### insights_aggregate.csv
`study_id,theme_id,theme,score_weighted,score_unweighted,agreement_weighted,agreement_unweighted,sentiment_weighted,sentiment_unweighted`

### insights_by_persona.csv
`study_id,persona_id,persona_name,theme_id,theme,theme_score,sentiment,top_quotes_json`

### guardrails.csv
`study_id,event_id,type,severity,detail,ts`

## YAML files
### study.yaml (excerpt)
```yaml
schema_version: v1
study:
    id: "st_123"
    title: "Onboarding Messaging"
    objective: "Validate friction points"
    constraints: { cost_cap_usd: 5.00, turns: 8 }
    weighting: { enabled: true, normalization: none }
personas:
    - id: "pe_1"
        name: "Ops Manager – Mid-Market"
        weight: 2.0
messages:
    - turn: 1
        persona_name: "Ops Manager – Mid-Market"
        role: "participant"
        content: "…"
insights:
    aggregate:
        themes:
            - id: "th_1"
                label: "Onboarding Confusion"
                score_weighted: 0.72
                score_unweighted: 0.61
                agreement_weighted: 0.68
                sentiment_weighted: -0.33
    by_persona:
        - persona_id: "pe_1"
            themes:
                - id: "th_1"
                    theme_score: 0.83
                    sentiment: -0.4
                    quotes: ["I wasn't sure which plan…"]
limitations: "Synthetic panel; directional only."
```