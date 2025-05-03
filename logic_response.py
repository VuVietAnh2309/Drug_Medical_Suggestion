from mongodb import get_thuoc_from_mongo
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.llms.openai import OpenAI
import os

# Khởi tạo GPT engine
def get_query_engine():
    storage_context = StorageContext.from_defaults(persist_dir="./index")
    index = load_index_from_storage(storage_context)
    return index.as_query_engine(llm=OpenAI(temperature=0.3, model="gpt-4o-mini"))

query_engine = get_query_engine()

def search_toa_thuoc(user_info):
    # 1. Tìm trong MongoDB
    result = get_thuoc_from_mongo(user_info)

    if result:
        return {
            "source": "mongo",
            "data": result.get("TOATHUOCCHIDINH", [])
        }
    else:
        # 2. Truy vấn GPT nếu MongoDB không có
        prompt = f"""
        Bạn là AI hỗ trợ tư vấn đơn thuốc phù hợp cho bệnh nhân. Dựa trên thông tin bệnh nhân sau, hãy kê đơn thuốc đầy đủ:

        - Giới tính: {user_info['GIOITINH']}
        - Tuổi: {user_info['TUOI']}
        - Tỉnh: {user_info['TENTINHTHANH']}
        - Mã ICD: {user_info['MAICD']}

        Yêu cầu:
        1. Đơn thuốc gồm các loại thuốc (2-5 loại thuốc) liên quan trực tiếp đến điều trị bệnh theo mã ICD đã cung cấp.
        2. Không kê các thuốc cho các bệnh lý khác nếu không có thông tin liên quan đến chúng.
        3. Ưu tiên các thuốc phổ biến, được tìm thấy trong tài liệu và phù hợp với độ tuổi và giới tính của bệnh nhân.
        4. Trình bày mỗi thuốc theo định dạng:
        Tên thuốc - Hàm lượng - Dạng - Số lượng yêu cầu
        5. Không cần giải thích gì thêm, chỉ trả về danh sách thuốc theo đúng định dạng trên.
        """
        response = query_engine.query(prompt)
        lines = [line.strip() for line in str(response).split("\n") if line.strip()]
        return {
            "source": "gpt",
            "data": lines
        }
