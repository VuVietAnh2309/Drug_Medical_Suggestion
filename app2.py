import os
import ast
import streamlit as st
from pymongo import MongoClient
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv

# --------------------- Configuration --------------------- #
# Set OpenAI API Key
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# --------------------- Database Connection --------------------- #
# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["thuoc_database"]
thuoc_collection = db["thuoc_collection"]

# --------------------- LLM Engine Setup --------------------- #
# Initialize GPT Query Engine (cached to run only once)
@st.cache_resource
def get_query_engine():
    """
    Load and initialize the LlamaIndex query engine with OpenAI LLM.
    Returns a pre-configured query engine for generating prescription recommendations.
    """
    storage_context = StorageContext.from_defaults(persist_dir="./index")
    index = load_index_from_storage(storage_context)
    return index.as_query_engine(llm=OpenAI(temperature=0.3, model="gpt-4o-mini"))

# Initialize the query engine
query_engine = get_query_engine()

# --------------------- Helper Functions --------------------- #
def format_prescription_list(toa_thuoc):
    """
    Format prescription data for display.
    
    Args:
        toa_thuoc: Raw prescription data (list or string)
        
    Returns:
        List of formatted prescription items
    """
    # Convert string representation of list to actual list if needed
    if isinstance(toa_thuoc, str):
        try:
            toa_thuoc = ast.literal_eval(toa_thuoc)
        except:
            toa_thuoc = [toa_thuoc]
    
    # Ensure the data is in list format
    if not isinstance(toa_thuoc, list):
        toa_thuoc = [str(toa_thuoc)]
    
    # Return only non-empty items
    return [item.strip() for item in toa_thuoc if item and item.strip()]

def create_gpt_prompt(user_data):
    """
    Create a well-structured prompt for GPT based on user input.
    
    Args:
        user_data: Dictionary containing patient information
        
    Returns:
        Formatted prompt string for GPT
    """
    return f"""
    Bạn là AI hỗ trợ tư vấn đơn thuốc phù hợp cho bệnh nhân. Dựa trên thông tin bệnh nhân sau, hãy kê đơn thuốc đầy đủ:

    - Giới tính: {user_data['GIOITINH']}
    - Tuổi: {user_data['TUOI']}
    - Tỉnh: {user_data['TENTINHTHANH']}
    - Mã ICD: {user_data['MAICD']}

    Yêu cầu:
    1. Đơn thuốc gồm các loại thuốc (2-5 loại thuốc) liên quan trực tiếp đến điều trị bệnh theo mã ICD đã cung cấp.
    2. Không kê các thuốc cho các bệnh lý khác nếu không có thông tin liên quan đến chúng.
    3. Ưu tiên các thuốc phổ biến, được tìm thấy trong tài liệu và phù hợp với độ tuổi và giới tính của bệnh nhân.
    4. Trình bày mỗi thuốc theo định dạng:
    Tên thuốc - Hàm lượng - Dạng - Số lượng yêu cầu
    5. Không cần giải thích gì thêm, chỉ trả về danh sách thuốc theo đúng định dạng trên.
    """

# --------------------- Streamlit UI --------------------- #
def main():
    """Main application function that sets up the Streamlit UI and handles user interactions."""
    # App title and description
    st.title("💊 Tư vấn đơn thuốc theo mã ICD")
    st.write("Điền thông tin bệnh nhân để hệ thống đề xuất đơn thuốc phù hợp.")
    
    # User input form
    with st.container():
        gioitinh = st.selectbox("Giới tính", ["Nam", "Nữ"])
        tuoi = st.number_input("Tuổi", min_value=0, max_value=120, value=50)
        tinh = st.text_input("Tỉnh/Thành phố", "Hồ Chí Minh")
        ma_icd = st.text_input("Mã ICD", "I10")
    
    # Process when button is clicked
    if st.button("📋 Lấy đơn thuốc"):
        # Prepare user info
        user_info = {
            "GIOITINH": gioitinh,
            "TUOI": int(tuoi),
            "TENTINHTHANH": tinh,
            "MAICD": ma_icd.strip().upper()
        }
        
        # Query MongoDB first
        mongo_result = get_prescription_from_db(user_info)
        
        # If not found in MongoDB, use GPT
        if not mongo_result:
            get_prescription_from_gpt(user_info)

def get_prescription_from_db(user_info):
    """
    Retrieve prescription from MongoDB based on user information.
    
    Args:
        user_info: Dictionary containing patient information
        
    Returns:
        Boolean indicating if a prescription was found
    """
    result = thuoc_collection.find_one(user_info)
    
    if result:
        st.success("✅ Đã tìm thấy đơn thuốc từ database!")
        st.markdown("### Đơn thuốc:")
        
        # Get and format prescription
        toa_thuoc = result.get("TOATHUOCCHIDINH", [])
        formatted_items = format_prescription_list(toa_thuoc)
        
        # Display each item
        for item in formatted_items:
            st.markdown(f"- {item}")
        return True
    
    return False

def get_prescription_from_gpt(user_info):
    """
    Generate prescription using GPT based on user information.
    
    Args:
        user_info: Dictionary containing patient information
    """
    st.warning("❌ Không tìm thấy trong MongoDB. Đang truy vấn GPT...")
    
    # Create prompt and query GPT
    prompt = create_gpt_prompt(user_info)
    
    with st.spinner("🔎 Đang truy vấn GPT..."):
        response = query_engine.query(prompt)
        
        st.success("✅ Đơn thuốc từ GPT:")
        
        # Process and display response
        try:
            # Try to handle as a list
            response_list = ast.literal_eval(str(response))
            if isinstance(response_list, list):
                for item in response_list:
                    st.markdown(f"- {item}")
            else:
                raise ValueError("Không phải list, xử lý như văn bản thường.")
        except:
            # Handle as regular text
            for line in str(response).split("\n"):
                if line.strip():
                    st.markdown(f"- {line.strip()}")

# Run the application
if __name__ == "__main__":
    main()