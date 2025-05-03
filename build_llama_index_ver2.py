"""
Build LlamaIndex from patient and prescription data.

This script loads medical prescription data from a JSON file,
converts it to Document objects, and creates a searchable
vector index using LlamaIndex.
"""

import os
import json
from llama_index.core import VectorStoreIndex, Document
from llama_index.embeddings.openai import OpenAIEmbedding

# --------------------- Configuration --------------------- #
# Set OpenAI API Key 
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# --------------------- Data Loading --------------------- #
def load_prescription_data(file_path):
    """
    Load prescription data from JSON file.
    
    Args:
        file_path: Path to the JSON data file
        
    Returns:
        List of Document objects ready for indexing
    """
    print(f"Loading data from {file_path}...")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        documents = []
        for entry in data:
            # Extract patient information and prescriptions
            info = entry["Thông tin bệnh nhân"]
            thuoc = "\n".join(entry["Đơn thuốc chỉ định"])
            
            # Format data for indexing
            full_text = f"Thông tin bệnh nhân: {info}\nĐơn thuốc chỉ định:\n{thuoc}"
            documents.append(Document(text=full_text))
            
        print(f"Successfully processed {len(documents)} documents.")
        return documents
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

# --------------------- Index Creation --------------------- #
def build_and_save_index(documents, output_dir="./index"):
    """
    Create and save vector index from documents.
    
    Args:
        documents: List of Document objects
        output_dir: Directory to save the index
    """
    if not documents:
        print("No documents to index. Exiting.")
        return
        
    print(f"Building index with {len(documents)} documents...")
    
    # Initialize and build index
    index = VectorStoreIndex.from_documents(documents)
    
    # Save index to disk
    index.storage_context.persist(persist_dir=output_dir)
    
    print(f"✅ Index successfully created and saved to '{output_dir}'")

# --------------------- Main Function --------------------- #
def main():
    """Main function to execute the indexing process."""
    # Define input file path
    input_file = "data/data_small.json"
    output_dir = "./index"
    
    # Load documents
    documents = load_prescription_data(input_file)
    
    # Build and save index
    build_and_save_index(documents, output_dir)

if __name__ == "__main__":
    main()