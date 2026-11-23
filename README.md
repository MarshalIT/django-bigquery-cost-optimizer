# Django + GCP BigQuery Cost & Query Optimization Demo

A production-ready reference showing how to cut Google Cloud BigQuery scan costs by **~95%** using date partitioning, clustering, and batch ingestion from a Django backend.

## Architecture & Highlights
- **Storage Optimization:** Migrated raw flat tables to `PARTITION BY DATE(event_timestamp)` + `CLUSTER BY customer_id, event_type`.
- **SQL Refactoring:** Replaced `SELECT *` and full-table cross joins with partition-pruned CTEs and pre-aggregated materialized views.
- **Reliable Django Ingestion:** Custom Django management command (`sync_events_to_bq`) using BigQuery batch load jobs (zero streaming insert fees) with idempotent watermarking.

## Benchmark Comparison (100M Row Event Table)

| Metric | Before (Raw Table) | After (Partitioned + Clustered) | Improvement |
| :--- | :--- | :--- | :--- |
| **Bytes Scanned** | 48.2 GB | 1.4 GB | **97% Reduction** |
| **Query Execution Time** | 14.8 sec | 1.9 sec | **7.8x Faster** |
| **Est. Cost per 1,000 Runs** | ~$301.25 | ~$8.75 | **$292.50 Saved** |
