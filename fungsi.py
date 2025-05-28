import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime

# Fungsi untuk file upload (regex disesuaikan)
def process_chat_text_file(chat_text):
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - (.*?): (.+?)(?=\n\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} -|\Z)'
    entries = re.findall(pattern, chat_text, re.DOTALL)

    data = []
    for date_str, time, sender, message in entries:
        if not re.search(r'\b(UNRECORD|REQ BIN TF|WRONG BIN|UNRECORDS)\b', message, re.IGNORECASE):
            continue

        remark = "UNRECORD"
        if "REQ BIN TF" in message.upper():
            remark = "REQ BIN TF"
        elif "WRONG BIN" in message.upper():
            remark = "WRONG BIN"

        base = {
            "Nama": sender.split()[0],
            "Tanggal": datetime.strptime(date_str, "%d/%m/%y").strftime("%m/%d/%Y"),
            "LOC": "", "BIN": "", "PN": "", "SN": "", "QTY": 1, "REMARK": remark
        }

        lines = message.strip().splitlines()
        sn_list, parsing_bulk_items, multi_item_found = [], False, False

        for line in lines:
            line, upper_line = line.strip(), line.upper()
            if re.match(r'PN\s*(,|&)\s*QTY', upper_line):
                parsing_bulk_items = True
                continue
            if parsing_bulk_items:
                match = re.match(r'^\d+\.\s*([\w\-\/]+)\s*\((\d+)', line)
                if match:
                    pn, qty = match.group(1).strip(), int(match.group(2).strip())
                    record = base.copy(); record["PN"], record["QTY"] = pn, qty
                    data.append(record); multi_item_found = True
                continue
            if line.startswith("-") and "|" in line:
                item_match = re.match(r'-\s*(.+?)\s*\|\s*(\d+)', line)
                if item_match:
                    pn, qty = item_match.group(1).strip(), int(item_match.group(2).strip())
                    record = base.copy(); record["PN"], record["QTY"] = pn, qty
                    data.append(record); multi_item_found = True
                continue
            if re.match(r'(PN:|PN :)', upper_line): base["PN"] = line.split(":", 1)[1].strip()
            elif re.match(r'(SN:|SN :)', upper_line): sn = line.split(":", 1)[1].strip(); sn_list.append(sn)
            elif re.match(r'^\d+\.\s', line): sn = line.split('.', 1)[1].strip(); sn_list.append(sn)
            elif re.match(r'(BIN|BIN\s*ACT|BIN\s*ACTUAL|FOUND IN BIN)', upper_line): base["BIN"] = line.split(":", 1)[1].strip()
            elif re.match(r'(LOC:|LOC :)', upper_line): base["LOC"] = line.split(":", 1)[1].strip()
            elif "QTY ACTUAL" in upper_line or "QTY ACT" in upper_line or "QTY" in upper_line:
                qty_match = re.search(r'\d+', line)
                if qty_match: base["QTY"] = int(qty_match.group())
            elif re.match(r'(REMARK:|REMARKS:|REMARK :|REMARKS :)', upper_line): base["REMARK"] = line.split(":", 1)[1].strip()
        if not multi_item_found:
            if not sn_list: sn_list.append("")
            for sn in sn_list: row = base.copy(); row["SN"] = sn; data.append(row)
    return pd.DataFrame(data)

# Fungsi untuk copy-paste manual (pakai code awal kamu)
def process_chat_text_manual(chat_text):
        # Regex pattern to extract message blocks
    pattern = r'\[(\d{2}:\d{2}), (\d{1,2}/\d{1,2}/\d{4})\] (.*?): (.*?)(?=\[\d{2}:\d{2},|\Z)'
    entries = re.findall(pattern, chat_text, re.DOTALL)

    data = []

    for time, date_str, sender, message in entries:
        if not re.search(r'\b(UNRECORD|REQ BIN TF|WRONG BIN|UNRECORDS)\b', message, re.IGNORECASE):
            continue

        remark = "UNRECORD"
        if "REQ BIN TF" in message.upper():
            remark = "REQ BIN TF"
        elif "WRONG BIN" in message.upper():
            remark = "WRONG BIN"

        base = {
            "Nama": sender.split()[0],
            "Tanggal": date_str,
            "LOC": "",
            "BIN": "",
            "PN": "",
            "SN": "",
            "QTY": 1,
            "REMARK": remark
        }

        lines = message.strip().splitlines()
        sn_list = []
        parsing_bulk_items = False
        multi_item_found = False

        for line in lines:
            line = line.strip()
            upper_line = line.upper()

            if re.match(r'PN\s*(,|&)\s*QTY', upper_line):
                parsing_bulk_items = True
                continue

            if parsing_bulk_items:
                match = re.match(r'^\d+\.\s*([\w\-\/]+)\s*\((\d+)', line)
                if match:
                    pn = match.group(1).strip()
                    qty = int(match.group(2).strip())
                    record = base.copy()
                    record["PN"] = pn
                    record["QTY"] = qty
                    data.append(record)
                    multi_item_found = True
                continue

            if line.startswith("-") and "|" in line:
                item_match = re.match(r'-\s*(.+?)\s*\|\s*(\d+)', line)
                if item_match:
                    pn = item_match.group(1).strip()
                    qty = int(item_match.group(2).strip())
                    record = base.copy()
                    record["PN"] = pn
                    record["QTY"] = qty
                    data.append(record)
                    multi_item_found = True
                continue

            if re.match(r'(PN:|PN :)', upper_line):
                base["PN"] = line.split(":", 1)[1].strip()

            elif re.match(r'(SN:|SN :)', upper_line):
                sn = line.split(":", 1)[1].strip()
                if sn:
                    sn_list.append(sn)

            elif re.match(r'^\d+\.\s', line):  # SN list
                sn = line.split('.', 1)[1].strip()
                if sn:
                    sn_list.append(sn)

            elif re.match(r'(BIN|BIN\s*ACT|BIN\s*ACTUAL|FOUND IN BIN)', upper_line):
                base["BIN"] = line.split(":", 1)[1].strip()

            elif re.match(r'(LOC:|LOC :)', upper_line):
                base["LOC"] = line.split(":", 1)[1].strip()

            elif "QTY ACTUAL" in upper_line or "QTY ACT" in upper_line or "QTY" in upper_line:
                qty_match = re.search(r'\d+', line)
                if qty_match:
                    base["QTY"] = int(qty_match.group())

            elif re.match(r'(REMARK:|REMARKS:|REMARK :|REMARKS :)', upper_line):
                base["REMARK"] = line.split(":", 1)[1].strip()

        if not multi_item_found:
            if not sn_list:
                sn_list.append("")  # still add row if SN is empty
            for sn in sn_list:
                row = base.copy()
                row["SN"] = sn
                data.append(row)
    return pd.DataFrame(data)

