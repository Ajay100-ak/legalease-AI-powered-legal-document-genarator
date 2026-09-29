import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

router = APIRouter()

# ============================================================
# GEMINI CONFIGURATION
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-3.8-flash"

client = None

if API_KEY:
    client = genai.Client(api_key=API_KEY)


# ============================================================
# REQUEST MODEL
# ============================================================

class DocumentRequest(BaseModel):
    document_type: str
    parties: str
    terms: str
    effective_date: str


# ============================================================
# FALLBACK DOCUMENT
# ============================================================

def create_fallback_document(request: DocumentRequest):

    return f"""
LEGAL DOCUMENT DRAFT

Document Type:
{request.document_type}

Parties:
{request.parties}

Effective Date:
{request.effective_date}

TERMS AND CONDITIONS

{request.terms}

GENERAL PROVISIONS

1. The parties agree to comply with the terms stated above.

2. Any amendment to this document should be made in writing
and agreed to by the relevant parties.

3. The parties should comply with all applicable laws and
regulations.

4. This document is provided as a draft for informational
purposes and should be reviewed by a qualified legal
professional before use.

SIGNATURES

Party 1: __________________________

Name: _____________________________

Date: _____________________________


Party 2: __________________________

Name: _____________________________

Date: _____________________________
"""


# ============================================================
# TEST ENDPOINT
# ============================================================

@router.get("/test")
def test():
    return {
        "message": "LegalEase backend is working",
        "model": MODEL
    }


# ============================================================
# GENERATE DOCUMENT
# ============================================================

@router.post("/generate")
def generate_document(request: DocumentRequest):

    prompt = f"""
You are LegalEase AI, an assistant for creating legal document drafts.

Create a professional legal document based ONLY on the information
provided by the user.

Document type:
{request.document_type}

Parties:
{request.parties}

Terms:
{request.terms}

Effective date:
{request.effective_date}

Instructions:

1. Use clear and professional legal language.
2. Give the document an appropriate title.
3. Clearly identify the parties.
4. Clearly state the effective date.
5. Clearly state the terms and conditions.
6. Include relevant clauses where appropriate.
7. Include a signature section.
8. Do not invent important facts that were not provided.
9. Do not claim that the document is legal advice.
10. Clearly state that this is a draft that should be reviewed
    by a qualified legal professional.

Return ONLY the document text.
"""

    # ========================================================
    # CHECK API KEY
    # ========================================================

    if client is None:
        return {
            "document": create_fallback_document(request),
            "source": "fallback",
            "message": "Gemini API key was not found. A basic draft was generated.",
            "model": MODEL
        }

    # ========================================================
    # CALL GEMINI
    # ========================================================

    try:

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        if response is None:
            raise Exception("Gemini returned no response.")

        if not response.text:
            raise Exception("Gemini returned an empty response.")

        return {
            "document": response.text,
            "source": "gemini",
            "model": MODEL
        }

    # ========================================================
    # GEMINI QUOTA / RATE LIMIT
    # ========================================================

    except Exception as e:

        error_message = str(e)

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED" in error_message
            or "quota" in error_message.lower()
            or "rate limit" in error_message.lower()
        ):

            return {
                "document": create_fallback_document(request),
                "source": "fallback",
                "message": "Gemini API quota is currently unavailable. A basic draft was generated instead.",
                "model": MODEL
            }

        # ====================================================
        # MODEL NOT FOUND
        # ====================================================

        if "404" in error_message or "NOT_FOUND" in error_message:

            raise HTTPException(
                status_code=500,
                detail=(
                    f"Gemini model '{MODEL}' is unavailable for this API key/project. "
                    f"Check the Gemini API model access. Original error: {error_message}"
                )
            )

        # ====================================================
        # OTHER GEMINI ERROR
        # ====================================================

        raise HTTPException(
            status_code=500,
            detail=f"Gemini generation failed: {error_message}"
        )