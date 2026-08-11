class CustomAsserts:
    @staticmethod
    def compare_table_data(expected_data: list, actual_data: list) -> dict:
        """
        So sánh dữ liệu bảng giữa Expected và Actual.
        Trả về kết quả chi tiết phân loại 3 trạng thái: mismatch, missing, unexpected.
        """
        mismatch = []
        missing = []
        unexpected = []
        
        # Kiểm tra phần tử thiếu hoặc khác biệt
        for idx, exp_item in enumerate(expected_data):
            if idx < len(actual_data):
                act_item = actual_data[idx]
                if exp_item != act_item:
                    mismatch.append({"index": idx, "expected": exp_item, "actual": act_item})
            else:
                missing.append({"index": idx, "expected": exp_item})
                
        # Kiểm tra phần tử thừa xuất hiện ngoài ý muốn
        if len(actual_data) > len(expected_data):
            for idx in range(len(expected_data), len(actual_data)):
                unexpected.append({"index": idx, "actual": actual_data[idx]})
                
        is_passed = (len(mismatch) == 0 and len(missing) == 0 and len(unexpected) == 0)
        
        return {
            "passed": is_passed,
            "mismatch": mismatch,
            "missing": missing,
            "unexpected": unexpected
        }