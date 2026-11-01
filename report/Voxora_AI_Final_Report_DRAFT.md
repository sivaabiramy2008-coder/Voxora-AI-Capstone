# Voxora AI - Capstone Project Report

## Overview
Voxora AI is a customer-support assistant prototype for the fictional ZentroMart store. It combines a Flask web application, a Markdown knowledge base, retrieval-based responses, order lookup and support-ticket utilities.

## Main capabilities
- Retrieval of relevant customer-support knowledge-base sections.
- Order lookup with verification checks.
- Support-ticket creation utility.
- Flask API endpoints for chat, health checks and voice workflows.
- Practice-question dataset included with the project.

## Technology
Python, Flask, retrieval-based search, CSV datasets, Markdown knowledge documents, and optional Gnani speech services.

## Testing and limitations
See `sample_outputs/final_test_results.txt` for the checks actually run. Gnani voice functionality must be considered unverified unless a valid API key passes a live request. LLM responses require configured credentials. Retrieval quality should be reviewed against the saved evaluation questions.

## Conclusion
Voxora AI demonstrates a modular customer-support workflow with knowledge retrieval and verification-aware support utilities. Further work includes improving retrieval relevance, validating live speech services, and completing automated evaluation.
