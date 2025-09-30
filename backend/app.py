# /backend/app.py

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import Pinecone
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")

# Basic environment validation
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set. Please add it to your .env file.")
if not PINECONE_API_KEY:
    print("[WARN] PINECONE_API_KEY is not set. Pinecone operations may fail.", flush=True)

# --- CONFIGURE THE DATABASE ---
INDEX_NAME = os.getenv("ACTIVE_INDEX", "pyos-index")
# ------------------------------

# Initialize Flask App and CORS
app = Flask(__name__)
CORS(app)

# Simple in-memory active index name; initialized from env
active_index = INDEX_NAME


@app.get('/health')
def health():
    return jsonify({"status": "ok", "active_index": active_index})


@app.get('/indexes')
def list_indexes():
    try:
        from pinecone import Pinecone as Pc
        pc = Pc(api_key=PINECONE_API_KEY)
        names = pc.list_indexes().names()
        return jsonify({"indexes": names, "active": active_index})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post('/set-index')
def set_index():
    global active_index
    data = request.get_json(force=True, silent=True) or {}
    name = data.get('index')
    if not name:
        return jsonify({"error": "'index' is required"}), 400
    active_index = name
    try:
        load_retriever()
        return jsonify({"message": f"Active index set to '{name}'"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.post('/create-index')
def create_index():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        name = payload.get('name')
        dim = int(payload.get('dimension') or 768)
        metric = (payload.get('metric') or 'cosine')
        if not name:
            return jsonify({"error": "'name' is required"}), 400
        from pinecone import Pinecone as Pc, ServerlessSpec
        pc = Pc(api_key=PINECONE_API_KEY)
        if name in pc.list_indexes().names():
            return jsonify({"message": f"Index '{name}' already exists"})
        pc.create_index(name=name, dimension=dim, metric=metric,
                        spec=ServerlessSpec(cloud='aws', region=os.getenv('PINECONE_ENVIRONMENT') or 'us-east-1'))
        return jsonify({"message": f"Index '{name}' created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.get('/documents')
def list_documents():
    docs_dir = os.path.join(os.path.dirname(__file__), 'documents')
    try:
        files = [f for f in os.listdir(docs_dir) if f.lower().endswith('.txt')]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post('/upload')
def upload_documents():
    docs_dir = os.path.join(os.path.dirname(__file__), 'documents')
    os.makedirs(docs_dir, exist=True)
    files = request.files.getlist('files')
    if not files:
        return jsonify({"error": "No files provided"}), 400
    saved = []
    for file in files:
        fname = file.filename
        if not fname.lower().endswith('.txt'):
            continue
        path = os.path.join(docs_dir, os.path.basename(fname))
        file.save(path)
        saved.append(os.path.basename(fname))
    return jsonify({"message": f"Uploaded {len(saved)} files", "saved": saved})


@app.post('/ingest')
def trigger_ingest():
    try:
        # Run the ingest_api.main within same process to keep deps simple
        os.environ["ACTIVE_INDEX"] = active_index
        from ingest_api import main as ingest_main
        ingest_main()
        return jsonify({"message": "Ingestion completed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post('/set-keys')
def set_keys():
    payload = request.get_json(force=True, silent=True) or {}
    # For security, we won't persist to disk; just allow setting for current process
    new_anthropic = payload.get('ANTHROPIC_API_KEY')
    global llm
    try:
        if new_anthropic:
            os.environ['ANTHROPIC_API_KEY'] = new_anthropic
            # Recreate LLM with new key
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(model="claude-3-5-sonnet-latest", api_key=new_anthropic)
        return jsonify({"message": "Keys updated for current session"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Initialize LLM and Embeddings
llm = ChatAnthropic(model="claude-3-5-sonnet-latest", api_key=anthropic_api_key)
# This model produces 768-dimensional vectors
model_name = "sentence-transformers/all-mpnet-base-v2"
embeddings = HuggingFaceEmbeddings(model_name=model_name)

# Function to (re)load Pinecone retriever for current active index
retriever = None


def load_retriever():
    global retriever
    print(f"Loading vector store from Pinecone index '{active_index}'...")
    try:
        vs = Pinecone.from_existing_index(index_name=active_index, embedding=embeddings)
        retriever = vs.as_retriever()
        print("Vector store loaded successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to load Pinecone index '{active_index}': {e}")
        raise


load_retriever()

# --- MODIFIED PROMPT TEMPLATE ---
prompt_template = """
# ROLE: PsyOS Team Lead Persona

You are the **PsyOS Team Lead**, a world-class Senior Technical Architect and Project Manager. Your sole mission is to guide the development and implementation of the PsyOS platform. Your entire knowledge base comes from the **`PsyOS Project Bible`** (the document provided as context). You must ground every response, analysis, and piece of code in the specifications found within that document. You are a leader, not just a search index. Your goal is to transform retrieved information into actionable strategy, improved architecture, and production-ready code.

---
### CORE DIRECTIVES

1.  **Analyze, Don't Just Recite**: When a user asks a question, never simply quote the document. First, summarize the relevant information, then provide a **"Team Lead's Analysis"**. This analysis should include insights, potential challenges, strategic advice, or areas for improvement.
2.  **Architect and Improve**: You are an expert architect. When asked about any system or module, you must be able to critique the existing design and propose a **"Revised Architecture"**. Justify your proposed changes based on principles like scalability, security, maintainability, and efficiency.
3.  **Code with Excellence**: You are a polyglot programmer, fluent in **Python, JavaScript, and Go**. When asked to generate code, you must produce clean, well-commented, and robust code that directly implements the specifications from the document.
4.  **Adopt a Leadership Tone**: Your communication style is authoritative, clear, and collaborative. Use phrases like "Let's review...", "Our goal here is...", "I recommend we approach this by...", and "Good question, this ties into...". You are guiding a team to success.

---
### QUERY ANALYSIS & RESPONSE STRATEGY

Before answering, first determine the nature of the user's request:

1.  **Project-Specific Question**: Is the user asking about a concept, architecture, workflow, or term that is proprietary to or specifically defined by the `PsyOS Project Bible`? (e.g., "What is a Patient Kernel?", "Tell me about the MCP Server", "What is PsyOS?").
    * **Response Strategy**: For these questions, your answer **MUST BE BASED STRICTLY AND EXCLUSIVELY** on the provided **CONTEXT**. Synthesize information from the context to form a comprehensive answer. Do not introduce external knowledge. If the context is insufficient, state that the project bible does not provide enough detail on that specific topic.

2.  **General Knowledge Question**: Is the user asking for a definition of a general industry term or technology that is mentioned in the `PsyOS Project Bible` but not defined by it? (e.g., "What is HIPAA?", "What is a vector database?", "What is a healthcare system?").
    * **Response Strategy**: For these questions, provide a clear, general definition using your own expert knowledge. Then, **use the provided CONTEXT to explain the term's relevance *to the PsyOS project***. For example, after defining HIPAA, you should explain how PsyOS adheres to it based on the document's compliance section.

---
### TASK EXECUTION

Now, analyze the user's request, apply the correct response strategy, and use the provided context to formulate your answer.

**CONTEXT:**
{context}

**USER REQUEST:**
{question}

**YOUR RESPONSE AS TEAM LEAD:**
"""

prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])


@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "Invalid request. 'query' is required."}), 400

        user_query = data['query'].strip()

        # Validate query input
        if not user_query:
            return jsonify({"error": "Query cannot be empty."}), 400

        if len(user_query) > 1000:
            return jsonify({"error": "Query is too long. Maximum 1000 characters allowed."}), 400

        retrieved_docs = retriever.get_relevant_documents(user_query)
        context = "\n\n".join([doc.page_content for doc in retrieved_docs])

        if not context:
            # If no context is found, we can still attempt a general knowledge answer.
            # We'll create a minimal context that lets the LLM know nothing was found.
            context = "No specific information was found in the PsyOS Project Bible regarding this topic."

        formatted_prompt = prompt.format(context=context, question=user_query)

        # Call the LLM safely; different versions may return string or a message object
        llm_response = llm.invoke(formatted_prompt) if hasattr(llm, "invoke") else llm(formatted_prompt)
        response_text = getattr(llm_response, "content", None) or (
            llm_response if isinstance(llm_response, str) else str(llm_response))

        return jsonify({"response": response_text})
    except Exception as error:
        print(f"An error occurred: {error}")
        return jsonify({"error": "An internal server error occurred."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)