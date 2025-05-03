# Bài toán gợi ý thuốc sử dụng AI

## Bài toán

## Cách cài đặt 
**Bước 1: Khởi tạo cơ sở dữ liệu MongoDB**
Chạy file mongodb.py để nạp dữ liệu từ file Excel vào MongoDB:

```bash
python mongodb.py
```

File này sẽ:

- Kết nối tới MongoDB trên localhost:27017
- Tạo database "thuoc_database" và collection "thuoc_collection"
- Nạp dữ liệu từ file "data/data_preprocess.xlsx"

**Bước 2: Xây dựng chỉ mục LlamaIndex**
Chạy file build_llama_index.py để tạo vector index cho LLM:

```bash
python build_llama_index.py
```

File này sẽ:

- Đọc dữ liệu từ file "data/data_small.json"
- Chuyển đổi thành Document objects
- Tạo và lưu chỉ mục vector vào thư mục "./index"

**Bước 3: Chạy ứng dụng Streamlit**
Cuối cùng, chạy file app.py để khởi động giao diện người dùng:

```bash
streamlit run app.py
```

Ứng dụng Streamlit sẽ:

- Tải chỉ mục vector từ thư mục "./index"
- Kết nối tới MongoDB
- Hiển thị giao diện người dùng để nhập thông tin bệnh nhân và lấy đơn thuốc

