import json
from copy import deepcopy
from pathlib import Path


class DataStore:
    """JSON store tạm cho phần UI của Linh.

    Khi service SQLite của nhóm sẵn sàng, có thể giữ nguyên giao diện các method
    bên dưới và thay implementation bằng repository SQLite.
    """

    def __init__(self, path=None):
        base = Path(__file__).resolve().parents[1]
        self.path = Path(path) if path else base / "data" / "page_elements.json"
        self.data = self._load()

    def _load(self):
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def reload(self):
        self.data = self._load()
        return self.data

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def websites(self):
        return self.data.get("websites", [])

    def find_website(self, website_id):
        return next(
            (w for w in self.websites() if w.get("id") == website_id),
            None,
        )

    def find_page(self, website_id, page_id):
        website = self.find_website(website_id)
        if not website:
            return None
        return next(
            (p for p in website.get("pages", []) if p.get("id") == page_id),
            None,
        )

    def find_element(self, website_id, page_id, element_id):
        page = self.find_page(website_id, page_id)
        if not page:
            return None
        return next(
            (e for e in page.get("elements", []) if e.get("id") == element_id),
            None,
        )

    def page_url(self, website_id, page_id):
        website = self.find_website(website_id)
        page = self.find_page(website_id, page_id)
        if not website or not page:
            return ""
        return website.get("base_url", "").rstrip("/") + "/" + page.get("path", "").lstrip("/")

    def add_or_update_element(self, website_id, page_id, element_data, original_element_id=None):
        page = self.find_page(website_id, page_id)
        if not page:
            raise ValueError("Không tìm thấy Page đang chọn")

        elements = page.setdefault("elements", [])
        if original_element_id:
            for index, element in enumerate(elements):
                if element.get("id") == original_element_id:
                    elements[index] = deepcopy(element_data)
                    self.save()
                    return

        elements.append(deepcopy(element_data))
        self.save()

    def delete_element(self, website_id, page_id, element_id):
        page = self.find_page(website_id, page_id)
        if not page:
            return False

        elements = page.get("elements", [])
        new_elements = [e for e in elements if e.get("id") != element_id]
        if len(new_elements) == len(elements):
            return False

        page["elements"] = new_elements
        self.save()
        return True

    def ensure_page(self, website_id, page_stub):
        """Đảm bảo một Page tồn tại (idempotent), dùng cho module tự chủ như Danh mục xe.

        Nếu Page đã có (theo id) thì giữ nguyên dữ liệu hiện tại, không ghi đè element
        đã được người dùng chỉnh sửa. Trả về id của Page.
        """
        website = self.find_website(website_id)
        if not website:
            raise ValueError(f"Không tìm thấy Website '{website_id}'")

        existing = self.find_page(website_id, page_stub.get("id"))
        if existing:
            return existing.get("id")

        website.setdefault("pages", []).append(deepcopy(page_stub))
        self.save()
        return page_stub.get("id")

    def elements_by_group(self, website_id, page_id, group):
        """Trả về danh sách element thuộc một nhóm (vd: 'brand' / 'model')."""
        page = self.find_page(website_id, page_id)
        if not page:
            return []
        return [e for e in page.get("elements", []) if e.get("group") == group]
