import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import io

def chunk_text(text, chunk_size=1000, overlap=100):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks

def find_relevant_chunks(chunks, question):
    """Find chunks that contain words from the question."""
    # Extract capitalized words (likely names)
    names = [word for word in question.split() if word[0].isupper()]
    
    # First pass: look for chunks containing any capitalized names
    if names:
        name_chunks = []
        for i, chunk in enumerate(chunks):
            for name in names:
                if name.lower() in chunk.lower():
                    name_chunks.append(chunk)
                    break
        if name_chunks:
            return name_chunks[:15]
    
    # Second pass: word matching
    question_words = set(question.lower().split())
    scored_chunks = []
    
    for i, chunk in enumerate(chunks):
        chunk_lower = chunk.lower()
        score = 0
        for word in question_words:
            if word in chunk_lower:
                score += 1
            elif len(word) > 3:
                for chunk_word in chunk_lower.split():
                    if word in chunk_word or chunk_word in word:
                        score += 0.5
        if score > 0:
            scored_chunks.append((score, i, chunk))
    
    scored_chunks.sort(reverse=True, key=lambda x: x[0])
    return [chunk for _, _, chunk in scored_chunks[:15]]

def get_document_summary(text):
    """Get a summary of the document."""
    chunks = chunk_text(text, chunk_size=3000, overlap=200)
    first_chunks = chunks[:5]  # Use first 5 chunks as sample
    
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "Summarize the following text in 500 words or less. Focus on main characters, key events, and important facts."},
            {"role": "user", "content": " ".join(first_chunks)}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

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
        st.text(st.session_state.doc_text[:2000])

# Chat interface
if st.session_state.doc_text:
    st.markdown("---")
    st.subheader("Ask questions about the document")
    
    # User input
    user_question = st.chat_input("Your question:")
    
    if user_question:
        # Add question to history
        st.session_state.chat_history.append({"question": user_question, "answer": ""})
        
        # Build messages with history
        system_prompt = """You are DocuBot. Answer questions based on the document excerpts provided.
        Read the excerpts carefully and infer answers from context when the information is implied but not explicitly stated word-for-word.
        If the document genuinely does not contain any information related to the question, say: 'The document does not contain 
        information about that.' Do not make anything up. Be concise and direct. If the user asks a follow-up question,
        use the previous conversation context to understand what they're referring to."""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Send the document directly to the AI
        messages.append({"role": "user", "content": f"DOCUMENT:\n{st.session_state.doc_text}"})
        
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