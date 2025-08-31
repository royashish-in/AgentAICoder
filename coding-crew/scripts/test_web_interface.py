#!/usr/bin/env python3
"""Test the web interface with sample data."""

import requests
import time
import json
from datetime import datetime

def test_web_interface():
    """Test the web interface with sample analysis data."""
    
    base_url = "http://localhost:8000"
    
    # Sample analysis data
    sample_analysis = {
        "id": "test-analysis-001",
        "title": "E-commerce Platform Analysis",
        "content": """# System Analysis: E-commerce Platform

## Architecture Overview
- **Frontend**: React.js with TypeScript
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL with Redis cache
- **Authentication**: JWT with OAuth2

## Key Components
1. User Management Service
2. Product Catalog Service  
3. Order Processing Service
4. Payment Gateway Integration
5. Inventory Management System

## Data Flow
1. User authentication → JWT token generation
2. Product browsing → Cache-first data retrieval
3. Order placement → Transaction processing
4. Payment processing → External gateway integration
5. Order fulfillment → Inventory updates

## Security Considerations
- Input validation on all endpoints
- Rate limiting for API calls
- Encrypted data transmission
- Secure session management""",
        "diagrams": [
            "system_architecture_diagram.xml",
            "data_flow_diagram.xml"
        ],
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }
    
    try:
        # Test API endpoints
        print("Testing Web Interface API...")
        
        # 1. Submit analysis
        print("\n1. Submitting sample analysis...")
        response = requests.post(f"{base_url}/api/analyses", json=sample_analysis)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # 2. Get all analyses
        print("\n2. Retrieving all analyses...")
        response = requests.get(f"{base_url}/api/analyses")
        print(f"Status: {response.status_code}")
        analyses = response.json()
        print(f"Found {len(analyses)} analyses")
        
        # 3. Get specific analysis
        print("\n3. Retrieving specific analysis...")
        response = requests.get(f"{base_url}/api/analyses/{sample_analysis['id']}")
        print(f"Status: {response.status_code}")
        analysis = response.json()
        print(f"Analysis title: {analysis.get('title')}")
        
        # 4. Check approval status
        print("\n4. Checking approval status...")
        response = requests.get(f"{base_url}/api/approval-status/{sample_analysis['id']}")
        print(f"Status: {response.status_code}")
        status = response.json()
        print(f"Approval status: {status}")
        
        print("\n✅ Web interface is working correctly!")
        print(f"🌐 Visit {base_url} to view the interface")
        print("📝 The sample analysis is ready for approval")
        
    except requests.ConnectionError:
        print("❌ Cannot connect to web interface")
        print("💡 Start the web interface first:")
        print("   python scripts/start_web_interface.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_web_interface()