import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import io

client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

st.title("📄 DocuBot")
st.caption("Upload a document. Ask questions. Get answers from the document.")

# Initialize session state
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# File uploader
uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt"])

# Process uploaded file
if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        st.session_state.doc_text = text
        st.success(f"Loaded PDF with {len(pdf_reader.pages)} pages")
    
    elif uploaded_file.name.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8")
        st.session_state.doc_text = text
        st.success("Loaded text file")
    
    else:
        st.error("Unsupported file type")

# Show document preview
if st.session_state.doc_text:
    with st.expander("Preview document"):
        st.text_area("Document text", st.session_state.doc_text, height=300)

# Chat interface
if st.session_state.doc_text:
    st.markdown("---")
    st.subheader("Ask questions about the document")
    
    # Display chat history
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(chat["question"])
        with st.chat_message("assistant"):
            st.write(chat["answer"])
    
    # User input
    user_question = st.chat_input("Your question:")
    
    if user_question:
        # Add question to history
        st.session_state.chat_history.append({"question": user_question, "answer": ""})
        
        # Build messages with history
        system_prompt = """You are DocuBot. Answer questions ONLY based on the document provided.
        If the answer is not in the document, say: 'The document does not contain information about that.'
        Do not make anything up. Be concise and direct. If the user asks a follow-up question,
        use the previous conversation context to understand what they're referring to."""
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.append({"role": "user", "content": f"DOCUMENT:\n{st.session_state.doc_text[:50000]}"})
        
        # Add chat history for context (last 5 exchanges)
        for chat in st.session_state.chat_history[-5:]:
            if chat["answer"]:
                messages.append({"role": "user", "content": chat["question"]})
                messages.append({"role": "assistant", "content": chat["answer"]})
        
        # Add current question
        messages.append({"role": "user", "content": user_question})
        
        # Get AI response
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.3
        )
        answer = response.choices[0].message.content
        
        # Update chat history with answer
        st.session_state.chat_history[-1]["answer"] = answer
        
        # Now display the full chat history including the latest
        for chat in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(chat["question"])
            with st.chat_message("assistant"):
                st.write(chat["answer"])