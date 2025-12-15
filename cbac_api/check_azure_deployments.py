"""
Helper script to test Azure OpenAI connection and list available deployments.
This helps identify the correct deployment name to use.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import AzureOpenAI
from app.config.settings import settings


def test_deployments():
    """Test different common deployment names"""
    print("Testing Azure OpenAI Connection...")
    print(f"API Base: {settings.OPENAI_API_BASE}")
    print(f"API Key: {'***' + settings.OPENAI_API_KEY[-8:] if settings.OPENAI_API_KEY else 'NOT SET'}")
    print()
    
    client = AzureOpenAI(
        api_key=settings.OPENAI_API_KEY,
        api_version="2024-02-15-preview",
        azure_endpoint=settings.OPENAI_API_BASE
    )
    
    # Common deployment names to try
    deployment_names = [
        "gpt-4",
        "gpt-4o",
        "gpt-4-32k",
        "gpt-35-turbo",
        "gpt-4-turbo",
        "gpt-4o-mini",
        settings.OPENAI_DEPLOYMENT_NAME
    ]
    
    print("Testing common deployment names:\n")
    
    working_deployments = []
    
    for deployment in deployment_names:
        try:
            print(f"Testing '{deployment}'...", end=" ")
            response = client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print(f"✅ WORKS")
            working_deployments.append(deployment)
        except Exception as e:
            error_msg = str(e)
            if "DeploymentNotFound" in error_msg:
                print(f"❌ Not found")
            elif "InvalidRequestError" in error_msg:
                print(f"⚠️  Found but invalid request")
                working_deployments.append(deployment)
            else:
                print(f"❌ Error: {error_msg[:50]}")
    
    print("\n" + "="*60)
    if working_deployments:
        print(f"✅ Found {len(working_deployments)} working deployment(s):")
        for dep in working_deployments:
            print(f"   - {dep}")
        print(f"\nRecommendation: Update .env with:")
        print(f"OPENAI_DEPLOYMENT_NAME={working_deployments[0]}")
    else:
        print("❌ No working deployments found!")
        print("\nPossible issues:")
        print("1. Deployment names don't match standard names")
        print("2. API key is incorrect or expired")
        print("3. API endpoint URL is incorrect")
        print("4. No chat models deployed in this resource")
        print("\nPlease check your Azure OpenAI resource in Azure Portal.")


if __name__ == "__main__":
    test_deployments()
