# Deployment Guide for Kolada Fabric

This guide provides detailed instructions for deploying the Kolada data ingestion solution to Microsoft Fabric.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Authentication Setup](#authentication-setup)
3. [Deployment Options](#deployment-options)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Running the Notebooks](#running-the-notebooks)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Access

- Microsoft Fabric enabled in your tenant
- Access to create workspaces in Fabric
- Permissions to create Lakehouses and Notebooks
- For automated deployment: Ability to create Azure AD App Registrations

### Software Requirements

- Python 3.8 or higher (for automated deployment)
- Git (to clone this repository)
- Web browser (to access Fabric portal)

## Authentication Setup

### Option A: Service Principal (Recommended for Automation)

1. **Create an Azure AD App Registration**
   
   Navigate to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations

   ```
   - Click "New registration"
   - Name: "Fabric-Kolada-Deployment"
   - Supported account types: Single tenant
   - Click "Register"
   ```

2. **Create a Client Secret**
   
   ```
   - Go to "Certificates & secrets"
   - Click "New client secret"
   - Description: "Fabric Deployment Secret"
   - Expiration: Choose appropriate duration
   - Click "Add"
   - IMPORTANT: Copy the secret value immediately (you won't see it again)
   ```

3. **Note the Application Details**
   
   From the "Overview" page, copy:
   - Application (client) ID
   - Directory (tenant) ID

4. **Grant Fabric API Permissions**
   
   ```
   - Go to "API permissions"
   - Click "Add a permission"
   - Select "Power BI Service"
   - Select "Delegated permissions"
   - Check "Workspace.ReadWrite.All"
   - Click "Add permissions"
   - Click "Grant admin consent"
   ```

5. **Assign to Workspace**
   
   After creating your Fabric workspace:
   ```
   - Open the workspace in Fabric
   - Click workspace settings (gear icon)
   - Go to "Access"
   - Add the service principal as "Admin" or "Member"
   ```

### Option B: User Authentication (For Manual Deployment)

Simply use your own credentials to log into the Fabric portal.

## Deployment Options

### Option 1: Automated Deployment (Using Python Script)

This option uses the deployment script to automatically create and configure all resources.

1. **Clone the Repository**
   
   ```bash
   git clone https://github.com/villezekeviking/Kolada_Fabric.git
   cd Kolada_Fabric
   ```

2. **Install Dependencies**
   
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up Environment Variables**
   
   **On Linux/Mac:**
   ```bash
   # Run the setup script
   ./deployment/setup_env.sh
   
   # Or manually create .env file
   cp .env.example .env
   # Edit .env with your values
   
   # Load environment variables
   source .env
   ```
   
   **On Windows:**
   ```cmd
   # Run the setup script
   deployment\setup_env.bat
   
   # Or manually create .env file
   copy .env.example .env
   # Edit .env with your values
   
   # Set environment variables
   # You can set them manually in cmd or PowerShell
   ```

4. **Run the Deployment Script**
   
   ```bash
   python deployment/deploy_to_fabric.py
   ```
   
   The script will:
   - Create the workspace (if it doesn't exist)
   - Create the Lakehouse
   - Upload all notebooks
   - Display deployment summary

### Option 2: Manual Deployment (Using Fabric Portal)

This option involves manually creating resources and uploading files through the Fabric web interface.

1. **Create a Workspace**
   
   ```
   - Go to https://app.fabric.microsoft.com
   - Click "Workspaces" → "New workspace"
   - Name: "KoladaWorkspace" (or your preferred name)
   - Click "Apply"
   ```

2. **Create a Lakehouse**
   
   ```
   - In your new workspace, click "New" → "Lakehouse"
   - Name: "KoladaLakehouse"
   - Click "Create"
   ```

3. **Upload Notebooks**
   
   ```
   - In the workspace, click "New" → "Import notebook"
   - Select and upload each notebook from the notebooks/ folder:
     * 01_Fetch_KPI_Metadata.ipynb
     * 02_Fetch_Municipality_Metadata.ipynb
     * 03_Fetch_Kolada_Data.ipynb
   ```

4. **Attach Lakehouse to Notebooks**
   
   For each notebook:
   ```
   - Open the notebook
   - Click "Add" in the left panel (Lakehouse section)
   - Select "Existing lakehouse"
   - Choose "KoladaLakehouse"
   - Click "Add"
   ```

## Post-Deployment Configuration

### Configure the Data Ingestion Parameters

Open notebook `03_Fetch_Kolada_Data.ipynb` and customize the parameters:

```python
# Municipality data parameters
KPI_IDS = ["N00945", "N00946"]  # Add your KPI IDs here
MUNICIPALITY_IDS = []  # e.g., ["1860", "0180"] or leave empty for all
YEARS = ["2020", "2021", "2022", "2023"]  # Customize years

# OU data parameters (enabled by default)
OU_KPI_IDS = ["N15033", "N15030"]  # KPIs with OU data
OU_IDS = []  # Specific OUs or leave empty for all
OU_YEARS = ["2020", "2021", "2022"]
```

### Find KPI IDs

To discover available KPI IDs:
1. Run notebook `01_Fetch_KPI_Metadata.ipynb`
2. Browse the resulting `dKpi` dimension table
3. Look for KPIs of interest and note their IDs
4. Check `has_ou_data` column to see which KPIs support OU-level data
5. Use these IDs in notebook 03

### Understanding the Star Schema

The solution uses Power BI star schema naming conventions:
- **Dimensions** (prefix `d`): `dKpi`, `dMunicipality`, `dOrganizationalUnit`
- **Facts** (prefix `f`): `fKoladaData` (unified fact table)
- **Bridge tables** (prefix `br`): `brMunicipalityGroupMember`, `brKpiGroupMember`

All dimensions include integer surrogate keys for optimal Power BI performance:
- `kpi_key` in `dKpi`
- `municipality_key` in `dMunicipality`
- `ou_key` in `dOrganizationalUnit`

The unified fact table `fKoladaData` contains both municipality-level and OU-level data:
- Municipality records have `ou_id` starting with "NO_OU_"
- OU records have `ou_id` as the actual organizational unit ID

## Running the Notebooks

Execute the notebooks in the following order:

### Step 1: Fetch KPI Metadata
```
Notebook: 01_Fetch_KPI_Metadata.ipynb
Purpose: Downloads all available KPI definitions with surrogate keys
Output: dKpi dimension table
Estimated Time: 2-5 minutes
Key: Creates kpi_key surrogate integer keys for relationships
```

### Step 2: Fetch Municipality Metadata
```
Notebook: 02_Fetch_Municipality_Metadata.ipynb
Purpose: Downloads municipality, group, and OU metadata with surrogate keys
Output: Multiple dimension and bridge tables (dMunicipality, dOrganizationalUnit, 
        dMunicipalityGroup, dKpiGroup, brMunicipalityGroupMember, brKpiGroupMember)
Estimated Time: 3-7 minutes
Key: Creates surrogate keys and "No OU" placeholders for unified fact table
```

### Step 3: Fetch Data
```
Notebook: 03_Fetch_Kolada_Data.ipynb
Purpose: Downloads actual data values (both municipality and OU level)
Output: fKoladaData unified fact table
Estimated Time: Varies based on parameters (5-30 minutes)
Key: Combines municipality and OU data into single table with surrogate keys
```

### Scheduling Automated Runs

To keep your data up-to-date:

1. In Fabric, navigate to each notebook
2. Click on "Run" → "Schedule"
3. Set up a schedule (e.g., monthly for metadata, weekly for data)
4. Configure email notifications for failures

## Troubleshooting

### Issue: Authentication Fails

**Symptoms:** "401 Unauthorized" or "403 Forbidden" errors

**Solutions:**
- Verify your Service Principal credentials are correct
- Ensure the Service Principal has been granted admin consent for API permissions
- Check that the Service Principal has been added to the workspace
- Verify the workspace exists and you have access

### Issue: Lakehouse Not Attached

**Symptoms:** Error writing to Lakehouse, files saved to Files section instead

**Solutions:**
- Open the notebook
- Click "Add" in the Lakehouse panel on the left
- Select your Lakehouse
- Re-run the failing cell

### Issue: API Timeout or Connection Errors

**Symptoms:** Requests timeout, network errors

**Solutions:**
- Check your internet connection
- The Kolada API might be temporarily unavailable - retry later
- Reduce the batch size (fewer KPIs or years per request)

### Issue: No Data Retrieved

**Symptoms:** Empty DataFrames, zero rows

**Solutions:**
- Verify the KPI IDs are valid (check notebook 01 output in `dKpi` table)
- Ensure the years you're requesting have data
- Check if the municipality IDs are correct
- Some KPIs only have data for specific years or municipalities
- For OU data, ensure `has_ou_data = true` in the `dKpi` table for those KPIs

### Issue: Deployment Script Fails

**Symptoms:** Python errors, API errors

**Solutions:**
- Verify all environment variables are set correctly
- Check that Python dependencies are installed: `pip install -r requirements.txt`
- Ensure your Service Principal has the correct permissions
- Check the Fabric API status and your subscription limits

### Issue: Large Dataset Performance

**Symptoms:** Notebook runs very slowly, timeouts

**Solutions:**
- Process data in smaller batches (fewer years at a time)
- Use incremental loading with `from_date` parameter
- Consider filtering to specific municipalities
- Run during off-peak hours

## Best Practices

1. **Start Small**: Begin with 1-2 KPIs and a few years to test
2. **Monitor Costs**: Be aware of data storage and compute costs in Fabric
3. **Version Control**: Keep your notebook versions in sync with this repository
4. **Data Freshness**: Schedule regular updates based on Kolada's publication schedule
5. **Documentation**: Document any custom KPIs or queries you create
6. **Backup**: Regularly export important data or maintain backups

## Next Steps

After successful deployment:

1. **Explore the Data**
   - Open the Lakehouse
   - Browse the tables created
   - Create SQL endpoints for querying

2. **Create Power BI Reports**
   - Connect Power BI to your Lakehouse
   - Set up relationships using surrogate keys (kpi_key, municipality_key, ou_key)
   - Build visualizations using the star schema
   - Use the unified fact table to compare municipality and OU-level data
   - Leverage bridge tables for many-to-many relationships with groups
   - Share insights with stakeholders

3. **Extend the Solution**
   - Add custom transformations
   - Create aggregation tables
   - Integrate with other data sources

## Support and Resources

- **Kolada API Documentation**: https://github.com/Hypergene/kolada/wiki/API
- **Microsoft Fabric Documentation**: https://learn.microsoft.com/en-us/fabric/
- **Repository Issues**: https://github.com/villezekeviking/Kolada_Fabric/issues

## Updates and Maintenance

To get the latest version of the notebooks:

```bash
cd Kolada_Fabric
git pull origin main
```

Then re-upload the updated notebooks to your Fabric workspace.
