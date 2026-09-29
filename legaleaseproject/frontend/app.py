import os
from datetime import date
from io import BytesIO
from html import escape

import requests
import streamlit as st

from dotenv import load_dotenv
from docx import Document
from docx.shared import Pt
from fpdf import FPDF


# ==================================================
# CONFIGURATION
# ==================================================

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)


st.set_page_config(
    page_title="LegalEase AI",
    page_icon="⚖️",
    layout="wide"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #888888;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .preview-box {
        background-color: #111827;
        color: #f9fafb;
        padding: 25px;
        border-radius: 12px;
        line-height: 1.7;
        max-height: 600px;
        overflow-y: auto;
        white-space: pre-wrap;
        border: 1px solid #374151;
    }

    .notice {
        padding: 12px;
        border-radius: 8px;
        background-color: #fff7ed;
        border: 1px solid #fed7aa;
        color: #9a3412;
        margin-top: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==================================================
# SESSION STATE
# ==================================================

if "document" not in st.session_state:
    st.session_state["document"] = ""

if "document_type" not in st.session_state:
    st.session_state["document_type"] = ""

if "terms" not in st.session_state:
    st.session_state["terms"] = ""

if "editing" not in st.session_state:
    st.session_state["editing"] = False


# ==================================================
# HEADER
# ==================================================

st.markdown(
    '<div class="main-title">⚖️ LegalEase AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI-Powered Legal Document Generator</div>',
    unsafe_allow_html=True
)


st.markdown(
    """
    LegalEase AI helps you create structured legal document drafts
    from your information using artificial intelligence.
    """,
    unsafe_allow_html=True
)


# ==================================================
# INPUT SECTION
# ==================================================

st.markdown(
    '<div class="section-title">📋 Document Details</div>',
    unsafe_allow_html=True
)


col1, col2 = st.columns(2)


with col1:

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Lease Agreement",
            "Service Agreement",
            "Freelance Agreement",
            "Partnership Agreement",
            "Sale Agreement",
            "Consulting Agreement",
            "Other"
        ]
    )


with col2:

    effective_date = st.date_input(
        "Effective Date",
        value=date.today()
    )


parties = st.text_area(
    "Parties Involved",
    placeholder=(
        "Example:\n"
        "Party 1: ABC Technologies Pvt. Ltd.\n"
        "Party 2: John Doe"
    ),
    height=120
)


terms = st.text_area(
    "Terms and Conditions",
    placeholder=(
        "Enter the important terms and conditions.\n\n"
        "Example:\n"
        "Salary: ₹50,000 per month\n"
        "Working hours: 9 AM to 6 PM\n"
        "Notice period: 30 days\n"
        "Confidentiality: Required"
    ),
    height=220
)


# ==================================================
# GENERATE DOCUMENT
# ==================================================

if st.button(
    "🚀 Generate Legal Document",
    use_container_width=True,
    type="primary"
):

    if not parties.strip():
        st.warning("Please enter the parties involved.")

    elif not terms.strip():
        st.warning("Please enter the terms and conditions.")

    else:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": str(effective_date)
        }

        with st.spinner(
            "Generating your legal document..."
        ):

            try:

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=120
                )

                if response.status_code == 200:

                    result = response.json()

                    generated_document = result.get(
                        "document",
                        ""
                    )

                    if generated_document:

                        st.session_state["document"] = (
                            generated_document
                        )

                        st.session_state["document_type"] = (
                            document_type
                        )

                        st.session_state["terms"] = terms

                        st.session_state["editing"] = False

                        st.success(
                            "Legal document generated successfully!"
                        )

                    else:

                        st.error(
                            "The backend returned an empty document."
                        )

                else:

                    try:
                        error_detail = response.json().get(
                            "detail",
                            response.text
                        )
                    except Exception:
                        error_detail = response.text

                    st.error(
                        f"Backend error ({response.status_code}): "
                        f"{error_detail}"
                    )

            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to the LegalEase backend."
                )

                st.info(
                    "Make sure FastAPI is running with:\n\n"
                    "uvicorn backend.main:app --reload"
                )

            except requests.exceptions.Timeout:

                st.error(
                    "The request timed out. Gemini may be busy. "
                    "Please try again."
                )

            except Exception as e:

                st.error(
                    f"Unexpected error: {str(e)}"
                )


# ==================================================
# DOCUMENT PREVIEW
# ==================================================

document = st.session_state.get(
    "document",
    ""
)


if document:

    st.markdown("---")

    st.markdown(
        '<div class="section-title">📄 Document Preview</div>',
        unsafe_allow_html=True
    )


    # ==================================================
    # EDIT BUTTON
    # ==================================================

    if not st.session_state["editing"]:

        if st.button(
            "✏️ Edit Document",
            use_container_width=False
        ):

            st.session_state["editing"] = True
            st.rerun()


    # ==================================================
    # EDIT MODE
    # ==================================================

    if st.session_state["editing"]:

        edited_document = st.text_area(
            "Edit your document",
            value=document,
            height=600
        )


        save_col, cancel_col = st.columns(2)


        with save_col:

            if st.button(
                "💾 Save Changes",
                use_container_width=True
            ):

                st.session_state["document"] = (
                    edited_document
                )

                st.session_state["editing"] = False

                st.success(
                    "Changes saved successfully."
                )

                st.rerun()


        with cancel_col:

            if st.button(
                "↩️ Cancel",
                use_container_width=True
            ):

                st.session_state["editing"] = False
                st.rerun()


        document = st.session_state["document"]


    # ==================================================
    # NORMAL PREVIEW
    # ==================================================

    else:

        safe_document = escape(document)

        st.markdown(
            f"""
            <div class="preview-box">
            {safe_document}
            </div>
            """,
            unsafe_allow_html=True
        )


# ==================================================
# DOCX CREATION
# ==================================================

if document:

    docx_document = Document()


    # Page margins
    section = docx_document.sections[0]

    section.top_margin = 720
    section.bottom_margin = 720
    section.left_margin = 720
    section.right_margin = 720


    # Title
    title = docx_document.add_paragraph()

    title.alignment = 1

    run = title.add_run(
        st.session_state.get(
            "document_type",
            document_type
        )
    )

    run.bold = True
    run.font.size = Pt(18)


    docx_document.add_paragraph()


    # Add document content
    lines = document.split("\n")


    for line in lines:

        line = line.strip()

        if not line:
            docx_document.add_paragraph()
            continue


        paragraph = docx_document.add_paragraph()

        # Detect numbered headings
        is_heading = (
            line[:2].isdigit()
            and "." in line[:3]
        )


        if is_heading:

            run = paragraph.add_run(line)

            run.bold = True
            run.font.size = Pt(12)

        else:

            run = paragraph.add_run(line)

            run.font.size = Pt(10.5)


    # Footer
    footer = section.footer

    footer_paragraph = footer.paragraphs[0]

    footer_paragraph.alignment = 1

    footer_run = footer_paragraph.add_run(
        "AI-generated draft. Review with a qualified legal professional before use."
    )

    footer_run.font.size = Pt(8)


    docx_buffer = BytesIO()

    docx_document.save(docx_buffer)

    docx_file = docx_buffer.getvalue()


# ==================================================
# PDF CREATION
# ==================================================

if document:

    class LegalEasePDF(FPDF):

        def footer(self):

            self.set_y(-15)

            self.set_font(
                "Arial",
                size=8
            )

            self.cell(
                0,
                8,
                "LegalEase - AI-generated draft. Review with a qualified legal professional before use.",
                align="C"
            )


    # Create PDF
    pdf = LegalEasePDF()


    # --------------------------------------------------
    # UNICODE ARIAL FONT
    # --------------------------------------------------

    pdf.add_font(
        "Arial",
        "",
        r"C:\Windows\Fonts\arial.ttf"
    )

    pdf.add_font(
        "Arial",
        "B",
        r"C:\Windows\Fonts\arialbd.ttf"
    )


    # --------------------------------------------------
    # PAGE SETTINGS
    # --------------------------------------------------

    pdf.set_auto_page_break(
        auto=True,
        margin=20
    )


    pdf.set_margins(
        18,
        18,
        18
    )


    pdf.add_page()


    # --------------------------------------------------
    # TITLE
    # --------------------------------------------------

    pdf.set_font(
        "Arial",
        "B",
        16
    )


    pdf.multi_cell(
        0,
        10,
        st.session_state.get(
            "document_type",
            document_type
        ),
        align="C"
    )


    pdf.ln(5)


    # --------------------------------------------------
    # DOCUMENT CONTENT
    # --------------------------------------------------

    lines = document.split("\n")


    for line in lines:

        line = line.strip()


        if not line:

            pdf.ln(3)

            continue


        # Detect numbered sections
        first_part = line.split(".", 1)[0]


        is_numbered_heading = (
            first_part.isdigit()
            and len(first_part) <= 2
            and "." in line
        )


        if is_numbered_heading:

            pdf.set_font(
                "Arial",
                "B",
                11
            )


            pdf.multi_cell(
                0,
                7,
                line
            )


            pdf.ln(1)


        else:

            pdf.set_font(
                "Arial",
                size=10
            )


            pdf.multi_cell(
                pdf.epw,
                6,
                line
            )


            pdf.ln(1)


    # --------------------------------------------------
    # CREATE PDF FILE
    # --------------------------------------------------

    pdf_file = bytes(
        pdf.output()
    )


# ==================================================
# DOWNLOAD SECTION
# ==================================================

if document:

    st.markdown("---")


    st.markdown(
        '<div class="section-title">⬇️ Download Document</div>',
        unsafe_allow_html=True
    )


    col1, col2, col3 = st.columns(3)


    # --------------------------------------------------
    # TXT
    # --------------------------------------------------

    with col1:

        st.download_button(
            label="📄 Download TXT",
            data=document,
            file_name="LegalEase_Document.txt",
            mime="text/plain",
            use_container_width=True
        )


    # --------------------------------------------------
    # DOCX
    # --------------------------------------------------

    with col2:

        st.download_button(
            label="📝 Download DOCX",
            data=docx_file,
            file_name="LegalEase_Document.docx",
            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True
        )


    # --------------------------------------------------
    # PDF
    # --------------------------------------------------

    with col3:

        st.download_button(
            label="📕 Download PDF",
            data=pdf_file,
            file_name="LegalEase_Document.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# ==================================================
# DISCLAIMER
# ==================================================

if document:

    st.markdown(
        """
        <div class="notice">
        ⚠️ <b>Important:</b> LegalEase AI generates drafts for
        informational purposes. Review the document with a
        qualified legal professional before using it for legal purposes.
        </div>
        """,
        unsafe_allow_html=True
    )