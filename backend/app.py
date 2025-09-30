import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import functions from our new modular files
from chatbot import initialize_retriever, get_chat_response
from create_index import create_pinecone_index, list_pinecone_indexes
from data_ingest import process_and_embed_document
from create_index import delete_pinecone_index

# ==============================================================================
# 1. INITIAL SETUP & CONFIGURATION
# ==============================================================================
load_dotenv()
app = Flask(__name__)
CORS(app)

# --- Global Variables ---
# Default active index name, can be changed via API
active_index_name = os.getenv("ACTIVE_INDEX", "pyos-index")

# Global retriever object, initialized on startup
retriever = None


# ==============================================================================
# 2. CORE API ENDPOINTS
# ==============================================================================

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Main endpoint for interacting with the chatbot."""
    if not retriever:
        return jsonify({"error": "Chatbot is not ready. Please set a valid active index via /switch-db."}), 503

    try:
        data = request.json
        user_query = data.get('query', '').strip()
        if not user_query:
            return jsonify({"error": "Query cannot be empty."}), 400

        response_text = get_chat_response(user_query, retriever)
        return jsonify({"response": response_text, "index_used": active_index_name})
    except Exception as e:
        print(f"An error occurred during chat: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500


@app.route('/create-db', methods=['POST'])
def create_db_endpoint():
    """Endpoint to create a new Pinecone index."""
    try:
        payload = request.get_json()
        index_name = payload.get('name')
        if not index_name:
            return jsonify({"error": "'name' is required"}), 400

        message = create_pinecone_index(index_name)
        status_code = 201 if "created successfully" in message else 200
        return jsonify({"message": message}), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/list-dbs', methods=['GET'])
def list_dbs_endpoint():
    """Endpoint to list all available Pinecone indexes."""
    try:
        indexes = list_pinecone_indexes()
        return jsonify({"indexes": indexes, "active_index": active_index_name})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/switch-db', methods=['POST'])
def switch_db_endpoint():
    """Endpoint to switch the active index for the chatbot."""
    global retriever, active_index_name
    payload = request.get_json()
    index_name = payload.get('name')
    if not index_name:
        return jsonify({"error": "'name' is required"}), 400

    new_retriever = initialize_retriever(index_name)
    if new_retriever:
        retriever = new_retriever
        active_index_name = index_name
        return jsonify({"message": f"Active database switched to '{index_name}'."})
    else:
        return jsonify({"error": f"Could not connect to index '{index_name}'. Please ensure it exists."}), 404


@app.route('/delete-db', methods=['POST'])
def delete_db_endpoint():
    """Endpoint to delete a Pinecone index."""
    global retriever, active_index_name
    try:
        payload = request.get_json()
        index_name = payload.get('name')
        if not index_name:
            return jsonify({"error": "'name' is required"}), 400

        # Safety check: if deleting the active index, disconnect the retriever
        if index_name == active_index_name:
            retriever = None
            active_index_name = None
            print(f"Warning: Active index '{index_name}' is being deleted. Chatbot is now offline.")

        message, status_code = delete_pinecone_index(index_name)

        if status_code == 200 and not active_index_name:
            message += " Chatbot is now offline. Please switch to an existing database."

        return jsonify({"message": message}), status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/upload-data', methods=['POST'])
def upload_data_endpoint():
    """Endpoint to upload a document to a specified Pinecone index."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    # You can specify which index to upload to, otherwise it uses the active one
    index_name = request.form.get('index_name', active_index_name)

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not (file.filename.endswith('.txt') or file.filename.endswith('.md')):
        return jsonify({"error": "Invalid file type. Only .txt and .md are allowed."}), 400

    upload_folder = os.path.join(os.path.dirname(__file__), 'temp_uploads')
    os.makedirs(upload_folder, exist_ok=True)
    temp_path = os.path.join(upload_folder, file.filename)

    try:
        file.save(temp_path)
        message, status_code = process_and_embed_document(temp_path, index_name)
        return jsonify({"message": message}), status_code
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ==============================================================================
# 3. APPLICATION STARTUP
# ==============================================================================
if __name__ == '__main__':
    print("--- Starting Modular Backend Server ---")
    retriever = initialize_retriever(active_index_name)
    if not retriever:
        print(f"\nWARNING: Could not connect to default index '{active_index_name}'.")
        print("The /chat endpoint will not work until a valid index is set via /switch-db.")

    app.run(host='0.0.0.0', port=5000)

