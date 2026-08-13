import csv
import os
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree


SPREADSHEET_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}


def _rows_to_text(rows):
    lines = []
    for row in rows:
        values = [str(value).strip() for value in row]
        while values and not values[-1]:
            values.pop()
        if any(values):
            lines.append("\t".join(values))
    return "\n".join(lines)


def _column_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref or "")
    if not match:
        return 0

    index = 0
    for char in match.group(1):
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1


def _load_csv(path: str):
    encodings = ("utf-8-sig", "utf-8", "cp1258")
    last_error = None
    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding, newline="") as handle:
                sample = handle.read(4096)
                handle.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample)
                except csv.Error:
                    dialect = csv.excel
                return _rows_to_text(csv.reader(handle, dialect))
        except UnicodeDecodeError as error:
            last_error = error
    raise ValueError(f"Không đọc được encoding CSV: {last_error}")


def _load_shared_strings(archive: zipfile.ZipFile):
    try:
        xml_data = archive.read("xl/sharedStrings.xml")
    except KeyError:
        return []

    root = ElementTree.fromstring(xml_data)
    values = []
    for item in root.findall("main:si", SPREADSHEET_NS):
        texts = [node.text or "" for node in item.findall(".//main:t", SPREADSHEET_NS)]
        values.append("".join(texts))
    return values


def _cell_value(cell, shared_strings):
    cell_type = cell.attrib.get("t")
    value_node = cell.find("main:v", SPREADSHEET_NS)

    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//main:t", SPREADSHEET_NS))

    if value_node is None or value_node.text is None:
        return ""

    raw_value = value_node.text
    if cell_type == "s":
        index = int(raw_value)
        return shared_strings[index] if index < len(shared_strings) else ""

    return raw_value


def _load_xlsx(path: str):
    with zipfile.ZipFile(path) as archive:
        shared_strings = _load_shared_strings(archive)
        sheet_names = sorted(
            name
            for name in archive.namelist()
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        )
        if not sheet_names:
            raise ValueError("File Excel không có worksheet.")

        sheet = ElementTree.fromstring(archive.read(sheet_names[0]))
        rows = []
        for row_node in sheet.findall(".//main:row", SPREADSHEET_NS):
            row = []
            for cell in row_node.findall("main:c", SPREADSHEET_NS):
                column_index = _column_index(cell.attrib.get("r", ""))
                while len(row) <= column_index:
                    row.append("")
                row[column_index] = _cell_value(cell, shared_strings)
            rows.append(row)
        return _rows_to_text(rows)


def load_table_file(path: str):
    suffix = Path(path).suffix.lower()
    if suffix == ".csv":
        return _load_csv(path)
    if suffix == ".xlsx":
        return _load_xlsx(path)
    raise ValueError("Chỉ hỗ trợ file .csv hoặc .xlsx.")
