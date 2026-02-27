# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {}
# META   }
# META }

# MARKDOWN ********************

# # Kolada Data Fetcher for Microsoft Fabric
# 
# This notebook fetches data from the [Kolada API](https://www.kolada.se/) and stores it in a Delta Lake table in your Fabric Lakehouse.
# 
# ## Overview
# The Kolada database contains Swedish municipal and regional key performance indicators (KPIs).
# 
# ### Features:
# - **Batch requests**: Optimized to fetch multiple municipalities/years in a single API call
# - **Rate limiting**: Respects API limits to avoid being throttled
# - **Delta Lake storage**: Data is stored in Delta format for efficient querying
# - **Incremental loading**: Supports appending new data or replacing existing data
# 
# ### API Limits:
# - The Kolada API has limits on request frequency and response size
# - This notebook uses batch requests to minimize the number of API calls
# - A small delay is added between requests to be respectful to the API

# CELL ********************

# Configuration parameters
# Modify these settings based on your needs

# Lakehouse table names for output (Power BI star schema naming)
VALUES_TABLE_NAME = "fKoladaData"
KPI_DETAILS_TABLE_NAME = "dKpi"

# API settings
KOLADA_BASE_URL = "http://api.kolada.se/v2"
REQUEST_DELAY_SECONDS = 0.5  # Delay between API requests to respect rate limits
BATCH_SIZE_MUNICIPALITIES = 50  # Number of municipalities per batch request
BATCH_SIZE_YEARS = 10  # Number of years per batch request
BATCH_SIZE_KPIS = 100  # Number of KPIs per batch request for details

# Write mode: "overwrite" to replace data, "append" to add to existing
WRITE_MODE = "overwrite"

# MARKDOWN ********************

# ## Setup and Imports
# Import required libraries for data fetching and processing.

# CELL ********************

import requests
import time
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, BooleanType
from pyspark.sql.functions import col, explode, lit, current_timestamp
from itertools import product
from typing import List, Dict, Any, Optional

# Initialize Spark session (already available in Fabric)
spark = SparkSession.builder.getOrCreate()

print("✓ Libraries imported successfully")
print(f"✓ Spark version: {spark.version}")

# MARKDOWN ********************

# ## Helper Functions
# 
# These functions handle API requests, batching, and data transformation.

# CELL ********************

def fetch_with_retry(url: str, max_retries: int = 3, delay: float = REQUEST_DELAY_SECONDS) -> Optional[Dict]:
    """
    Fetch data from URL with retry logic and rate limiting.
    
    Args:
        url: The API endpoint URL
        max_retries: Number of retry attempts on failure
        delay: Delay between requests in seconds
    
    Returns:
        JSON response as dictionary, or None if all retries fail
    """
    for attempt in range(max_retries):
        try:
            time.sleep(delay)  # Rate limiting
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(delay * (attempt + 1))  # Exponential backoff
    return None


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def build_batch_url(municipality_ids: List[str], years: List[str]) -> str:
    """
    Build a batch URL for fetching values for multiple municipalities and years.
    
    The Kolada API supports comma-separated IDs and years for efficient batch requests.
    Example: /v2/data/municipality/0114,0115/year/2020,2021
    """
    municipalities_str = ",".join(municipality_ids)
    years_str = ",".join(years)
    return f"{KOLADA_BASE_URL}/data/municipality/{municipalities_str}/year/{years_str}"


def build_kpi_batch_url(kpi_ids: List[str]) -> str:
    """
    Build a batch URL for fetching KPI details.
    
    Example: /v2/kpi?id=N00002,N00003
    """
    kpis_str = ",".join(kpi_ids)
    return f"{KOLADA_BASE_URL}/kpi?id={kpis_str}"

print("✓ Helper functions defined")

# MARKDOWN ********************

# ## Data Input Configuration
# 
# Define the municipalities and years you want to fetch data for.
# You can either:
# 1. Manually specify the lists below, or
# 2. Read from a CSV file in your Lakehouse

# CELL ********************

# Option 1: Manual input - define your municipalities and years directly
# Uncomment and modify these lists as needed

# Municipality IDs to fetch (use 4-digit municipal codes)
# Example Swedish municipality codes: "0114" (Upplands Väsby), "0115" (Vallentuna), etc.
MUNICIPALITY_IDS = [
    "0114", "0115", "0117", "0120", "0123", "0125", "0126", "0127", "0128", "0136",
    "0138", "0139", "0140", "0160", "0162", "0163", "0180", "0181", "0182", "0183"
]

# Years to fetch data for
YEARS = ["2019", "2020", "2021", "2022", "2023"]

# KPI IDs for fetching KPI details
# Example KPI IDs from Kolada
KPI_IDS = [
    "N00002", "N00003", "N00004", "N00005", "N00006", 
    "N00007", "N00008", "N00009", "N00010", "N00011"
]

print(f"✓ Configured to fetch data for {len(MUNICIPALITY_IDS)} municipalities")
print(f"✓ Configured to fetch data for {len(YEARS)} years")
print(f"✓ Configured to fetch details for {len(KPI_IDS)} KPIs")

# CELL ********************

# Option 2: Read from CSV files in Lakehouse (uncomment if using CSV input)
# Make sure your CSV files are uploaded to the Lakehouse Files section

# def load_input_from_csv():
#     """Load municipality IDs, years, and KPI IDs from CSV files in Lakehouse."""
#     global MUNICIPALITY_IDS, YEARS, KPI_IDS
#     
#     # Read municipality/year combinations from input.csv
#     # Expected columns: ID, YEAR
#     try:
#         input_df = spark.read.option("header", "true").csv("Files/input.csv")
#         MUNICIPALITY_IDS = list(set([row.ID for row in input_df.select("ID").collect()]))
#         YEARS = list(set([row.YEAR for row in input_df.select("YEAR").collect()]))
#         print(f"✓ Loaded {len(MUNICIPALITY_IDS)} municipalities and {len(YEARS)} years from input.csv")
#     except Exception as e:
#         print(f"⚠ Could not load input.csv: {e}")
#     
#     # Read KPI IDs from KPI_Input.csv
#     # Expected column: ID
#     try:
#         kpi_input_df = spark.read.option("header", "true").csv("Files/KPI_Input.csv")
#         KPI_IDS = [row.ID for row in kpi_input_df.select("ID").collect()]
#         print(f"✓ Loaded {len(KPI_IDS)} KPI IDs from KPI_Input.csv")
#     except Exception as e:
#         print(f"⚠ Could not load KPI_Input.csv: {e}")
# 
# # Uncomment the line below to load from CSV files
# # load_input_from_csv()

# MARKDOWN ********************

# ## Fetch Municipality Values
# 
# This section fetches KPI values for the configured municipalities and years.
# The data is fetched in batches to optimize API calls.

# CELL ********************

def fetch_municipality_values(municipality_ids: List[str], years: List[str]) -> List[Dict]:
    """
    Fetch KPI values for given municipalities and years using batch requests.
    
    Returns a list of flattened records ready for DataFrame creation.
    """
    all_records = []
    
    # Chunk municipalities and years for batch processing
    municipality_chunks = chunk_list(municipality_ids, BATCH_SIZE_MUNICIPALITIES)
    year_chunks = chunk_list(years, BATCH_SIZE_YEARS)
    
    total_batches = len(municipality_chunks) * len(year_chunks)
    current_batch = 0
    
    print(f"Fetching data in {total_batches} batch(es)...")
    
    for muni_chunk in municipality_chunks:
        for year_chunk in year_chunks:
            current_batch += 1
            url = build_batch_url(muni_chunk, year_chunk)
            print(f"  Batch {current_batch}/{total_batches}: {len(muni_chunk)} municipalities × {len(year_chunk)} years")
            
            data = fetch_with_retry(url)
            
            if data and "values" in data:
                # Flatten the nested structure
                for value_entry in data["values"]:
                    kpi_id = value_entry.get("kpi")
                    period = value_entry.get("period")
                    
                    for value_item in value_entry.get("values", []):
                        record = {
                            "kpi_id": kpi_id,
                            "period": period,
                            "municipality_id": value_item.get("municipality"),
                            "value": value_item.get("value"),
                            "gender": value_item.get("gender"),
                            "status": value_item.get("status")
                        }
                        all_records.append(record)
                
                print(f"    ✓ Retrieved {len(data['values'])} KPI entries")
            else:
                print(f"    ⚠ No data returned for this batch")
    
    return all_records

# Fetch the data
print("=" * 50)
print("FETCHING MUNICIPALITY VALUES")
print("=" * 50)
values_records = fetch_municipality_values(MUNICIPALITY_IDS, YEARS)
print(f"\n✓ Total records fetched: {len(values_records)}")

# CELL ********************

# Convert to Spark DataFrame and save to Delta table
if values_records:
    # Define schema for values
    values_schema = StructType([
        StructField("kpi_id", StringType(), True),
        StructField("period", IntegerType(), True),
        StructField("municipality_id", StringType(), True),
        StructField("value", DoubleType(), True),
        StructField("gender", StringType(), True),
        StructField("status", StringType(), True)
    ])
    
    # Create DataFrame
    values_df = spark.createDataFrame(values_records, schema=values_schema)
    
    # Add metadata columns
    values_df = values_df.withColumn("loaded_at", current_timestamp())
    
    # Show sample data
    print("Sample of fetched data:")
    values_df.show(10, truncate=False)
    
    # Save to Delta table
    values_df.write.format("delta").mode(WRITE_MODE).saveAsTable(VALUES_TABLE_NAME)
    print(f"\n✓ Data saved to Delta table: {VALUES_TABLE_NAME}")
    print(f"  Total rows: {values_df.count()}")
else:
    print("⚠ No values data to save")

# MARKDOWN ********************

# ## Fetch KPI Details
# 
# This section fetches metadata/details for the configured KPIs.
# Details include KPI descriptions, measurement units, and other metadata.

# CELL ********************

def fetch_kpi_details(kpi_ids: List[str]) -> List[Dict]:
    """
    Fetch KPI details using batch requests.
    
    Returns a list of KPI detail records.
    """
    all_details = []
    
    # Chunk KPIs for batch processing
    kpi_chunks = chunk_list(kpi_ids, BATCH_SIZE_KPIS)
    total_batches = len(kpi_chunks)
    
    print(f"Fetching KPI details in {total_batches} batch(es)...")
    
    for batch_num, kpi_chunk in enumerate(kpi_chunks, 1):
        url = build_kpi_batch_url(kpi_chunk)
        print(f"  Batch {batch_num}/{total_batches}: {len(kpi_chunk)} KPIs")
        
        data = fetch_with_retry(url)
        
        if data and "values" in data:
            for kpi in data["values"]:
                detail = {
                    "kpi_id": kpi.get("id"),
                    "title": kpi.get("title"),
                    "description": kpi.get("description"),
                    "definition": kpi.get("definition"),
                    "operating_area": kpi.get("operating_area"),
                    "ou_publication_date": kpi.get("ou_publication_date"),
                    "publication_date": kpi.get("publication_date"),
                    "municipality_type": kpi.get("municipality_type"),
                    "perspective": kpi.get("perspective"),
                    "prel_publication_date": kpi.get("prel_publication_date"),
                    "is_divided_by_gender": bool(kpi.get("is_divided_by_gender", False)),
                    "has_ou_data": bool(kpi.get("has_ou_data", False))
                }
                all_details.append(detail)
            
            print(f"    ✓ Retrieved {len(data['values'])} KPI details")
        else:
            print(f"    ⚠ No data returned for this batch")
    
    return all_details

# Fetch KPI details
print("=" * 50)
print("FETCHING KPI DETAILS")
print("=" * 50)
kpi_details_records = fetch_kpi_details(KPI_IDS)
print(f"\n✓ Total KPI details fetched: {len(kpi_details_records)}")

# CELL ********************

# Convert to Spark DataFrame and save to Delta table
if kpi_details_records:
    # Define schema for KPI details
    details_schema = StructType([
        StructField("kpi_id", StringType(), True),
        StructField("title", StringType(), True),
        StructField("description", StringType(), True),
        StructField("definition", StringType(), True),
        StructField("operating_area", StringType(), True),
        StructField("ou_publication_date", StringType(), True),
        StructField("publication_date", StringType(), True),
        StructField("municipality_type", StringType(), True),
        StructField("perspective", StringType(), True),
        StructField("prel_publication_date", StringType(), True),
        StructField("is_divided_by_gender", BooleanType(), True),
        StructField("has_ou_data", BooleanType(), True)
    ])
    
    # Create DataFrame
    details_df = spark.createDataFrame(kpi_details_records, schema=details_schema)
    
    # Add metadata columns
    details_df = details_df.withColumn("loaded_at", current_timestamp())
    
    # Show sample data
    print("Sample of KPI details:")
    details_df.show(5, truncate=50)
    
    # Save to Delta table
    details_df.write.format("delta").mode(WRITE_MODE).saveAsTable(KPI_DETAILS_TABLE_NAME)
    print(f"\n✓ Data saved to Delta table: {KPI_DETAILS_TABLE_NAME}")
    print(f"  Total rows: {details_df.count()}")
else:
    print("⚠ No KPI details data to save")

# MARKDOWN ********************

# ## Summary and Next Steps
# 
# ### Data Loaded
# The following Delta tables have been created/updated in your Lakehouse:
# - **kolada_values**: Contains KPI values for municipalities by year
# - **kolada_kpi_details**: Contains metadata about KPIs
# 
# ### Querying the Data
# You can query these tables using SQL or Spark:
# 
# ```sql
# -- Example: Get average values per KPI
# SELECT kpi_id, AVG(value) as avg_value
# FROM kolada_values
# GROUP BY kpi_id
# ```
# 
# ```python
# # Example: Read the values table
# df = spark.read.table("kolada_values")
# df.show()
# ```
# 
# ### Tips for Large Data Volumes
# 1. Adjust `BATCH_SIZE_*` parameters if you encounter API limits
# 2. Use `WRITE_MODE = "append"` for incremental loads
# 3. Consider filtering data by specific KPIs of interest
# 
# ### API Documentation
# For more information about the Kolada API, visit: https://www.kolada.se/applikation/dokumentation

# CELL ********************

# Final summary
print("=" * 50)
print("DATA LOADING COMPLETE")
print("=" * 50)
print(f"\n📊 Tables created/updated:")
print(f"   • {VALUES_TABLE_NAME}")
print(f"   • {KPI_DETAILS_TABLE_NAME}")
print(f"\n💡 Use spark.read.table('table_name') to query the data")
print(f"\n✅ Notebook execution finished successfully!")
