import streamlit as st
from openai import OpenAI
from pypdf import PdfReader
import io

client = OpenAI(
    api_key=st.secrets["DEEPSEEK_API_KEY"],
    base_url="https://api.deepseek.com"
)

st.title("📄 DocuBot")
st.caption("Upload a PDF or text file. Ask questions. Get answers.")

# File uploader
uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt"])

# Initialize document text
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""
    st.session_state.chat_history = []

# Process uploaded file
if uploaded_file is not None:
    # Check file type
    if uploaded_file.name.endswith(".pdf"):
        # Read PDF
        pdf_reader = PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        st.session_state.doc_text = text
        st.success(f"Loaded PDF with {len(pdf_reader.pages)} pages")
    
    elif uploaded_file.name.endswith(".txt"):
        # Read text file
        text = uploaded_file.read().decode("utf-8")
        st.session_state.doc_text = text
        st.success("Loaded text file")
    
    else:
        st.error("Unsupported file type")

# Show preview of document
if st.session_state.doc_text:
    with st.expander("Preview document text"):
        st.text(st.session_state.doc_text[:2000])  # Show first 2000 characters

# Q&A section
if st.session_state.doc_text:
    st.markdown("---")
    st.subheader("Ask a question about the document")
    
    user_question = st.text_input("Your question:")
    
    if st.button("Get Answer") and user_question:
        with st.spinner("Reading document..."):
            # Send document + question to DeepSeek
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "You are DocuBot. Answer questions ONLY based on the document provided. If the answer is not in the document, say: 'The document does not contain information about that.' Do not make anything up."
                    },
                    {
                        "role": "user",
                        "content": f"DOCUMENT:\n{st.session_state.doc_text}\n\nQUESTION:\n{user_question}"
                    }
                ],
                temperature=0.3
            )
            
            answer = response.choices[0].message.content
            st.write(answer)
            
            # Save to history
            st.session_state.chat_history.append({"question": user_question, "answer": answer})

# Show chat history
if st.session_state.chat_history:
    st.markdown("---")
    st.subheader("History")
    for entry in reversed(st.session_state.chat_history):
        st.markdown(f"**Q:** {entry['question']}")
        st.markdown(f"**A:** {entry['answer']}")
        st.markdown("---")