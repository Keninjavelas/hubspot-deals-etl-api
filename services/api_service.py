import os
import psycopg2
from psycopg2 import extras
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List
import logging

# Set up logging for this module
logging.basicConfig(level=logging.INFO)

# FastAPI application instance
app = FastAPI()

# --- API Endpoints Start Here ---

@app.get("/deals", response_model=List[Dict[str, Any]])
def get_all_deals():
    """Retrieves all deals from the database."""
    conn = None
    try:
        # Connect to the database
        db_conn_str = f"host={os.getenv('DB_HOST')} dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')}"
        conn = psycopg2.connect(db_conn_str)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Select all deals
        cur.execute("SELECT * FROM deals;")
        deals = cur.fetchall()
        
        return deals
    except (Exception, psycopg2.Error) as error:
        logging.error(f"Database error: {error}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if conn:
            cur.close()
            conn.close()

@app.get("/deals/{deal_id}", response_model=Dict[str, Any])
def get_deal_by_id(deal_id: int):
    """Retrieves a single deal from the database by its ID."""
    conn = None
    try:
        db_conn_str = f"host={os.getenv('DB_HOST')} dbname={os.getenv('DB_NAME')} user={os.getenv('DB_USER')} password={os.getenv('DB_PASSWORD')}"
        conn = psycopg2.connect(db_conn_str)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
        # Select a specific deal
        cur.execute("SELECT * FROM deals WHERE id = %s;", (deal_id,))
        deal = cur.fetchone()
        
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        return deal
    except (Exception, psycopg2.Error) as error:
        logging.error(f"Database error: {error}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if conn:
            cur.close()
            conn.close()