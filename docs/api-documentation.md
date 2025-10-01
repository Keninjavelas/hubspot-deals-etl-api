# Deals Extraction Service API

## GET /deals
- List deals for the authorized account. Supports pagination.

## GET /health
- Healthcheck endpoint.

## POST /extract
- Triggers HubSpot deals extraction with supplied token.

### Response Codes
- 200 – Success
- 400 – Bad Request
- 401 – Unauthorized
- 500 – Server Error

### Request/Response Schema

{ "deal_id": "string", "stage": "string", "amount": 123.45 }
undefined