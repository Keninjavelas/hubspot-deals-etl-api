import os
import requests
import time
import logging
import psycopg2
from psycopg2 import extras

# --- Configuration ---
# Set up a clear logging format for better debugging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration from environment variables
HUBSPOT_ACCESS_TOKEN = os.getenv("HUBSPOT_ACCESS_TOKEN")
HUBSPOT_API_BASE_URL = os.getenv("HUBSPOT_API_BASE_URL", "https://api.hubapi.com")
DB_CONN_STR = (
    f"host={os.getenv('DB_HOST')} "
    f"dbname={os.getenv('DB_NAME')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PASSWORD')}"
)

# --- HubSpot API Logic ---
def get_all_hubspot_deals():
    """Fetches all deals from the HubSpot API, handling pagination and errors."""
    if not HUBSPOT_ACCESS_TOKEN:
        logging.error("FATAL: HUBSPOT_ACCESS_TOKEN is not set. Aborting extraction.")
        return []

    deals = []
    after = None
    headers = {"Authorization": f"Bearer {HUBSPOT_ACCESS_TOKEN}"}
    
    # This is the corrected list of properties to request from the HubSpot API
    properties_to_request = "dealname,amount,pipeline,dealstage,createdate,hs_lastmodifieddate,closedate"
    endpoint = f"{HUBSPOT_API_BASE_URL}/crm/v3/objects/deals"

    while True:
        try:
            # Build the request parameters for this page
            params = {"properties": properties_to_request, "limit": 100}
            if after:
                params["after"] = after
            
            logging.info(f"Fetching deals page from HubSpot...")
            response = requests.get(endpoint, headers=headers, params=params, timeout=15)
            response.raise_for_status() # Raise an exception for HTTP errors

            data = response.json()
            deals.extend(data.get("results", []))
            
            # Check for the next page of results
            paging = data.get("paging")
            if paging and paging.get("next"):
                after = paging["next"]["after"]
            else:
                logging.info("No more pages to fetch from HubSpot.")
                break
        except requests.exceptions.RequestException as e:
            logging.error(f"An API error occurred while fetching from HubSpot: {e}")
            break # Stop trying if there's an error
            
    logging.info(f"Successfully fetched a total of {len(deals)} deals from HubSpot.")
    return deals

# --- Database Logic ---
def load_data_to_postgres(deals):
    """Connects to PostgreSQL and loads a list of deals, updating on conflict."""
    if not deals:
        logging.info("No deals were fetched, so nothing will be loaded into the database.")
        return

    conn = None
    try:
        logging.info("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(DB_CONN_STR)
        with conn.cursor() as cur:
            insert_query = """
                INSERT INTO deals (id, dealname, amount, pipeline, dealstage, createdate, hs_lastmodifieddate, closedate, properties)
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                    dealname = EXCLUDED.dealname,
                    amount = EXCLUDED.amount,
                    pipeline = EXCLUDED.pipeline,
                    dealstage = EXCLUDED.dealstage,
                    hs_lastmodifieddate = EXCLUDED.hs_lastmodifieddate,
                    closedate = EXCLUDED.closedate,
                    properties = EXCLUDED.properties;
            """
            
            records_to_insert = []
            for deal in deals:
                props = deal.get("properties", {})
                try: # Safely convert amount to float
                    amount = float(props.get("amount")) if props.get("amount") is not None else None
                except (ValueError, TypeError):
                    amount = None

                records_to_insert.append((
                    deal.get("id"), props.get("dealname"), amount, props.get("pipeline"),
                    props.get("dealstage"), props.get("createdate"), props.get("hs_lastmodifieddate"),
                    props.get("closedate"), extras.Json(props)
                ))
            
            if records_to_insert:
                extras.execute_values(cur, insert_query, records_to_insert)
                conn.commit()
                logging.info(f"Successfully inserted or updated {len(records_to_insert)} records in the database.")
            
    except psycopg2.Error as e:
        logging.error(f"A database error occurred: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

# --- Main Execution Block ---
if __name__ == "__main__":
    logging.info("Starting HubSpot Deals extraction service run.")
    
    wait_time = 10 # A brief delay to ensure the database is fully ready
    logging.info(f"Waiting for {wait_time} seconds...")
    time.sleep(wait_time)
    
    all_deals = get_all_hubspot_deals()
    load_data_to_postgres(all_deals)
    
    logging.info("Extraction service has finished its run.")




