Bajaj Health Datathon - Bill Data Extraction Pipeline
📌 Overview
This project is an automated bill data extraction pipeline designed for the Bajaj Health Datathon. It processes medical invoices (images/PDFs) to extract granular line items, ensuring mathematical reconciliation of totals and avoidance of double-counting (subtotals vs. items).
The solution is deployed as a FastAPI service on Railway, powered by Azure OpenAI (GPT-4 Vision) for high-accuracy extraction.
⚙️ Tech Stack
Framework: FastAPI (Python 3.9+)
AI Model: Azure OpenAI (GPT-4 Vision)
PDF/Image Processing: PyMuPDF, Pillow, OpenCV
Deployment: Railway
🔌 API Documentation
Endpoint Details
Base URL: https://bajajmlps-production.up.railway.app
Route: /extract-bill-data
Method: POST
Content-Type: application/json
Request Format
The API accepts a public URL to an image or PDF.
{
  "document": "[https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png)"
}


Response Format
Returns extracted line items and the mathematically reconciled total.
{
  "is_success": true,
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "bill_items": [
          {
            "item_name": "Livi 300mg Tab",
            "item_amount": 448.0,
            "item_rate": 32.0,
            "item_quantity": 14
          }
        ]
      }
    ],
    "total_item_count": 1,
    "reconciled_amount": 448.0
  }
}


🧪 Testing the API (Important)
You can test the deployed solution using the methods below.
1. Python Script
import requests
import json

url = "[https://bajajmlps-production.up.railway.app/extract-bill-data](https://bajajmlps-production.up.railway.app/extract-bill-data)"
payload = {
    "document": "[https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png)"
}
headers = {'Content-Type': 'application/json'}

try:
    response = requests.post(url, headers=headers, json=payload)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")


2. cURL (Terminal)
curl -X POST "[https://bajajmlps-production.up.railway.app/extract-bill-data](https://bajajmlps-production.up.railway.app/extract-bill-data)" \
     -H "Content-Type: application/json" \
     -d '{"document": "[https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png)"}'


3. PowerShell (Windows)
$body = @{ document = "[https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png)" } | ConvertTo-Json
Invoke-RestMethod -Uri "[https://bajajmlps-production.up.railway.app/extract-bill-data](https://bajajmlps-production.up.railway.app/extract-bill-data)" -Method Post -Headers @{ "Content-Type" = "application/json" } -Body $body


🧠 Solution Logic
Input: Fetches document from URL; converts PDFs to high-res images.
Extraction: Azure GPT-4 Vision identifies table structures and line items.
Filtration: Strictly excludes "Subtotal", "GST", and "Balance Due" rows to prevent double-counting.
Reconciliation: Calculates reconciled_amount by summing individual item_amount values to verify accuracy against the bill's grand total.
⚠️ Environment Variables (For Local Dev)
USE_AZURE_OPENAI=true
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT_NAME=<your-deployment>
