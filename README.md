# Kolada_Fabric
This repo holds the resources needed to fetch and analyze Kolada data in Power BI and Fabric

## Files

### Kolada_Fabric_Notebook.py
A Microsoft Fabric-compatible Python notebook for fetching data from the [Kolada API](https://www.kolada.se/). This notebook is optimized for use in MS Fabric and stores data in Delta Lake tables.

**Features:**
- **Batch requests**: Fetches multiple municipalities/years in a single API call (instead of one request per row)
- **Rate limiting**: Includes delays and retry logic to respect API limits
- **Delta Lake storage**: Data is stored in Delta format in your Fabric Lakehouse
- **Incremental loading**: Supports both overwrite and append modes

**How to use:**
1. Download `Kolada_Fabric_Notebook.py` from this repository
2. In Microsoft Fabric, go to your workspace
3. Click "Import" → "Notebook" → "From this computer"
4. Select the `.py` file
5. Attach a Lakehouse to the notebook
6. Modify the configuration parameters (municipalities, years, KPIs)
7. Run all cells

### Old_Manual_Scripts
Legacy Python scripts for local execution. These scripts write data to local JSON files and are not optimized for cloud usage.
