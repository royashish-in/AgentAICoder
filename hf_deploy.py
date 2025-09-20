#!/usr/bin/env python3
"""
Hugging Face Spaces deployment script for AgentAI
"""

import os
import subprocess
from huggingface_hub import HfApi, create_repo

def deploy_to_huggingface():
    """Deploy AgentAI to Hugging Face Spaces."""
    
    # Configuration
    SPACE_NAME = "AgentAI"
    USERNAME = "royashish"  # Your actual HF username
    
    print("🚀 Deploying AgentAI to Hugging Face Spaces...")
    
    try:
        # Initialize Hugging Face API
        api = HfApi()
        
        # Create repository
        repo_id = f"{USERNAME}/{SPACE_NAME}"
        
        print(f"📦 Creating repository: {repo_id}")
        
        try:
            create_repo(
                repo_id=repo_id,
                repo_type="space",
                space_sdk="gradio",
                exist_ok=True
            )
            print("✅ Repository created successfully!")
        except Exception as e:
            print(f"ℹ️  Repository might already exist: {e}")
        
        # Upload files
        print("📤 Uploading files to Hugging Face Spaces...")
        
        files_to_upload = [
            "app.py",
            "requirements.txt", 
            "README.md",
            "Dockerfile",
            ".gitignore"
        ]
        
        for file in files_to_upload:
            if os.path.exists(file):
                print(f"  📄 Uploading {file}...")
                api.upload_file(
                    path_or_fileobj=file,
                    path_in_repo=file,
                    repo_id=repo_id,
                    repo_type="space"
                )
            else:
                print(f"  ⚠️  File not found: {file}")
        
        print(f"""
🎉 AgentAI successfully deployed to Hugging Face Spaces!

🔗 Your Space URL: https://huggingface.co/spaces/{repo_id}

Next steps:
1. Visit your Space URL to see AgentAI in action
2. Update the README.md with your actual Space URL
3. Customize the interface and models as needed
4. Share with the Hugging Face community!

🤗 Welcome to the Hugging Face ecosystem!
        """)
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're logged in: huggingface-cli login")
        print("2. Check your internet connection")
        print("3. Verify your Hugging Face username")

if __name__ == "__main__":
    deploy_to_huggingface()