"""
Bill Extraction API - Main FastAPI Application
Extracts line items, sub-totals, and final totals from multi-page bills/invoices
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
from datetime import datetime

from services.document_processor import DocumentProcessor
from services.extraction_service import ExtractionService
from services.data_validator import DataValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Bill Extraction API",
    description="Extract line items, sub-totals, and totals from bills/invoices",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_processor = DocumentProcessor()
extraction_service = ExtractionService()
data_validator = DataValidator()


# Request/Response Models
class ExtractRequest(BaseModel):
    document: str = Field(..., description="URL of the document to process")


class TokenUsage(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int


class BillItem(BaseModel):
    item_name: str
    item_amount: float
    item_rate: float
    item_quantity: float


class PageLineItems(BaseModel):
    page_no: str
    page_type: str  # "Bill Detail" | "Final Bill" | "Pharmacy"
    bill_items: List[BillItem]


class ExtractionData(BaseModel):
    pagewise_line_items: List[PageLineItems]
    total_item_count: int
    reconciled_amount: float


class ExtractResponse(BaseModel):
    is_success: bool
    token_usage: TokenUsage
    data: ExtractionData


@app.get("/")
async def root():
    return {
        "message": "Bill Extraction API",
        "version": "1.0.0",
        "endpoint": "/extract-bill-data"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/extract-bill-data", response_model=ExtractResponse)
async def extract_bill_data(request: ExtractRequest):
    """
    Extract line items, sub-totals, and final totals from a bill/invoice document.
    
    Args:
        request: Contains document URL
        
    Returns:
        Structured response with pagewise line items and totals
    """
    try:
        logger.info(f"Processing document: {request.document}")
        
        # Step 1: Download and process document
        pages_data = await document_processor.process_document(request.document)
        if not pages_data:
            raise HTTPException(
                status_code=400,
                detail="Failed to process document. Please check the document URL."
            )
        
        logger.info(f"Document processed: {len(pages_data)} pages found")
        
        # Step 2: Extract data using LLM
        extraction_result = await extraction_service.extract_bill_data(pages_data)
        
        if not extraction_result or not extraction_result.get("pagewise_line_items"):
            raise HTTPException(
                status_code=500,
                detail="Failed to extract data from document"
            )
        
        # Step 3: Validate and deduplicate data
        validated_data = data_validator.validate_and_deduplicate(
            extraction_result["pagewise_line_items"]
        )
        
        # Step 4: Calculate total item count
        total_item_count = sum(
            len(page["bill_items"]) for page in validated_data
        )
        
        # Step 5: Calculate reconciled amount (sum of all item amounts)
        reconciled_amount = 0.0
        for page in validated_data:
            for item in page["bill_items"]:
                reconciled_amount += item.get("item_amount", 0.0)
        
        # Round to 2 decimal places for currency
        reconciled_amount = round(reconciled_amount, 2)
        
        # Step 6: Prepare response
        response_data = ExtractionData(
            pagewise_line_items=[
                PageLineItems(**page) for page in validated_data
            ],
            total_item_count=total_item_count,
            reconciled_amount=reconciled_amount
        )
        
        token_usage = extraction_result.get("token_usage", {
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0
        })
        
        return ExtractResponse(
            is_success=True,
            token_usage=TokenUsage(**token_usage),
            data=response_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

