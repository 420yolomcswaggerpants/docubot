# DocuBot

A Retrieval-Augmented Generation (RAG) app that answers questions about uploaded documents.

## Live Demo
https://docubot-420yolomcswaggerpants.streamlit.app

## What It Does
- Accepts PDF or TXT file uploads
- Extracts text from the document
- Answers questions based only on the document content
- Remembers conversation context for follow-up questions

## Features
- PDF and TXT support
- Document preview
- Chat-based Q&A interface
- Conversation history
- Strict grounding (only answers from the document)

## Tech Stack
- Python
- Streamlit
- DeepSeek API
- pypdf

## How It Works
1. User uploads a document
2. Text is extracted using pypdf (for PDFs) or direct read (for TXT)
3. User asks a question
4. The full document text is sent to DeepSeek with the question
5. The AI answers based only on the document

## Design Decisions
- Started with chunking and keyword search
- Found that full-document inference worked better for accuracy
- Prioritized correctness over speed for proof of concept

## Setup
1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Add your DeepSeek API key to `.streamlit/secrets.toml`
4. Run: `streamlit run app.py`

## Skills Demonstrated
- RAG architecture
- Document processing
- Prompt engineering
- Session state management
- Deployment
