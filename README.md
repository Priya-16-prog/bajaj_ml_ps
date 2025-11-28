# Bajaj Health Datathon - Bill Data Extraction Pipeline

## Overview
This project is an automated **bill data extraction pipeline** designed for the Bajaj Health Datathon.  
It processes **medical invoices (images/PDFs)** and extracts granular line items while ensuring:

- No double-counting of totals/subtotals  
- Accurate mathematical reconciliation  
- High-accuracy extraction using **Azure OpenAI GPT-4 Vision**

The solution is deployed as a **FastAPI web service on Railway**.

---

## Tech Stack

- **Framework:** FastAPI (Python 3.9+)
- **AI Model:** Azure OpenAI (GPT-4 Vision / GPT-4.1 Vision)
- **Processing:** PyMuPDF (PDF), Pillow (images), OpenCV
- **Deployment:** Railway

---

# API Documentation

## **Endpoint Details**

| Property | Value |
|---------|--------|
| **Base URL** | `https://bajajmlps-production.up.railway.app` |
| **Route** | `/extract-bill-data` |
| **Method** | `POST` |
| **Content-Type** | `application/json` |

---

## Request Format

Send a public URL pointing to an image or PDF.

```json
{
  "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_3.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A24%3A39Z&se=2026-11-25T14%3A24%3A00Z&sr=b&sp=r&sig=egKAmIUms8H5f3kgrGXKvcfuBVlQp0Qc2tsfxdvRgUY%3D"
}
```

## Response Format

The API returns extracted line items and the mathematically reconciled total.

```json
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
```

# Testing the API

You can test the deployed API using any of the following:
## 1. Python Script

```python
import requests
import json

url = "https://bajajmlps-production.up.railway.app/extract-bill-data"
payload = {
    "document": "[https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_3.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A24%3A39Z&se=2026-11-25T14%3A24%3A00Z&sr=b&sp=r&sig=egKAmIUms8H5f3kgrGXKvcfuBVlQp0Qc2tsfxdvRgUY%3D)"
}

headers = {"Content-Type": "application/json"}

try:
    response = requests.post(url, headers=headers, json=payload)
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
```

## 2. cURL (Linux/Mac)

```bash
curl -X POST "https://bajajmlps-production.up.railway.app/extract-bill-data" \
     -H "Content-Type: application/json" \
     -d '{"document": "[https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_3.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A24%3A39Z&se=2026-11-25T14%3A24%3A00Z&sr=b&sp=r&sig=egKAmIUms8H5f3kgrGXKvcfuBVlQp0Qc2tsfxdvRgUY%3D)"}'
```

## 3. PowerShell (Windows)
```powershell
$body = @{
  document = "[https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png](https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_3.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A24%3A39Z&se=2026-11-25T14%3A24%3A00Z&sr=b&sp=r&sig=egKAmIUms8H5f3kgrGXKvcfuBVlQp0Qc2tsfxdvRgUY%3D)"
} | ConvertTo-Json

 curl -Method POST `
>>   -Uri "https://bajajmlps-production.up.railway.app/extract-bill-data" `
>>   -Headers @{ "Content-Type" = "application/json" } `
>>   -Body $body | Select-Object -ExpandProperty Content
```

# Solution Logic

Input: Fetches document from URL; converts PDFs to high-res images.

Extraction: Azure GPT-4 Vision identifies table structures and line items.

Filtration: Strictly excludes "Subtotal", "GST", and "Balance Due" rows to prevent double-counting.

Reconciliation: Calculates reconciled_amount by summing individual item_amount values to verify accuracy against the bill's grand total.
