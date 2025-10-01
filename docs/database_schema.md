# Database Schema for HubSpot Deals ETL

This document outlines the PostgreSQL database schema for the `hubspot_deals_etl` service. The schema is designed to store deal data extracted from the HubSpot CRM API.

## Table: `deals`

The primary table to store HubSpot deal records.

| Column Name            | Data Type          | Description                                           |
|------------------------|--------------------|-------------------------------------------------------|
| `id`                   | BIGINT             | **Primary Key**. HubSpot's unique deal ID.            |
| `dealname`             | VARCHAR(255)       | The name of the deal.                                 |
| `amount`               | NUMERIC(15, 2)     | The monetary value of the deal.                       |
| `pipeline`             | VARCHAR(100)       | The sales pipeline the deal belongs to.               |
| `dealstage`            | VARCHAR(100)       | The current stage of the deal in the pipeline.        |
| `createdate`           | TIMESTAMP WITH TIME ZONE | The timestamp when the deal was created in HubSpot. |
| `hs_lastmodifieddate`  | TIMESTAMP WITH TIME ZONE | The timestamp of the last modification.            |
| `closedate`            | TIMESTAMP WITH TIME ZONE | The date the deal was closed.                     |
| `deal_owner_id`        | BIGINT             | The ID of the HubSpot user who owns the deal.         |
| `properties`           | JSONB              | Stores all other dynamic or custom deal properties.   |

### Indexes

* **Primary Key Index:** `deals_pkey` on `id`.
* **Timestamp Index:** `idx_deals_last_modified` on `hs_lastmodifieddate` to optimize queries for incremental updates and change data capture.
* **Owner Index:** `idx_deals_owner` on `deal_owner_id` for efficient filtering by deal owner.

## Table: `pipelines` (Optional, for lookup)

A potential lookup table to store pipeline and stage information if needed for reporting or validation.

| Column Name    | Data Type     | Description                           |
|----------------|---------------|---------------------------------------|
| `id`           | VARCHAR(100)  | Unique pipeline ID.                   |
| `label`        | VARCHAR(255)  | Human-readable name of the pipeline.  |
| `stages`       | JSONB         | Array of stages within the pipeline.  |
