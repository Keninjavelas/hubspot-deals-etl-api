# ==============================================================================
# main.py - FastAPI Application for HubSpot Deals ETL
# ==============================================================================

# --- Section 1: Standard Library Imports ---
import os
import time
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime  # <-- Import the datetime object

# --- Section 2: Third-Party Imports ---
import psycopg2
from psycopg2 import extras
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict

# ==============================================================================
# Section 3: Pydantic Models for Data Validation & Response Shaping
# ==============================================================================

class DealBase(BaseModel):
    """Defines the core fields and data types for a deal."""
    # THIS IS THE FIX: Changed from str to int to match the database
    id: int
    dealname: Optional[str] = None
    amount: Optional[float] = None
    pipeline: Optional[str] = None
    dealstage: Optional[str] = None
    # THIS IS THE FIX: Changed from str to datetime to match the database
    createdate: Optional[datetime] = None
    hs_lastmodifieddate: Optional[datetime] = None
    closedate: Optional[datetime] = None
    deal_owner_id: Optional[str] = None # Assuming this can be a string or null
    properties: Dict[str, Any]

class DealCreate(BaseModel):
    """Defines the fields required from the user to create a new deal."""
    dealname: str
    amount: float
    pipeline: str
    dealstage: str

class Deal(DealBase):
    """The full deal model used for API responses."""
    model_config = ConfigDict(from_attributes=True)

# ==============================================================================
# Section 4: FastAPI Application Setup
# ==============================================================================

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI(
    title="HubSpot Deals API",
    description="An API to manage and view HubSpot deals stored in a PostgreSQL database.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================================================================
# Section 5: Database Connection Logic
# ==============================================================================

def get_db_connection():
    """Establishes and returns a database connection using environment variables."""
    try:
        db_conn_str = (
            f"host={os.getenv('DB_HOST')} "
            f"dbname={os.getenv('DB_NAME')} "
            f"user={os.getenv('DB_USER')} "
            f"password={os.getenv('DB_PASSWORD')}"
        )
        conn = psycopg2.connect(db_conn_str)
        return conn
    except psycopg2.OperationalError as e:
        logging.error(f"FATAL: Could not connect to the database: {e}")
        raise HTTPException(status_code=503, detail="Database connection is currently unavailable.")

# ==============================================================================
# Section 6: API Endpoints
# ==============================================================================

@app.post("/deals", response_model=Deal, status_code=201, tags=["Deals"])
def create_deal(deal: DealCreate):
    """Creates a new deal record in the database from user-provided data."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            # Use integer for the new ID
            new_id = int(time.time() * 1000)
            now_iso_str = datetime.utcnow().isoformat()

            properties_json = deal.model_dump()
            properties_json.update({
                'hs_object_id': str(new_id), # Keep as string in the JSON blob
                'createdate': now_iso_str,
                'hs_lastmodifieddate': now_iso_str
            })

            insert_query = """
                INSERT INTO deals (id, dealname, amount, pipeline, dealstage, createdate, hs_lastmodifieddate, properties)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
            """
            cur.execute(insert_query, (
                new_id, deal.dealname, deal.amount, deal.pipeline, deal.dealstage,
                datetime.utcnow(), datetime.utcnow(), extras.Json(properties_json)
            ))
            
            new_deal_row = cur.fetchone()
            conn.commit()
            
            logging.info(f"Successfully created deal with ID: {new_id}")
            return dict(new_deal_row)
    except (Exception, psycopg2.Error) as error:
        logging.error(f"Database error during deal creation: {error}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while creating the deal.")
    finally:
        if conn:
            conn.close()

@app.get("/deals", response_model=List[Deal], tags=["Deals"])
def get_all_deals():
    """Retrieves all deal records from the database, ordered by creation date."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute("SELECT * FROM deals ORDER BY createdate DESC;")
            deals_rows = cur.fetchall()
            deals = [dict(row) for row in deals_rows]
            return deals
    except (Exception, psycopg2.Error) as error:
        logging.error(f"Database error while fetching all deals: {error}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching deals.")
    finally:
        if conn:
            conn.close()

# ==============================================================================
# Section 7: Static File Serving for Frontend
# ==============================================================================

static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount(f"/{static_dir}", StaticFiles(directory=static_dir), name="static")

@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serves the main index.html file when a user navigates to the root URL ("/")."""
    return FileResponse(os.path.join(static_dir, 'index.html'))

