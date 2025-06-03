#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для скачивания и парсинга всех требований к фотографиям (requirements)
со страницы https://visafoto.com/requirements и сохранения результатов сразу в виде
Python-кода.
"""

import requests
from bs4 import BeautifulSoup
import re
import pycountry
import traceback 

BASE_URL = "https://visafoto.com"
REQUIREMENTS_URL = BASE_URL + "/requirements"
INCH_TO_MM = 25.4

def _parse_value_unit(value_str, unit_str, dpi_for_px_conversion=300):
    if value_str is None:
        return None
    try:
        val = float(value_str)
    except ValueError:
        return None
        
    unit_lower = unit_str.lower() if unit_str else ""

    if unit_lower.startswith("in"): # inches
        return val * INCH_TO_MM
    elif unit_lower == "px" or unit_lower == "pixel": # pixels
        if dpi_for_px_conversion > 0:
            return (val / dpi_for_px_conversion) * INCH_TO_MM
        else: 
            print(f"  ПРЕДУПРЕЖДЕНИЕ: Невозможно конвертировать {val}px в мм. DPI = {dpi_for_px_conversion}")
            return None 
    return val # Default to mm


def _extract_dim_range_mm_in(base_pattern_text, text_block, dpi_for_px_conversion=300):
    pattern1 = re.compile(
        base_pattern_text +
        r".*?(?:\(|is\sbetween\s|:\s)?"  
        r"([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)?" 
        r"\s*(?:and|[–-])\s*"  
        r"([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)?"  
        r"(?:\s*(mm|in|inch(?:es)?|px|pixel))?"  
        r"\s*\)?",  
        re.IGNORECASE
    )
    m = pattern1.search(text_block)
    if m:
        val1_str, unit1_s, val2_str, unit2_s, unit_suffix_s = m.groups()
        u1 = unit1_s if unit1_s else unit_suffix_s
        u2 = unit2_s if unit2_s else unit_suffix_s
        if u1 and not u2: u2 = u1 
        if u2 and not u1: u1 = u2 
        min_val = _parse_value_unit(val1_str, u1, dpi_for_px_conversion)
        max_val = _parse_value_unit(val2_str, u2, dpi_for_px_conversion)
        return min_val, max_val

    pattern2 = re.compile(
        base_pattern_text +
        r".*?(?:is|:)?\s*" 
        r"([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)?", 
        re.IGNORECASE
    )
    m = pattern2.search(text_block)
    if m:
        val_str, unit_str = m.groups()
        val = _parse_value_unit(val_str, unit_str, dpi_for_px_conversion)
        return val, val 
    return None, None


def get_country_document_links():
    resp = requests.get(REQUIREMENTS_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for table in soup.find_all("table"): 
        for row in table.select("tr"):
            cells = row.find_all("td")
            if len(cells) < 2: continue
            country_cell_text = cells[0].get_text(strip=True)
            if not country_cell_text: continue
            country = country_cell_text
            a_tag = cells[1].find("a", href=True)
            if not a_tag: continue
            doc_text = a_tag.get_text(strip=True) 
            href = a_tag["href"]
            full_url = href if href.startswith("http") else BASE_URL + href
            links.append((country, doc_text, full_url))
    return links

def parse_requirements_page(url):
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    header = soup.find(lambda tag: tag.name in ("h2", "h3") and ("Requirement" in tag.get_text() or "Photo Specs" in tag.get_text()))
    if not header:
        print(f"Warning: No 'Requirement' or 'Photo Specs' header found on {url}")
        return {}
    raw_lines = []
    for sib in header.find_next_siblings():
        if sib.name in ("h2", "h3"): break
        text_content = sib.get_text("\n", strip=False) 
        if text_content:
            for ln in text_content.splitlines():
                ln_stripped = ln.strip()
                if ln_stripped: raw_lines.append(ln_stripped)
    
    labels = [
        "Country", "Document Type", 
        "Passport picture size", "Size", 
        "Resolution (dpi)",
        "Required Size in Kilobytes", 
        "Image definition parameters", "Background color", 
        "Printable?", "Suitable for online submission?", 
        "Other requirements", "Comments", "Web links to official documents", "File size"
    ]
    data_dict = {}
    i = 0
    n = len(raw_lines)
    while i < n:
        current_line_text = raw_lines[i]
        matched_label = None
        for label_text_candidate in labels:
            if current_line_text.lower().startswith(label_text_candidate.lower()):
                if len(current_line_text) == len(label_text_candidate) or \
                   not current_line_text[len(label_text_candidate)].isalnum(): 
                    matched_label = label_text_candidate
                    break
        
        if matched_label:
            value_collector = []
            first_value_part = current_line_text[len(matched_label):].lstrip(",: ").strip()
            if matched_label == "Background color" and not first_value_part:
                value_collector.append("") 
            elif first_value_part: 
                value_collector.append(first_value_part)
            
            next_line_idx = i + 1
            
            def _is_next_line_a_label(line_text):
                return any(line_text.lower().startswith(l.lower()) and \
                           (len(line_text) == len(l) or not line_text[len(l)].isalnum()) \
                           for l in labels)

            if matched_label == "Web links to official documents":
                while next_line_idx < n:
                    next_ln_text = raw_lines[next_line_idx].strip()
                    if _is_next_line_a_label(next_ln_text): break
                    if next_ln_text.startswith("http"): value_collector.append(next_ln_text)
                    elif not next_ln_text: pass 
                    else: break 
                    next_line_idx += 1
            else: 
                while next_line_idx < n:
                    next_ln_text = raw_lines[next_line_idx].strip()
                    if _is_next_line_a_label(next_ln_text): break
                    if next_ln_text: value_collector.append(next_ln_text)
                    next_line_idx += 1
            
            final_label = "Passport picture size" if matched_label == "Size" else matched_label
            if matched_label == "Required Size in Kilobytes": final_label = "File size"

            data_dict[final_label] = "\n".join(value_collector)
            i = next_line_idx -1 
        i += 1
    return data_dict

def parse_image_definition_params(text, dpi_for_px_conversion=300):
    result = {
        "head_min_pct": None, "head_max_pct": None,
        "head_min_mm_abs": None, "head_max_mm_abs": None,
        "top_margin_min_pct": None, "top_margin_max_pct": None, 
        "top_margin_min_mm_abs": None, "top_margin_max_mm_abs": None,
        "eye_min_mm": None, "eye_max_mm": None
    }
    if not text: return result
    
    m_head_pct_range = re.search(r"Head height.*?between\s*([\d.]+)\s*%?\s*and\s*([\d.]+)\s*%", text, flags=re.IGNORECASE)
    if m_head_pct_range:
        min_pct_val = _parse_value_unit(m_head_pct_range.group(1), None) 
        max_pct_val = _parse_value_unit(m_head_pct_range.group(2), None)
        result["head_min_pct"] = min_pct_val / 100.0 if min_pct_val is not None else None
        result["head_max_pct"] = max_pct_val / 100.0 if max_pct_val is not None else None
    else:
        m_head_pct_single = re.search(r"Head height.*?[:\s]\s*([\d.]+)\s*%", text, flags=re.IGNORECASE)
        if m_head_pct_single:
            pct_val = _parse_value_unit(m_head_pct_single.group(1), None)
            if pct_val is not None:
                result["head_min_pct"] = pct_val / 100.0
                result["head_max_pct"] = pct_val / 100.0
    
    result["head_min_mm_abs"], result["head_max_mm_abs"] = _extract_dim_range_mm_in(r"Head height", text, dpi_for_px_conversion)
    
    m_top_pct_range = re.search(r"Distance from top.*?between\s*([\d.]+)\s*%?\s*and\s*([\d.]+)\s*%", text, flags=re.IGNORECASE)
    if m_top_pct_range:
        min_pct_val = _parse_value_unit(m_top_pct_range.group(1), None)
        max_pct_val = _parse_value_unit(m_top_pct_range.group(2), None)
        result["top_margin_min_pct"] = min_pct_val / 100.0 if min_pct_val is not None else None
        result["top_margin_max_pct"] = max_pct_val / 100.0 if max_pct_val is not None else None
    else:
        m_top_pct_single = re.search(r"Distance from top.*?[:\s]\s*([\d.]+)\s*%", text, flags=re.IGNORECASE)
        if m_top_pct_single:
            pct_val = _parse_value_unit(m_top_pct_single.group(1), None)
            if pct_val is not None:
                result["top_margin_min_pct"] = pct_val / 100.0
                result["top_margin_max_pct"] = pct_val / 100.0
                
    result["top_margin_min_mm_abs"], result["top_margin_max_mm_abs"] = _extract_dim_range_mm_in(r"Distance from top", text, dpi_for_px_conversion)

    eye_base_pattern = r"(?:Eye\s*(?:level|distance|position)?\s*(?:from\s+(?:the\s+)?bottom)?|Chin\s+to\s+eye\s*center)"
    result["eye_min_mm"], result["eye_max_mm"] = _extract_dim_range_mm_in(eye_base_pattern, text, dpi_for_px_conversion)
    
    return result

def extract_background_color(text):
    text = text.strip()
    if not text: return None 
    if text.lower() in ["printable?", "see notes", "see comments", ""]: return None 
    cleaned_text = re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()
    if not cleaned_text and text.startswith("(") and text.endswith(")"): return None
    final_text = cleaned_text if cleaned_text else text
    return final_text if final_text else None

def extract_source_urls(data_dict):
    urls = []
    raw = data_dict.get("Web links to official documents", "")
    for ln in raw.splitlines():
        ln = ln.strip()
        if ln.startswith("http"):
            if "visafoto.com" in ln or "app.apple.com" in ln or "play.google.com" in ln: continue
            urls.append(ln)
    return urls

def country_to_iso2(name):
    try:
        name_clean = name.split('(')[0].strip()
        name_clean = name_clean.replace(", Bolivarian Republic of", "").strip()
        name_clean = name_clean.replace(", Islamic Republic of", "").strip()
        name_clean = name_clean.replace(", Plurinational State of", "").strip()
        name_clean = name_clean.replace(", People's Republic of", "").strip()
        name_clean = name_clean.replace(" SAR", "").strip()
        if name_clean.lower() == "congo, democratic republic of the": name_clean = "Congo, The Democratic Republic of the"
        if name_clean.lower() == "congo": name_clean = "Congo" 
        if name_clean.lower() == "korea, south": name_clean = "Korea, Republic of"
        if name_clean.lower() == "korea, north": name_clean = "Korea, Democratic People's Republic of"
        if name_clean.lower() == "macau" : name_clean = "Macao"
        c = pycountry.countries.lookup(name_clean)
        return c.alpha_2
    except (LookupError, KeyError):
        name_lower = name_clean.lower() 
        if "kosovo" in name_lower: return "XK" 
        if "taiwan" in name_lower: return "TW"
        try:
            c_fuzzy = pycountry.countries.search_fuzzy(name_clean)
            if c_fuzzy: return c_fuzzy[0].alpha_2
        except (LookupError, KeyError): pass
        return name_clean[:2].upper() if name_clean else "XX"

def build_photo_spec_code(country_from_link, doc_type_from_link, data_dict, source_url_page):
    lines = []
    lines.append("DOCUMENT_SPECIFICATIONS.append(PhotoSpecification(")
    
    country_name_from_data = data_dict.get("Country") 
    country_name = country_name_from_data if country_name_from_data else country_from_link
    iso2 = country_to_iso2(country_name)
    lines.append(f"    country_code='{iso2}',")

    document_name = doc_type_from_link 
    doc_esc = document_name.replace("'", "\\'")
    lines.append(f"    document_name='{doc_esc}',")

    dpi_txt = data_dict.get("Resolution (dpi)", "").strip()
    parsed_dpi_val = 0
    m_dpi = re.search(r"(\d+)", dpi_txt) 
    if m_dpi: 
        try: parsed_dpi_val = int(m_dpi.group(1))
        except ValueError: parsed_dpi_val = 0 
    
    final_dpi_val = 300 
    if parsed_dpi_val > 10: 
        final_dpi_val = parsed_dpi_val
    elif parsed_dpi_val > 0 : 
        print(f"  ИНФО: Обнаружено нереалистичное DPI={parsed_dpi_val} для '{document_name}' ({country_name}). Будет использовано DPI=300.")
        
    lines.append(f"    dpi={final_dpi_val},")

    size_val = data_dict.get("Passport picture size", "") 
    w_mm, h_mm = None, None
    m_dims = re.search(r"Width:\s*([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)\s*.*?[,;\s]?\s*Height:\s*([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)", size_val, re.IGNORECASE | re.DOTALL)
    if m_dims:
        w_mm = _parse_value_unit(m_dims.group(1), m_dims.group(2), final_dpi_val)
        h_mm = _parse_value_unit(m_dims.group(3), m_dims.group(4), final_dpi_val)
    else: 
        m_w = re.search(r"Width:\s*([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)", size_val, re.IGNORECASE)
        if m_w: w_mm = _parse_value_unit(m_w.group(1), m_w.group(2), final_dpi_val)
        m_h = re.search(r"Height:\s*([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)", size_val, re.IGNORECASE)
        if m_h: h_mm = _parse_value_unit(m_h.group(1), m_h.group(2), final_dpi_val)
        
        if w_mm is None or h_mm is None: 
            m_cross = re.search(r"([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)\s*[xX]\s*([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)", size_val, re.IGNORECASE)
            if m_cross:
                w_mm = _parse_value_unit(m_cross.group(1), m_cross.group(2), final_dpi_val)
                h_mm = _parse_value_unit(m_cross.group(3), m_cross.group(4), final_dpi_val)
            else:
                m_cross_unit_end = re.search(r"([\d.]+)\s*[xX]\s*([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)", size_val, re.IGNORECASE)
                if m_cross_unit_end:
                    unit = m_cross_unit_end.group(3)
                    w_mm = _parse_value_unit(m_cross_unit_end.group(1), unit, final_dpi_val)
                    h_mm = _parse_value_unit(m_cross_unit_end.group(2), unit, final_dpi_val)
                else: 
                    all_dims_found = re.findall(r"([\d.]+)\s*(mm|in|inch(?:es)?|px|pixel)", size_val, re.IGNORECASE)
                    if len(all_dims_found) == 1: w_mm = h_mm = _parse_value_unit(all_dims_found[0][0], all_dims_found[0][1], final_dpi_val)
                    elif len(all_dims_found) >= 2: 
                        w_mm = _parse_value_unit(all_dims_found[0][0], all_dims_found[0][1], final_dpi_val)
                        h_mm = _parse_value_unit(all_dims_found[1][0], all_dims_found[1][1], final_dpi_val)
    
    if w_mm is not None and h_mm is None: h_mm = w_mm
    elif h_mm is not None and w_mm is None: w_mm = h_mm
    w_mm_val = w_mm if w_mm is not None else 0.0 
    h_mm_val = h_mm if h_mm is not None else 0.0

    if w_mm_val == 0.0 or h_mm_val == 0.0:
        print(f"  ПРЕДУПРЕЖДЕНИЕ: Нулевые размеры для '{document_name}' ({country_name}). Ширина: {w_mm_val}, Высота: {h_mm_val}. URL: {source_url_page}")

    lines.append(f"    photo_width_mm={w_mm_val:.3f},")
    lines.append(f"    photo_height_mm={h_mm_val:.3f},")

    img_params_text = data_dict.get("Image definition parameters", "")
    img_info = parse_image_definition_params(img_params_text, final_dpi_val)

    head_min_p = img_info.get("head_min_pct")
    head_max_p = img_info.get("head_max_pct")
    if head_min_p is not None and head_max_p is None: head_max_p = head_min_p
    lines.append(f"    head_min_percentage={f'{head_min_p:.2f}' if head_min_p is not None else 'None'},")
    lines.append(f"    head_max_percentage={f'{head_max_p:.2f}' if head_max_p is not None else 'None'},")
    
    val_head_min_mm, val_head_max_mm = None, None
    abs_head_min_mm, abs_head_max_mm = img_info.get("head_min_mm_abs"), img_info.get("head_max_mm_abs")
    if abs_head_min_mm is not None: val_head_min_mm = abs_head_min_mm
    elif h_mm_val > 0 and head_min_p is not None: val_head_min_mm = head_min_p * h_mm_val
    if abs_head_max_mm is not None: val_head_max_mm = abs_head_max_mm
    elif h_mm_val > 0 and head_max_p is not None: val_head_max_mm = head_max_p * h_mm_val
    elif val_head_min_mm is not None : val_head_max_mm = val_head_min_mm
    lines.append(f"    head_min_mm={f'{val_head_min_mm:.3f}' if val_head_min_mm is not None else 'None'},")
    lines.append(f"    head_max_mm={f'{val_head_max_mm:.3f}' if val_head_max_mm is not None else 'None'},")

    eye_min_f_b_mm, eye_max_f_b_mm = img_info.get("eye_min_mm"), img_info.get("eye_max_mm")
    if eye_min_f_b_mm is not None and eye_max_f_b_mm is None: eye_max_f_b_mm = eye_min_f_b_mm
    lines.append(f"    eye_min_from_bottom_mm={f'{eye_min_f_b_mm:.3f}' if eye_min_f_b_mm is not None else 'None'},")
    lines.append(f"    eye_max_from_bottom_mm={f'{eye_max_f_b_mm:.3f}' if eye_max_f_b_mm is not None else 'None'},")
    
    val_head_top_min_dist_mm, val_head_top_max_dist_mm = None, None
    abs_top_min_mm = img_info.get("top_margin_min_mm_abs")
    abs_top_max_mm = img_info.get("top_margin_max_mm_abs")
    top_margin_min_p = img_info.get("top_margin_min_pct")
    top_margin_max_p = img_info.get("top_margin_max_pct")
    if top_margin_min_p is not None and top_margin_max_p is None: top_margin_max_p = top_margin_min_p

    if abs_top_min_mm is not None: val_head_top_min_dist_mm = abs_top_min_mm
    elif h_mm_val > 0 and top_margin_min_p is not None: val_head_top_min_dist_mm = top_margin_min_p * h_mm_val
    if abs_top_max_mm is not None: val_head_top_max_dist_mm = abs_top_max_mm
    elif h_mm_val > 0 and top_margin_max_p is not None: val_head_top_max_dist_mm = top_margin_max_p * h_mm_val
    elif val_head_top_min_dist_mm is not None: val_head_top_max_dist_mm = val_head_top_min_dist_mm
        
    lines.append(f"    distance_top_of_head_to_top_of_photo_min_mm={f'{val_head_top_min_dist_mm:.3f}' if val_head_top_min_dist_mm is not None else 'None'},")
    lines.append(f"    distance_top_of_head_to_top_of_photo_max_mm={f'{val_head_top_max_dist_mm:.3f}' if val_head_top_max_dist_mm is not None else 'None'},")
    lines.append(f"    head_top_min_dist_from_photo_top_mm={f'{val_head_top_min_dist_mm:.3f}' if val_head_top_min_dist_mm is not None else 'None'},") 
    lines.append(f"    head_top_max_dist_from_photo_top_mm={f'{val_head_top_max_dist_mm:.3f}' if val_head_top_max_dist_mm is not None else 'None'},")

    bg_color_val = extract_background_color(data_dict.get("Background color", ""))
    final_bg_color_str = f"'{bg_color_val.replace("'", "\\'")}'" if bg_color_val else "'white'" 
    lines.append(f"    background_color={final_bg_color_str},")

    other_req_text = data_dict.get("Other requirements", "") or data_dict.get("Comments", "")
    other_req_text_lower = other_req_text.lower() # This line defines other_req_text_lower

    glasses_val = 'no' 
    if "glasses are permitted" in other_req_text_lower and "not cause glare" in other_req_text_lower: glasses_val = 'if_no_glare'
    elif "glasses: yes" in other_req_text_lower or ("glasses allowed" in other_req_text_lower and not "not allowed" in other_req_text_lower and not "no glasses" in other_req_text_lower) : glasses_val = 'yes'
    elif any(s in other_req_text_lower for s in ["glasses: no", "no glasses", "glasses are not allowed", "glasses not permitted", "without glasses"]): glasses_val = 'no'
    lines.append(f"    glasses_allowed='{glasses_val}',")

    neutral_expr_val = True 
    if "no specific requirement for expression" in other_req_text_lower: neutral_expr_val = False
    # Corrected elif condition below
    elif not ("neutral expression" in other_req_text_lower or "mouth closed" in other_req_text_lower): 
        pass 
    else: 
        neutral_expr_val = "neutral expression" in other_req_text_lower or "mouth closed" in other_req_text_lower
    lines.append(f"    neutral_expression_required={neutral_expr_val},")
    
    other_req_esc = other_req_text.replace("'", "\\'").replace("\n", "\\n")
    lines.append(f"    other_requirements={'None' if not other_req_esc else f"'{other_req_esc}'"},")

    default_head_top_val = top_margin_min_p if top_margin_min_p is not None else 0.12 
    lines.append(f"    default_head_top_margin_percent={default_head_top_val:.2f},")
    
    lines.append(f"    min_visual_head_margin_px=5,")
    lines.append(f"    min_visual_chin_margin_px=5,")

    fs_min_kb, fs_max_kb = None, None
    file_size_text = data_dict.get("File size", "") or other_req_text 
    m_fs_range = re.search(r"(?:From:\s*)?([\d.]+)\s*(?:to)?\s*[–-]?\s*([\d.]+)\s*KB", file_size_text, re.IGNORECASE) 
    if m_fs_range:
        fs_min_kb_str, fs_max_kb_str = m_fs_range.group(1), m_fs_range.group(2)
        try: fs_min_kb = int(float(fs_min_kb_str)) 
        except ValueError: pass
        try: fs_max_kb = int(float(fs_max_kb_str))
        except ValueError: pass
    else: 
        m_fs_min = re.search(r"(?:min|minimum|from)\D*?([\d.]+)\s*KB", file_size_text, re.IGNORECASE)
        if m_fs_min:
            try: fs_min_kb = int(float(m_fs_min.group(1)))
            except ValueError: pass
        m_fs_max = re.search(r"(?:max|maximum|up\s*to|less\s*than|not\s*exceeding|not\s*more\s*than)\D*?([\d.]+)\s*KB", file_size_text, re.IGNORECASE)
        if m_fs_max:
            try: fs_max_kb = int(float(m_fs_max.group(1)))
            except ValueError: pass
            
    lines.append(f"    file_size_min_kb={'None' if fs_min_kb is None else fs_min_kb},")
    lines.append(f"    file_size_max_kb={'None' if fs_max_kb is None else fs_max_kb},")

    source_urls_list = extract_source_urls(data_dict)
    if source_urls_list:
        lines.append("    source_urls=[")
        for u in source_urls_list: lines.append(f"        '{u.replace("'", "\\'")}',")
        lines.append("    ],")
    else:
        lines.append("    source_urls=[],") 
    
    lines.append("))\n")
    return "\n".join(lines)

def main():
    links = get_country_document_links()
    specs_found = 0
    output_filename = "photo_app_req.py"
    with open(output_filename, "w", encoding="utf-8") as fout:
        fout.write("# Auto-generated PhotoSpecification entries from visafoto.com/requirements\n")
        fout.write("from dataclasses import dataclass, field\n")
        fout.write("from typing import List, Optional, Dict, Tuple\n\n")
        fout.write("@dataclass\n")
        fout.write("class PhotoSpecification:\n")
        fout.write("    country_code: str\n")
        fout.write("    document_name: str\n")
        fout.write("    photo_width_mm: float\n")
        fout.write("    photo_height_mm: float\n")
        fout.write("    dpi: int = 300\n")
        fout.write("    head_min_percentage: Optional[float] = None # Min head height as percentage of photo height\n")
        fout.write("    head_max_percentage: Optional[float] = None # Max head height as percentage of photo height\n")
        fout.write("    head_min_mm: Optional[float] = None # Absolute min head height in mm (alternative to percentage)\n")
        fout.write("    head_max_mm: Optional[float] = None # Absolute max head height in mm (alternative to percentage)\n")
        fout.write("    eye_min_from_bottom_mm: Optional[float] = None\n")
        fout.write("    eye_max_from_bottom_mm: Optional[float] = None\n")
        fout.write("    eye_min_from_top_mm: Optional[float] = None # Alternative for some specs\n")
        fout.write("    eye_max_from_top_mm: Optional[float] = None # Alternative for some specs\n")
        fout.write("    distance_top_of_head_to_top_of_photo_min_mm: Optional[float] = None # e.g. Schengen\n")
        fout.write("    distance_top_of_head_to_top_of_photo_max_mm: Optional[float] = None # e.g. Schengen\n")
        fout.write("    background_color: str = \"white\" # Controlled vocabulary: \"white\", \"off-white\", \"light_grey\", \"blue\"\n")
        fout.write("    glasses_allowed: str = \"no\" # Controlled vocabulary: \"yes\", \"no\", \"if_no_glare\"\n")
        fout.write("    neutral_expression_required: bool = True\n")
        fout.write("    other_requirements: Optional[str] = None\n")
        fout.write("    source_url: Optional[str] = None # Optional: URL to the official specification, can be list now\n")
        fout.write("    \n")
        fout.write("    # Enhanced positioning control fields\n")
        fout.write("    head_top_min_dist_from_photo_top_mm: Optional[float] = None\n")
        fout.write("    head_top_max_dist_from_photo_top_mm: Optional[float] = None\n")
        fout.write("    default_head_top_margin_percent: float = 0.12\n")
        fout.write("    min_visual_head_margin_px: int = 5\n")
        fout.write("    min_visual_chin_margin_px: int = 5\n")
        fout.write("\n")
        fout.write("    # New fields for visafoto style info\n")
        fout.write("    file_size_min_kb: Optional[int] = None\n")
        fout.write("    file_size_max_kb: Optional[int] = None\n")
        fout.write("    source_urls: Optional[List[str]] = field(default_factory=list)\n")
        fout.write("\n")
        fout.write("    MM_PER_INCH = 25.4\n")
        fout.write("\n")
        fout.write("    @property\n")
        fout.write("    def photo_width_px(self) -> int:\n")
        fout.write("        if self.photo_width_mm == 0 or self.dpi == 0: return 0\n")
        fout.write("        return int(self.photo_width_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("\n")
        fout.write("    @property\n")
        fout.write("    def photo_height_px(self) -> int:\n")
        fout.write("        if self.photo_height_mm == 0 or self.dpi == 0: return 0\n")
        fout.write("        return int(self.photo_height_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("\n")
        fout.write("    # Head height in pixels, derived primarily from mm if available, else from percentage\n")
        fout.write("    @property\n")
        fout.write("    def head_min_px(self) -> Optional[int]:\n")
        fout.write("        if self.head_min_mm is not None and self.dpi != 0:\n")
        fout.write("            return int(self.head_min_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("        if self.head_min_percentage is not None and self.photo_height_px > 0:\n") 
        fout.write("            return int(self.photo_height_px * self.head_min_percentage)\n")
        fout.write("        return None\n")
        fout.write("\n")
        fout.write("    @property\n")
        fout.write("    def head_max_px(self) -> Optional[int]:\n")
        fout.write("        if self.head_max_mm is not None and self.dpi != 0:\n")
        fout.write("            return int(self.head_max_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("        if self.head_max_percentage is not None and self.photo_height_px > 0:\n") 
        fout.write("            return int(self.photo_height_px * self.head_max_percentage)\n")
        fout.write("        return None\n")
        fout.write("\n")
        fout.write("    # Eye line from bottom in pixels\n")
        fout.write("    @property\n")
        fout.write("    def eye_min_from_bottom_px(self) -> Optional[int]:\n")
        fout.write("        if self.eye_min_from_bottom_mm is not None and self.dpi != 0:\n")
        fout.write("            return int(self.eye_min_from_bottom_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("        return None\n")
        fout.write("\n")
        fout.write("    @property\n")
        fout.write("    def eye_max_from_bottom_px(self) -> Optional[int]:\n")
        fout.write("        if self.eye_max_from_bottom_mm is not None and self.dpi != 0:\n")
        fout.write("            return int(self.eye_max_from_bottom_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("        return None\n")
        fout.write("        \n")
        fout.write("    # Eye line from top in pixels (useful for direct conversion if spec provides this)\n")
        fout.write("    @property\n")
        fout.write("    def eye_min_from_top_px(self) -> Optional[int]:\n")
        fout.write("        if self.eye_min_from_top_mm is not None and self.dpi != 0:\n")
        fout.write("            return int(self.eye_min_from_top_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("        elif self.eye_max_from_bottom_px is not None and self.photo_height_px > 0:\n")
        fout.write("             return self.photo_height_px - self.eye_max_from_bottom_px\n")
        fout.write("        return None\n")
        fout.write("\n")
        fout.write("    @property\n")
        fout.write("    def eye_max_from_top_px(self) -> Optional[int]:\n")
        fout.write("        if self.eye_max_from_top_mm is not None and self.dpi != 0:\n")
        fout.write("            return int(self.eye_max_from_top_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("        elif self.eye_min_from_bottom_px is not None and self.photo_height_px > 0:\n")
        fout.write("            return self.photo_height_px - self.eye_min_from_bottom_px\n")
        fout.write("        return None\n")
        fout.write("\n")
        fout.write("    # Distance from top of head to top of photo in pixels\n")
        fout.write("    @property\n")
        fout.write("    def distance_top_of_head_to_top_of_photo_min_px(self) -> Optional[int]:\n")
        fout.write("        if self.distance_top_of_head_to_top_of_photo_min_mm is not None and self.dpi != 0:\n")
        fout.write("            return int(self.distance_top_of_head_to_top_of_photo_min_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("        return None\n")
        fout.write("\n")
        fout.write("    @property\n")
        fout.write("    def distance_top_of_head_to_top_of_photo_max_px(self) -> Optional[int]:\n")
        fout.write("        if self.distance_top_of_head_to_top_of_photo_max_mm is not None and self.dpi != 0:\n")
        fout.write("            return int(self.distance_top_of_head_to_top_of_photo_max_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("        return None\n")
        fout.write("\n")
        fout.write("    # Enhanced positioning control in pixels\n")
        fout.write("    @property\n")
        fout.write("    def head_top_min_dist_from_photo_top_px(self) -> Optional[int]:\n")
        fout.write("        if self.head_top_min_dist_from_photo_top_mm is not None and self.dpi != 0:\n")
        fout.write("            return int(self.head_top_min_dist_from_photo_top_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("        return None\n")
        fout.write("\n")
        fout.write("    @property\n")
        fout.write("    def head_top_max_dist_from_photo_top_px(self) -> Optional[int]:\n")
        fout.write("        if self.head_top_max_dist_from_photo_top_mm is not None and self.dpi != 0:\n")
        fout.write("            return int(self.head_top_max_dist_from_photo_top_mm / self.MM_PER_INCH * self.dpi)\n")
        fout.write("        return None\n\n")
        fout.write("DOCUMENT_SPECIFICATIONS: List[PhotoSpecification] = []\n\n")
        
        total_links = len(links)
        for i, (country, doc_text, url) in enumerate(links):
            print(f"Парсинг ({i+1}/{total_links}): {country} – {doc_text} ({url})")
            try:
                data_dict = parse_requirements_page(url)
                if not data_dict:
                    print(f"  Пропущено (данные не найдены или не удалось распарсить): {url}")
                    continue
                block = build_photo_spec_code(country, doc_text, data_dict, url)
                fout.write(block)
                specs_found += 1
            except requests.exceptions.RequestException as e:
                print(f"  Ошибка при запросе {url}: {e}")
            except Exception as e:
                print(f"  КРИТИЧЕСКАЯ ОШИБКА при обработке {country} - {doc_text} ({url}): {e}")
                traceback.print_exc() 
    print(f"Готово: файл {output_filename} создан. Собрано {specs_found} спецификаций.")

if __name__ == "__main__":
    main()
