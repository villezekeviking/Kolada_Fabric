"""
Microsoft Fabric Deployment Script for Kolada Data Ingestion

This script automates the deployment of Kolada data ingestion resources to Microsoft Fabric:
- Creates or updates a Workspace
- Creates a Lakehouse
- Uploads and creates Notebooks from the GitHub repository

Prerequisites:
- Azure AD App Registration with Fabric API permissions
- Service Principal credentials (Client ID, Client Secret, Tenant ID)
- Or use interactive authentication with Azure CLI

Environment Variables Required:
- FABRIC_TENANT_ID: Your Azure AD Tenant ID
- FABRIC_CLIENT_ID: Service Principal Client ID
- FABRIC_CLIENT_SECRET: Service Principal Client Secret
- FABRIC_WORKSPACE_NAME: Name of the Fabric workspace (optional, defaults to config)
"""

import requests
import json
import os
import sys
import base64
from pathlib import Path
from typing import Dict, Optional
import time


class FabricDeployer:
    """
    Handles deployment of resources to Microsoft Fabric workspace.
    """
    
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.base_url = "https://api.fabric.microsoft.com/v1"
        
    def get_access_token(self) -> str:
        """
        Obtain an access token from Azure AD.
        """
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'scope': 'https://api.fabric.microsoft.com/.default'
        }
        
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        
        self.access_token = response.json()['access_token']
        print("✓ Successfully obtained access token")
        return self.access_token
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests.
        """
        if not self.access_token:
            self.get_access_token()
        
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def create_workspace(self, workspace_name: str, description: str = "") -> str:
        """
        Create a new workspace or get existing workspace ID.
        
        Args:
            workspace_name: Name of the workspace
            description: Optional description
            
        Returns:
            Workspace ID
        """
        # First, check if workspace exists
        workspace_id = self.get_workspace_id(workspace_name)
        if workspace_id:
            print(f"✓ Workspace '{workspace_name}' already exists (ID: {workspace_id})")
            return workspace_id
        
        # Create new workspace
        url = f"{self.base_url}/workspaces"
        payload = {
            'displayName': workspace_name,
            'description': description
        }
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        
        workspace_id = response.json()['id']
        print(f"✓ Created workspace '{workspace_name}' (ID: {workspace_id})")
        return workspace_id
    
    def get_workspace_id(self, workspace_name: str) -> Optional[str]:
        """
        Get workspace ID by name.
        
        Args:
            workspace_name: Name of the workspace
            
        Returns:
            Workspace ID or None if not found
        """
        url = f"{self.base_url}/workspaces"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        workspaces = response.json().get('value', [])
        for workspace in workspaces:
            if workspace['displayName'] == workspace_name:
                return workspace['id']
        
        return None
    
    def create_lakehouse(self, workspace_id: str, lakehouse_name: str, description: str = "") -> str:
        """
        Create a Lakehouse in the workspace.
        
        Args:
            workspace_id: ID of the workspace
            lakehouse_name: Name of the lakehouse
            description: Optional description
            
        Returns:
            Lakehouse ID
        """
        # Check if lakehouse exists
        lakehouse_id = self.get_lakehouse_id(workspace_id, lakehouse_name)
        if lakehouse_id:
            print(f"✓ Lakehouse '{lakehouse_name}' already exists (ID: {lakehouse_id})")
            return lakehouse_id
        
        # Create lakehouse
        url = f"{self.base_url}/workspaces/{workspace_id}/lakehouses"
        payload = {
            'displayName': lakehouse_name,
            'description': description
        }
        
        response = requests.post(url, headers=self._get_headers(), json=payload)
        response.raise_for_status()
        
        lakehouse_id = response.json()['id']
        print(f"✓ Created lakehouse '{lakehouse_name}' (ID: {lakehouse_id})")
        return lakehouse_id
    
    def get_lakehouse_id(self, workspace_id: str, lakehouse_name: str) -> Optional[str]:
        """
        Get lakehouse ID by name.
        
        Args:
            workspace_id: ID of the workspace
            lakehouse_name: Name of the lakehouse
            
        Returns:
            Lakehouse ID or None if not found
        """
        url = f"{self.base_url}/workspaces/{workspace_id}/lakehouses"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        lakehouses = response.json().get('value', [])
        for lakehouse in lakehouses:
            if lakehouse['displayName'] == lakehouse_name:
                return lakehouse['id']
        
        return None
    
    def create_notebook(self, workspace_id: str, notebook_name: str, notebook_path: Path) -> str:
        """
        Create or update a notebook in the workspace.
        
        Args:
            workspace_id: ID of the workspace
            notebook_name: Name of the notebook
            notebook_path: Path to the notebook file
            
        Returns:
            Notebook ID
        """
        # Read notebook content
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook_content = f.read()
        
        # Encode content as Base64
        encoded_content = base64.b64encode(notebook_content.encode()).decode()
        
        # Check if notebook exists
        notebook_id = self.get_notebook_id(workspace_id, notebook_name)
        
        if notebook_id:
            # Update existing notebook
            url = f"{self.base_url}/workspaces/{workspace_id}/notebooks/{notebook_id}/updateDefinition"
            payload = {
                'definition': {
                    'format': 'ipynb',
                    'parts': [
                        {
                            'path': 'notebook-content.py',
                            'payload': encoded_content,
                            'payloadType': 'InlineBase64'
                        }
                    ]
                }
            }
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            print(f"✓ Updated notebook '{notebook_name}'")
            return notebook_id
        else:
            # Create new notebook
            url = f"{self.base_url}/workspaces/{workspace_id}/notebooks"
            payload = {
                'displayName': notebook_name,
                'definition': {
                    'format': 'ipynb',
                    'parts': [
                        {
                            'path': 'notebook-content.py',
                            'payload': encoded_content,
                            'payloadType': 'InlineBase64'
                        }
                    ]
                }
            }
            
            response = requests.post(url, headers=self._get_headers(), json=payload)
            response.raise_for_status()
            
            notebook_id = response.json()['id']
            print(f"✓ Created notebook '{notebook_name}' (ID: {notebook_id})")
            return notebook_id
    
    def get_notebook_id(self, workspace_id: str, notebook_name: str) -> Optional[str]:
        """
        Get notebook ID by name.
        
        Args:
            workspace_id: ID of the workspace
            notebook_name: Name of the notebook
            
        Returns:
            Notebook ID or None if not found
        """
        url = f"{self.base_url}/workspaces/{workspace_id}/notebooks"
        response = requests.get(url, headers=self._get_headers())
        response.raise_for_status()
        
        notebooks = response.json().get('value', [])
        for notebook in notebooks:
            if notebook['displayName'] == notebook_name:
                return notebook['id']
        
        return None


def deploy_kolada_fabric(
    tenant_id: str,
    client_id: str,
    client_secret: str,
    workspace_name: str,
    lakehouse_name: str,
    notebooks_dir: Path
):
    """
    Main deployment function.
    
    Args:
        tenant_id: Azure AD Tenant ID
        client_id: Service Principal Client ID
        client_secret: Service Principal Client Secret
        workspace_name: Name of the Fabric workspace
        lakehouse_name: Name of the lakehouse
        notebooks_dir: Path to the notebooks directory
    """
    print("="*60)
    print("Microsoft Fabric Deployment - Kolada Data Ingestion")
    print("="*60)
    print()
    
    # Initialize deployer
    deployer = FabricDeployer(tenant_id, client_id, client_secret)
    
    # Step 1: Create/Get Workspace
    print("Step 1: Setting up Workspace")
    workspace_id = deployer.create_workspace(
        workspace_name,
        "Workspace for Kolada data ingestion and analysis"
    )
    print()
    
    # Step 2: Create/Get Lakehouse
    print("Step 2: Setting up Lakehouse")
    lakehouse_id = deployer.create_lakehouse(
        workspace_id,
        lakehouse_name,
        "Lakehouse for storing Kolada data"
    )
    print()
    
    # Step 3: Upload Notebooks
    print("Step 3: Uploading Notebooks")
    notebook_files = sorted(notebooks_dir.glob("*.ipynb"))
    
    if not notebook_files:
        print(f"⚠ No notebook files found in {notebooks_dir}")
    else:
        for notebook_file in notebook_files:
            notebook_name = notebook_file.stem
            try:
                deployer.create_notebook(workspace_id, notebook_name, notebook_file)
            except Exception as e:
                print(f"✗ Error deploying {notebook_name}: {e}")
    
    print()
    print("="*60)
    print("Deployment Complete!")
    print("="*60)
    print(f"Workspace: {workspace_name} (ID: {workspace_id})")
    print(f"Lakehouse: {lakehouse_name} (ID: {lakehouse_id})")
    print(f"Notebooks deployed: {len(notebook_files)}")
    print()
    print("Next steps:")
    print("1. Open the Fabric workspace in your browser")
    print("2. Navigate to the notebooks")
    print("3. Attach the lakehouse to each notebook")
    print("4. Run the notebooks in order (01, 02, 03)")


def main():
    """
    Main entry point for the deployment script.
    """
    # Load configuration
    config_path = Path(__file__).parent.parent / 'config' / 'config.json'
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        workspace_name = config.get('workspace_name', 'KoladaWorkspace')
        lakehouse_name = config.get('lakehouse_name', 'KoladaLakehouse')
    else:
        workspace_name = os.getenv('FABRIC_WORKSPACE_NAME', 'KoladaWorkspace')
        lakehouse_name = 'KoladaLakehouse'
    
    # Get credentials from environment variables
    tenant_id = os.getenv('FABRIC_TENANT_ID')
    client_id = os.getenv('FABRIC_CLIENT_ID')
    client_secret = os.getenv('FABRIC_CLIENT_SECRET')
    
    if not all([tenant_id, client_id, client_secret]):
        print("Error: Missing required environment variables")
        print("Please set: FABRIC_TENANT_ID, FABRIC_CLIENT_ID, FABRIC_CLIENT_SECRET")
        sys.exit(1)
    
    # Get notebooks directory
    notebooks_dir = Path(__file__).parent.parent / 'notebooks'
    
    if not notebooks_dir.exists():
        print(f"Error: Notebooks directory not found at {notebooks_dir}")
        sys.exit(1)
    
    # Run deployment
    try:
        deploy_kolada_fabric(
            tenant_id,
            client_id,
            client_secret,
            workspace_name,
            lakehouse_name,
            notebooks_dir
        )
    except Exception as e:
        print(f"\n✗ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
