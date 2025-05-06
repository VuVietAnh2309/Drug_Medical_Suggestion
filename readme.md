# Bài toán gợi ý thuốc sử dụng AI

## Bài toán

*Update từ readme cũ*

## Dữ liệu
1. Dữ liệu lưu trữ trong DB
- Các file excel (đã được xử lý đầu ra cho các đơn thuốc hợp nhất thành một - đã tiền xử lý)

2. Dữ liệu cho GPT embeddings 
- Dữ liệu dạng structure data (nên ở dạng json) => để tự format sang text theo hàm thì tốt hơn là mình tự chuyển sang text
- Ví dụ:

```
[
    {
        "Thông tin bệnh nhân": "Nữ, 75 tuổi, Hồ Chí Minh, mã bệnh: I10",
        "Đơn thuốc chỉ định": [
            "Lacisartan HCT 100/12.5 - Hàm lượng: 100mg + 12,5mg - Dạng: Viên - Số lượng yêu cầu: 28.0",
            "Amdepin Duo - Hàm lượng: 5mg + 10mg - Dạng: Viên - Số lượng yêu cầu: 28.0"
        ]
    },
    {
        "Thông tin bệnh nhân": "Nam, 57 tuổi, Hồ Chí Minh, mã bệnh: E11",
        "Đơn thuốc chỉ định": [
            "Diamicron MR 60mg - Hàm lượng: 60mg - Dạng: Viên - Số lượng yêu cầu: 28.0",
            "Kavasdin 5 - Hàm lượng: 5mg - Dạng: Viên - Số lượng yêu cầu: 56.0",
            "Stradiras 50/850 - Hàm lượng: 50mg; 850mg - Dạng: Viên - Số lượng yêu cầu: 28.0",
            "Glumeform 850 - Hàm lượng: 850mg - Dạng: Viên - Số lượng yêu cầu: 28.0",
            "Bivitanpo 50 - Hàm lượng: 50mg - Dạng: Viên - Số lượng yêu cầu: 28.0",
            "Lipotatin 20mg - Hàm lượng: 20mg - Dạng: Viên - Số lượng yêu cầu: 28.0"
        ]
    },
]
```

## Cách cài đặt 
### Chuẩn bị dữ liệu *private data*

**Bước 1: Khởi tạo cơ sở dữ liệu MongoDB**
Chạy file mongodb.py để nạp dữ liệu từ file Excel vào MongoDB:

```bash
python mongodb_ver2.py
```

File này sẽ:

- Kết nối tới MongoDB trên localhost:27017
- Tạo database "thuoc_database" và collection "thuoc_collection"
- Nạp dữ liệu từ file "data/data_preprocess.xlsx"

**Bước 2: Xây dựng chỉ mục LlamaIndex**
Chạy file build_llama_index.py để tạo vector index cho LLM:

```bash
python build_llama_index_ver2.py
```

File này sẽ:

- Đọc dữ liệu từ file "data/data_small.json" (file nhỏ của data gốc, lượng dữ liệu khoảng 5% so với data gốc) => giảm thiểu chi phí embeddings trong quá trình test
- Chuyển đổi thành Document objects
- Tạo và lưu chỉ mục vector vào thư mục "./index"

**Bước 3: Chạy ứng dụng Streamlit**
Cuối cùng, chạy file app.py để khởi động giao diện người dùng:

```bash
streamlit run app2.py
```

Ứng dụng Streamlit sẽ:

- Tải chỉ mục vector từ thư mục "./index"
- Kết nối tới MongoDB
- Hiển thị giao diện người dùng để nhập thông tin bệnh nhân và lấy đơn thuốc


## Luồng xử lý
1. Người dùng nhập thông tin bệnh nhân.

2. Tạo user_info từ dữ liệu nhập.

3. Truy vấn MongoDB (thuoc_collection) với user_info:
- Nếu có đơn thuốc: 
    - Hiển thị danh sách thuốc từ DB (được chuẩn hóa).
- Nếu không có đơn thuốc:
    - Chuyển sang truy vấn GPT.

4. Truy vấn GPT (sử dụng LlamaIndex + OpenAI gpt-4o-mini):

5. Các xử lý phụ trợ:
- format_prescription_list: Chuẩn hóa đầu ra đơn thuốc.
- create_gpt_prompt: Sinh prompt rõ ràng, có yêu cầu định dạng cụ thể cho GPT.

*note:  Code logic luồng được viết trong file logic_response.py*


