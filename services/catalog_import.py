"""Linh - Thứ Năm: import dữ liệu Excel/CSV/JSON cho module Danh mục xe.

Chuẩn hoá mọi định dạng về cùng một danh sách dict:
    {"loai": "hang" | "mau", "ten": str, "hang": str, "trang_thai": str}

- "loai" = "hang"  -> dòng dữ liệu Hãng xe, "hang" để trống.
- "loai" = "mau"   -> dòng dữ liệu Mẫu xe, "hang" là tên hãng liên kết (bắt buộc).

File mẫu tham khảo: data/sample_import/danh_muc_xe_mau.csv|.json
"""

import json
from pathlib import Path

SUPPORTED_EXTENSIONS = {".csv", ".json", ".xlsx", ".xls"}
VALID_LOAI = {"hang", "mau"}

# Alias cột thường gặp khi người dùng tự đặt tên cột trong file của họ.
COLUMN_ALIASES = {
    "loai": {"loai", "loại", "type", "kind"},
    "ten": {"ten", "tên", "name", "ten_xe", "tenxe"},
    "hang": {"hang", "hãng", "brand", "hang_lien_ket", "hãng liên kết", "hangxe"},
    "trang_thai": {"trang_thai", "trạng thái", "status"},
}


class CatalogImportError(ValueError):
    pass


def _normalize_key(key):
    return str(key).strip().lower().replace(" ", "_")


def _map_row(raw_row):
    normalized = {}
    for raw_key, value in raw_row.items():
        key = _normalize_key(raw_key)
        for target, aliases in COLUMN_ALIASES.items():
            if key in aliases or key == target:
                normalized[target] = value
                break

    loai = str(normalized.get("loai", "")).strip().lower()
    ten = str(normalized.get("ten", "")).strip()
    hang = str(normalized.get("hang", "") or "").strip()
    trang_thai = str(normalized.get("trang_thai", "") or "").strip() or "Đang hoạt động"

    return {"loai": loai, "ten": ten, "hang": hang, "trang_thai": trang_thai}


def _read_csv(path):
    import csv

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def _read_json(path):
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    if isinstance(payload, dict):
        payload = payload.get("rows", payload.get("data", []))
    if not isinstance(payload, list):
        raise CatalogImportError("File JSON phải là danh sách hoặc có khoá 'rows'.")
    return payload


def _read_excel(path):
    try:
        import pandas as pd
    except ModuleNotFoundError as exc:
        raise CatalogImportError(
            "Chưa cài pandas/openpyxl. Chạy: pip install -r requirements.txt"
        ) from exc

    frame = pd.read_excel(path, dtype=str).fillna("")
    return frame.to_dict(orient="records")


def import_catalog_file(path):
    """Đọc file CSV/JSON/XLSX và trả về (rows, warnings)."""

    path = Path(path)
    if not path.exists():
        raise CatalogImportError(f"Không tìm thấy file: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise CatalogImportError(
            f"Định dạng '{ext}' không được hỗ trợ. Chỉ nhận .csv, .json, .xlsx"
        )

    if ext == ".csv":
        raw_rows = _read_csv(path)
    elif ext == ".json":
        raw_rows = _read_json(path)
    else:
        raw_rows = _read_excel(path)

    rows = []
    warnings = []
    for index, raw_row in enumerate(raw_rows, start=1):
        row = _map_row(raw_row)

        if row["loai"] not in VALID_LOAI:
            warnings.append(f"Dòng {index}: bỏ qua - 'loai' phải là 'hang' hoặc 'mau'.")
            continue
        if not row["ten"]:
            warnings.append(f"Dòng {index}: bỏ qua - thiếu 'ten'.")
            continue
        if row["loai"] == "mau" and not row["hang"]:
            warnings.append(f"Dòng {index}: mẫu xe '{row['ten']}' chưa có 'hang' liên kết.")

        rows.append(row)

    if not rows:
        raise CatalogImportError("File không có dòng dữ liệu hợp lệ nào để import.")

    return rows, warnings
