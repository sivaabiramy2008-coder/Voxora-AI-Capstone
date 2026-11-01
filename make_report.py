from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from xml.sax.saxutils import escape
from pathlib import Path

out = Path("report/Voxora_AI_Final_Report.pdf")
doc = SimpleDocTemplate(str(out), pagesize=A4,
    rightMargin=18*mm, leftMargin=18*mm,
    topMargin=16*mm, bottomMargin=16*mm)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="SmallBody", parent=styles["BodyText"],
    fontSize=9, leading=13, spaceAfter=6))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"],
    textColor=colors.HexColor("#176B52"), fontSize=12, leading=15,
    spaceBefore=8, spaceAfter=5))

story = []
story.append(Paragraph("VOXORA AI", styles["Title"]))
story.append(Paragraph("AI-Powered Customer Support Assistant for ZentroMart",
    styles["Heading2"]))
story.append(Paragraph("CAPSTONE PROJECT REPORT", styles["Heading3"]))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#176B52")))
story.append(Spacer(1, 10))

sections = [
("1. Project Overview",
"Voxora AI is a customer-support assistant prototype for the fictional ZentroMart store. It uses a Flask web application and a structured knowledge base to retrieve relevant support information and respond to customer queries."),
("2. Problem Statement",
"Customers often need help with order tracking, returns, refunds, damaged products and other support requests. Finding the correct policy or reaching the right support process can take time."),
("3. Proposed Solution",
"Voxora AI provides a chat interface connected to a searchable knowledge base. It also includes order lookup utilities with verification checks and a support-ticket creation utility."),
("4. Key Features",
"• Knowledge-base retrieval from Markdown documents.<br/>• Customer chat API and health endpoint.<br/>• Order lookup with verification requirements.<br/>• Support-ticket creation utility.<br/>• Practice-question dataset and retrieval smoke tests.<br/>• Voice API endpoints prepared for speech integration."),
("5. Technology Stack",
"Python, Flask, retrieval-based search, CSV datasets, Markdown knowledge documents, and the Gnani speech SDK integration."),
("6. Testing and Results",
"Dataset validation passed for 9 CSV files and 21 knowledge-base documents. The dataset includes 1,000 orders, 1,783 order items, 244 support logs, 52 practice questions and 23 practice conversations. Core imports, Flask health API, chat API and five RAG smoke-test queries passed. All 52 practice questions returned HTTP 200 responses. This confirms API response availability only; answer accuracy was not scored."),
("7. Limitations",
"Live Gnani TTS testing returned HTTP 401 INVALID_API_KEY, so successful voice operation is not verified. Batch audio processing was not tested because no audio samples were available. LLM-based conversational responses require valid configured credentials. Retrieval relevance needs further evaluation."),
("8. Future Enhancements",
"Validate speech credentials and complete live STT/TTS testing; improve retrieval relevance; conduct human-reviewed answer accuracy evaluation; add automated regression tests; and test batch audio processing."),
("9. Conclusion",
"Voxora AI demonstrates a modular customer-support prototype combining knowledge retrieval, chat APIs, verification-aware order lookup and support-ticket utilities. Further validation is required before production use.")
]

for heading, body in sections:
    story.append(Paragraph(escape(heading), styles["Section"]))
    story.append(Paragraph(body, styles["SmallBody"]))

story.append(Spacer(1, 8))
story.append(Paragraph("Prepared for capstone project submission | 01 November 2026",
    styles["Italic"]))

doc.build(story)
print("PDF created:", out.resolve())
