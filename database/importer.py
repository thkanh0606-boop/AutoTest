import pandas as pd
import json
import os
from database.engine import SessionLocal
from database.models import Suite, TestCase, TestStep, Page

# --- PHẦN 1: TẠO DỮ LIỆU MẪU ĐỂ TEST (Đạt KPI 25 TCs, 2 Suites) ---
def generate_sample_files():
    data = []
    # Suite 1: Luồng Đặt Xe (13 Test Cases)
    for i in range(1, 14):
        data.append({
            "Suite": "Suite Đặt Xe Chuyên Sâu",
            "TC_Name": f"TC_DX_{i:02d} - Kiểm tra quy trình đặt xe {i}",
            "Description": f"Xác minh luồng đặt xe cơ bản số {i}",
            "Step_Order": 1,
            "Action": "Access the website. Chọn xe và điền thông tin.",
            "Expected": "Thông tin được ghi nhận chính xác."
        })
    
    # Suite 2: Luồng Quản Lý Xe (12 Test Cases) -> Tổng 25 TCs
    for i in range(14, 26):
        data.append({
            "Suite": "Suite Quản Lý Đội Xe",
            "TC_Name": f"TC_QLX_{i:02d} - Kiểm tra cập nhật trạng thái xe {i}",
            "Description": f"Xác minh việc thay đổi trạng thái xe {i}",
            "Step_Order": 1,
            "Action": "Access the website. Cập nhật trạng thái bảo dưỡng.",
            "Expected": "Hệ thống lưu trạng thái thành công."
        })

    df = pd.DataFrame(data)
    
    # Xuất ra 3 định dạng
    df.iloc[:10].to_csv("sample_data.csv", index=False) # 10 dòng đầu ra CSV
    df.iloc[10:20].to_excel("sample_data.xlsx", index=False) # 10 dòng tiếp ra Excel
    
    # 5 dòng cuối ra JSON theo cấu trúc list of dicts
    json_data = df.iloc[20:].to_dict(orient="records")
    with open("sample_data.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=4)
        
    print("Đã tạo thành công 3 file mẫu: sample_data.csv, sample_data.xlsx, sample_data.json")

# --- PHẦN 2: LOGIC IMPORT VÀ MAPPING ---
def import_to_db(file_path, file_type):
    db = SessionLocal()
    
    try:
        # 1. Đọc dữ liệu tùy theo định dạng
        if file_type == "csv":
            df = pd.read_csv(file_path)
        elif file_type == "excel":
            df = pd.read_excel(file_path)
        elif file_type == "json":
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
            df = pd.DataFrame(json_data)
        else:
            print("Định dạng không được hỗ trợ!")
            return

        # 2. Mapping và Lưu dữ liệu (Lấy Page mặc định ID = 3)
        default_page = db.query(Page).filter(Page.id == 3).first()
        if not default_page:
            print("Lỗi: Không tìm thấy Page ID=3. Vui lòng chạy seed_data.py trước.")
            return

        for index, row in df.iterrows():
            # Xử lý Suite
            suite_name = str(row['Suite'])
            suite = db.query(Suite).filter(Suite.name == suite_name).first()
            if not suite:
                suite = Suite(name=suite_name)
                db.add(suite)
                db.commit()
                db.refresh(suite)

            # Xử lý TestCase
            tc_name = str(row['TC_Name'])
            tc = db.query(TestCase).filter(TestCase.name == tc_name).first()
            if not tc:
                tc = TestCase(
                    page_id=default_page.id, 
                    name=tc_name, 
                    description=str(row['Description'])
                )
                db.add(tc)
                db.commit()
                db.refresh(tc)

            # Xử lý TestStep
            step = TestStep(
                testcase_id=tc.id,
                step_order=int(row['Step_Order']),
                action=str(row['Action']),
                expected_result=str(row['Expected'])
            )
            db.add(step)
            db.commit()

        print(f"✅ Import thành công từ file {file_path} ({file_type.upper()})")

    except Exception as e:
        print(f"❌ Lỗi khi import file {file_path}: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Bắt đầu xử lý task T5...")
    # Tạo file mẫu để có đủ 25 Test Cases & 2 Suites
    generate_sample_files()
    
    # Chạy hàm import cho cả 3 định dạng
    import_to_db("sample_data.csv", "csv")
    import_to_db("sample_data.xlsx", "excel")
    import_to_db("sample_data.json", "json")
    
    # Xóa file tạm sau khi import xong để dự án luôn sạch sẽ
    os.remove("sample_data.csv")
    os.remove("sample_data.xlsx")
    os.remove("sample_data.json")
    print("Đã dọn dẹp các file tạm. KPI T5 hoàn tất!")