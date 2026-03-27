import streamlit as st
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from io import BytesIO
import re
import tempfile
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image

st.set_page_config(page_title="RBD Formatter", layout="wide")
st.title("📚 RBD Publication – Smart Formatter")

# File uploader
uploaded_file = st.file_uploader("📄 Upload Chapter DOCX", type=["docx"])

# =============================================================================
# SIDEBAR – ALL CONTROLS
# =============================================================================
with st.sidebar:
    st.header("📄 Page Design")
    page_width = st.number_input("Page Width (inches)", 5.0, 12.0, 7.0, 0.1)
    page_height = st.number_input("Page Height (inches)", 6.0, 14.0, 9.0, 0.1)
    top_margin = st.number_input("Top Margin (inches)", 0.2, 1.0, 0.4, 0.05)
    bottom_margin = st.number_input("Bottom Margin (inches)", 0.2, 1.0, 0.4, 0.05)
    left_margin = st.number_input("Left Margin (inches)", 0.2, 1.0, 0.4, 0.05)
    right_margin = st.number_input("Right Margin (inches)", 0.2, 1.0, 0.4, 0.05)

    st.header("📐 Layout")
    num_columns = st.selectbox("Number of Columns", [2, 3], index=0)
    auto_fill = st.checkbox("Auto‑fill pages", True)
    if not auto_fill:
        questions_per_page = st.number_input("Fixed questions per page", 10, 100, 30, 5)

    st.header("✍️ Text Styling")
    q_font = st.slider("Question font size (pt)", 6.0, 12.0, 8.0, 0.5)
    q_indent = st.number_input("Content indent (inches)", 0.0, 0.8, 0.2, 0.05, 
                                help="Indentation for options, answer, and explanation")
    opt_font = st.slider("Options font size (pt)", 6.0, 11.0, 7.0, 0.5)
    opt_bold = st.checkbox("Bold options", False)
    ans_font = st.slider("Answer font size (pt)", 6.0, 11.0, 7.0, 0.5)
    ans_bold = st.checkbox("Bold answer", True)
    expl_font = st.slider("Explanation font size (pt)", 6.0, 10.0, 6.5, 0.5)

    st.header("📏 Spacing")
    line_spacing = st.slider("Line spacing (pt)", 8.0, 15.0, 9.0, 0.5)
    para_spacing = st.slider("Space after paragraph (pt)", 0.0, 6.0, 1.0, 0.5)
    char_spacing = st.slider("Character spacing (pt)", 0.0, 3.0, 0.0, 0.5)

    st.header("🎨 Option Wrapping")
    opts_per_line = st.selectbox("Max options per line", [2, 3, 4], index=0)
    if opts_per_line == 4:
        default_char_limit = 80
    elif opts_per_line == 3:
        default_char_limit = 68
    else:
        default_char_limit = 68
    opt_char_limit = st.slider("Option line length threshold", 40, 120, default_char_limit)

    st.header("📝 Header & Footer")
    header_template = st.text_input("Header template", "{book_name} | {chapter_title} | पृष्ठ {page}")
    book_name = st.text_input("Book name", "RBD PUBLICATION")
    header_font = st.slider("Header font size (pt)", 8.0, 16.0, 11.0, 0.5)
    header_bold = st.checkbox("Header bold", True)
    header_bg = st.checkbox("Header grey background", True)
    header_align = st.selectbox("Header alignment", ["Left", "Center", "Right"], index=1)

    st.header("🔢 Page Numbers")
    page_num_pos = st.selectbox("Position", ["None", "Top Left", "Top Center", "Top Right",
                                              "Bottom Left", "Bottom Center", "Bottom Right"], index=5)
    hide_on_first = st.checkbox("Hide on first page", False) if page_num_pos != "None" else False

    st.header("✨ Extras")
    show_correct_inline = st.checkbox("Show correct answer on last option line (right‑aligned)", True)
    show_separator = st.checkbox("Show line after each question", False)
    expl_bullet = st.checkbox("Bullet points in explanation", True)
    expl_bg = st.checkbox("Light grey background for explanation", True)

    # Compact mode override
    if st.checkbox("Extra compact mode", False):
        line_spacing = 9.0
        para_spacing = 1.0
        q_font = 8.0
        opt_font = 7.0
        ans_font = 7.0
        expl_font = 6.5

# =============================================================================
# PARSING
# =============================================================================
def parse_questions(doc):
    full_text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    questions = []
    blocks = re.split(r'(?=प्रश्न\s+\d+\b)', full_text)

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        hdr = re.match(r'प्रश्न\s+(\d+)\s*\n?', block)
        if not hdr:
            continue
        q_no = hdr.group(1)
        rest = block[hdr.end():]
        ans_split = re.split(r'\nउत्तर\s*:\s*', rest, maxsplit=1)
        before_ans = ans_split[0].strip()
        after_ans = ans_split[1].strip() if len(ans_split) > 1 else ""
        first_opt = re.search(r'\n?\(a\)', before_ans)
        if first_opt:
            question_text = before_ans[:first_opt.start()].strip().replace('\n', ' ')
            opts_raw = before_ans[first_opt.start():]
        else:
            question_text = before_ans.strip().replace('\n', ' ')
            opts_raw = ""
        options = []
        for m in re.finditer(r'\(([a-dA-D])\)\s*(.*?)(?=\s*\([a-dA-D]\)|$)', opts_raw, re.DOTALL):
            key = m.group(1).lower()
            text = m.group(2).strip().replace('\n', ' ')
            if text:
                options.append({"key": f"({key})", "text": text})
        ans_m = re.match(r'\((.+?)\)', after_ans)
        correct = f"({ans_m.group(1).strip()})" if ans_m else ""
        explanation_parts = []
        source_match = re.search(r'स्रोत/स्पष्टीकरण\s*:\s*(.*?)(?=अन्य महत्वपूर्ण तथ्य|स्पष्टीकरण\s*:|$)', after_ans, re.DOTALL | re.IGNORECASE)
        if source_match:
            source_text = source_match.group(1).strip()
            source_text = re.sub(r'\n+', ' ', source_text)
            if source_text:
                explanation_parts.append(f"स्रोत/स्पष्टीकरण: {source_text}")
        facts_match = re.search(r'अन्य महत्वपूर्ण तथ्य\s*:\s*(.*?)(?=प्रश्न\s+\d+|$)', after_ans, re.DOTALL | re.IGNORECASE)
        if facts_match:
            facts_text = facts_match.group(1).strip()
            facts_text = re.sub(r'\n+', ' ', facts_text)
            if facts_text:
                explanation_parts.append(f"अन्य महत्वपूर्ण तथ्य: {facts_text}")
        expl_match = re.search(r'स्पष्टीकरण\s*:\s*(.*?)(?=अन्य महत्वपूर्ण तथ्य|प्रश्न\s+\d+|$)', after_ans, re.DOTALL | re.IGNORECASE)
        if expl_match and not source_match:
            expl_text = expl_match.group(1).strip()
            expl_text = re.sub(r'\n+', ' ', expl_text)
            if expl_text:
                explanation_parts.append(f"स्पष्टीकरण: {expl_text}")
        explanation = " | ".join(explanation_parts) if explanation_parts else ""
        questions.append({
            "no": q_no,
            "question": question_text,
            "options": options,
            "correct": correct,
            "explanation": explanation.strip(),
        })
    return questions

# =============================================================================
# OPTION LAYOUT
# =============================================================================
def layout_options(opts, max_per_line=2, char_limit=68):
    result = []
    i = 0
    n = len(opts)
    while i < n:
        best = 1
        for k in range(max_per_line, 1, -1):
            if i + k <= n:
                combined = "    ".join(f"{opts[i+j]['key']} {opts[i+j]['text']}" for j in range(k))
                individual_ok = True
                for j in range(k):
                    if len(opts[i+j]['text']) > char_limit // 2:
                        individual_ok = False
                        break
                if len(combined) <= char_limit and individual_ok:
                    best = k
                    break
        group = [opts[i + j] for j in range(best)]
        result.append(group)
        i += best
    return result

# =============================================================================
# DOCX HELPERS
# =============================================================================
FONT_DOCX = "Mangal"

def set_spacing(para, line_pts, after_pts=0, before_pts=0):
    pPr = para._p.get_or_add_pPr()
    for old in pPr.findall(qn('w:spacing')):
        pPr.remove(old)
    s = OxmlElement('w:spacing')
    s.set(qn('w:line'), str(int(line_pts * 20)))
    s.set(qn('w:lineRule'), 'exact')
    s.set(qn('w:before'), str(int(before_pts * 20)))
    s.set(qn('w:after'), str(int(after_pts * 20)))
    pPr.append(s)

def set_char_spacing(run, spacing_pt):
    if spacing_pt > 0:
        rPr = run._r.get_or_add_rPr()
        spacing = OxmlElement('w:spacing')
        spacing.set(qn('w:val'), str(int(spacing_pt * 20)))
        rPr.append(spacing)

def set_paragraph_background(para, color_rgb):
    shading = OxmlElement('w:shd')
    shading.set(qn('w:val'), 'clear')
    shading.set(qn('w:color'), 'auto')
    shading.set(qn('w:fill'), color_rgb)
    pPr = para._p.get_or_add_pPr()
    pPr.append(shading)

def set_paragraph_indent(para, left_inches):
    if left_inches > 0:
        pPr = para._p.get_or_add_pPr()
        ind = OxmlElement('w:ind')
        ind.set(qn('w:left'), str(int(left_inches * 1440)))
        pPr.append(ind)

def set_hanging_indent(para, left_inches, first_line_inches):
    """Set hanging indent where first line is less indented than subsequent lines."""
    if left_inches > 0 or first_line_inches > 0:
        pPr = para._p.get_or_add_pPr()
        ind = OxmlElement('w:ind')
        if left_inches > 0:
            ind.set(qn('w:left'), str(int(left_inches * 1440)))
        if first_line_inches > 0:
            ind.set(qn('w:firstLine'), str(int(first_line_inches * 1440)))
        pPr.append(ind)

def no_border():
    return {"val": "nil"}

def set_cell_borders(cell, **kw):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    for old in tcPr.findall(qn('w:tcBorders')):
        tcPr.remove(old)
    tcB = OxmlElement('w:tcBorders')
    for edge, attrs in kw.items():
        tag = OxmlElement(f'w:{edge}')
        for k, v in attrs.items():
            tag.set(qn(f'w:{k}'), v)
        tcB.append(tag)
    tcPr.append(tcB)

def remove_cell_margins(cell):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    for old in tcPr.findall(qn('w:tcMar')):
        tcPr.remove(old)
    tcMar = OxmlElement('w:tcMar')
    for edge in ['top', 'left', 'bottom', 'right']:
        tag = OxmlElement(f'w:{edge}')
        tag.set(qn('w:w'), '0')
        tag.set(qn('w:type'), 'dxa')
        tcMar.append(tag)
    tcPr.append(tcMar)

def cell_para(cell, runs, line=10, after=1.5, before=0, bg_color=None, left_indent=0, first_line_indent=0):
    p = cell.add_paragraph()
    if left_indent > 0 or first_line_indent > 0:
        set_hanging_indent(p, left_indent, first_line_indent)
    for text, bold, size in runs:
        r = p.add_run(text)
        r.bold = bold
        r.font.size = Pt(size)
        r.font.name = FONT_DOCX
        if char_spacing > 0:
            set_char_spacing(r, char_spacing)
    if bg_color:
        set_paragraph_background(p, bg_color)
    set_spacing(p, line_pts=line, after_pts=after, before_pts=before)
    return p

def fill_cell(cell, q):
    for p in list(cell.paragraphs):
        p._p.getparent().remove(p._p)
    remove_cell_margins(cell)

    # Question with hanging indent: first line (question number) starts at left margin,
    # subsequent lines indented by q_indent
    q_text = f"{q['no']}. {q['question']}"
    cell_para(cell,
              [(q_text, True, q_font)],
              line=line_spacing, after=para_spacing, 
              left_indent=q_indent, first_line_indent=-q_indent)

    # Options (all indented by q_indent)
    option_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
    for idx, group in enumerate(option_groups):
        if len(group) == 1:
            text = f"{group[0]['key']} {group[0]['text']}"
        else:
            text = "    ".join(f"{opt['key']} {opt['text']}" for opt in group)
        
        # If this is the last group and inline answer is enabled, add answer right-aligned
        if show_correct_inline and idx == len(option_groups)-1:
            # Use a separate paragraph with right-aligned tab
            p = cell.add_paragraph()
            set_hanging_indent(p, q_indent, 0)  # Indent entire paragraph
            # Set tab stop at right margin
            tab_stops = p.paragraph_format.tab_stops
            tab_stops.add_tab_stop(Inches(6.0), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
            r = p.add_run(text + "\t" + q['correct'])
            r.bold = opt_bold
            r.font.size = Pt(opt_font)
            r.font.name = FONT_DOCX
            if char_spacing > 0:
                set_char_spacing(r, char_spacing)
            set_spacing(p, line_pts=line_spacing, after_pts=para_spacing)
        else:
            cell_para(cell, [(text, opt_bold, opt_font)], 
                      line=line_spacing, after=para_spacing, left_indent=q_indent)

    # Answer line (only if not shown inline)
    if not show_correct_inline:
        cell_para(cell,
                  [(f"उत्तर: {q['correct']}", ans_bold, ans_font)],
                  line=line_spacing, after=para_spacing, before=para_spacing, left_indent=q_indent)

    # Explanation with bullet (indented by q_indent)
    if q['explanation']:
        expl_text = q['explanation'].replace('|', '\n')
        if expl_bullet:
            expl_lines = expl_text.split('\n')
            expl_text = "\n".join(["• " + line for line in expl_lines])
        bg = "E6E6E6" if expl_bg else None
        cell_para(cell, [(expl_text, False, expl_font)],
                  line=line_spacing, after=para_spacing * 2, bg_color=bg, left_indent=q_indent)

    # Optional separator line
    if show_separator:
        p = cell.add_paragraph()
        r = p.add_run()
        r.add_break()
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '4')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), 'auto')
        pBdr.append(bottom)
        pPr.append(pBdr)
        set_spacing(p, line_pts=line_spacing, after_pts=2)

# =============================================================================
# DOCX PAGE GENERATION (unchanged)
# =============================================================================
def create_page_with_questions(questions, page_num, total_pages, chapter_title):
    new_doc = Document()
    sec = new_doc.sections[0]
    sec.page_width = Inches(page_width)
    sec.page_height = Inches(page_height)
    sec.top_margin = Inches(top_margin)
    sec.bottom_margin = Inches(bottom_margin)
    sec.left_margin = Inches(left_margin)
    sec.right_margin = Inches(right_margin)

    # Header
    header_text = header_template.format(book_name=book_name, chapter_title=chapter_title, page=page_num)
    header_para = new_doc.add_paragraph()
    if header_align == "Left":
        header_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    elif header_align == "Right":
        header_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    header_run = header_para.add_run(header_text)
    header_run.bold = header_bold
    header_run.font.size = Pt(header_font)
    header_run.font.name = FONT_DOCX
    if header_bg:
        set_paragraph_background(header_para, "E6E6E6")
    set_spacing(header_para, line_pts=header_font+2, after_pts=6)

    # Top page number
    if page_num_pos.startswith("Top") and not (hide_on_first and page_num == 1):
        top_para = new_doc.add_paragraph()
        if "Left" in page_num_pos:
            top_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif "Center" in page_num_pos:
            top_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            top_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        top_run = top_para.add_run(f"पृष्ठ {page_num}")
        top_run.font.size = Pt(9)
        set_spacing(top_para, line_pts=10, after_pts=3)

    # Multi‑column table
    content_width = page_width - left_margin - right_margin
    col_width = (content_width - (0.05 * (num_columns - 1))) / num_columns
    DIV = Inches(0.05)

    n = len(questions)
    per_col = (n + num_columns - 1) // num_columns
    cols = []
    for i in range(num_columns):
        start = i * per_col
        end = min((i + 1) * per_col, n)
        cols.append(questions[start:end])
    rows = max(len(col) for col in cols)
    tbl = new_doc.add_table(rows=rows, cols=num_columns * 2 - 1)
    tbl.autofit = False
    for i in range(num_columns):
        tbl.columns[i*2].width = Inches(col_width)
        if i < num_columns - 1:
            tbl.columns[i*2+1].width = DIV
    divider_border = {"val": "single", "sz": "4", "color": "AAAAAA", "space": "0"}
    for row_idx in range(rows):
        row = tbl.rows[row_idx]
        for col_idx in range(num_columns):
            cell = row.cells[col_idx*2]
            cell.width = Inches(col_width)
            if row_idx < len(cols[col_idx]):
                fill_cell(cell, cols[col_idx][row_idx])
            set_cell_borders(cell, top=no_border(), bottom=no_border(),
                             left=no_border() if col_idx==0 else divider_border,
                             right=divider_border if col_idx < num_columns-1 else no_border())
            if col_idx < num_columns - 1:
                div_cell = row.cells[col_idx*2+1]
                div_cell.width = DIV
                set_cell_borders(div_cell, top=no_border(), bottom=no_border(),
                                 left=no_border(), right=no_border())

    # Bottom page number
    if page_num_pos.startswith("Bottom") and not (hide_on_first and page_num == 1):
        bottom_para = new_doc.add_paragraph()
        if "Left" in page_num_pos:
            bottom_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif "Center" in page_num_pos:
            bottom_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            bottom_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        bottom_run = bottom_para.add_run(f"पृष्ठ {page_num}")
        bottom_run.font.size = Pt(9)
        set_spacing(bottom_para, line_pts=10, before_pts=5)

    if page_num < total_pages:
        new_doc.add_page_break()
    return new_doc

def generate_multi_page_docx(questions, chapter_title, q_per_page=None):
    if q_per_page is None:
        sample = min(10, len(questions))
        total_lines = 0
        for q in questions[:sample]:
            lines = 1  # question
            opt_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
            lines += len(opt_groups)
            if not show_correct_inline:
                lines += 1  # answer
            if q['explanation']:
                lines += len(q['explanation'].split('|'))
            total_lines += lines
        avg_lines = total_lines / sample if sample > 0 else 10
        usable_height = page_height - top_margin - bottom_margin - 1.2
        lines_per_page = usable_height / (line_spacing / 72.0)
        q_per_page = int(lines_per_page / avg_lines)
        q_per_page = max(1, q_per_page)
    total_pages = (len(questions) + q_per_page - 1) // q_per_page
    final_doc = None
    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * q_per_page
        end = min(start + q_per_page, len(questions))
        page_questions = questions[start:end]
        page_doc = create_page_with_questions(page_questions, page_num, total_pages, chapter_title)
        if final_doc is None:
            final_doc = page_doc
        else:
            for element in page_doc.element.body:
                final_doc.element.body.append(element)
    return final_doc

# =============================================================================
# HTML PREVIEW (with proper hanging indent)
# =============================================================================
def render_q_preview(q):
    option_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
    opts_html = ""
    for idx, group in enumerate(option_groups):
        if len(group) == 1:
            line = f"{group[0]['key']} {group[0]['text']}"
        else:
            line = "&nbsp;&nbsp;&nbsp;&nbsp;".join(f"{opt['key']} {opt['text']}" for opt in group)
        if show_correct_inline and idx == len(option_groups)-1:
            # Use CSS flexbox to place answer on the right
            opts_html += f"<div style='display: flex; justify-content: space-between;'><span>{line}</span><span>{q['correct']}</span></div>"
        else:
            opts_html += f"<div>{line}</div>"

    expl = q['explanation'].replace('|', '<br>')
    if expl_bullet:
        expl = "• " + expl.replace('<br>', '<br>• ')
    expl_style = f"background-color: #F5F5F5; padding: 2px 4px; border-radius: 3px;" if expl_bg else ""

    # Hanging indent: question number at left, text indented
    q_text = f"<b>{q['no']}.</b> {q['question']}"
    
    return f"""
<div class="qblock">
  <div class="qtext" style="margin-left: {q_indent*96}px; text-indent: -{q_indent*96}px;">{q_text}</div>
  <div class="qopts" style="margin-left: {q_indent*96}px; font-size: {opt_font}pt;">{opts_html}</div>
  <div class="qans" style="margin-left: {q_indent*96}px; font-size: {ans_font}pt;">{'<b>उत्तर: ' + q['correct'] + '</b>' if not show_correct_inline else ''}</div>
  <div class="qexpl" style="margin-left: {q_indent*96}px; font-size: {expl_font}pt; {expl_style}">{expl}</div>
  {('<hr>' if show_separator else '')}
</div>"""

def build_preview_with_pagination(questions, q_per_page, chapter_title):
    total_pages = (len(questions) + q_per_page - 1) // q_per_page
    pages_html = []
    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * q_per_page
        end = min(start + q_per_page, len(questions))
        page_questions = questions[start:end]
        per_col = (len(page_questions) + num_columns - 1) // num_columns
        cols = []
        for i in range(num_columns):
            start_col = i * per_col
            end_col = min((i+1) * per_col, len(page_questions))
            cols.append(page_questions[start_col:end_col])

        col_html = []
        for col in cols:
            col_content = "".join(render_q_preview(q) for q in col)
            col_html.append(f"<div class='col'>{col_content}</div>")

        page_html = f"""
<div class="page">
  <div class="page-header" style="background-color: #E6E6E6; padding: 4px; border-radius: 3px; text-align: center; font-weight: bold;">
    {header_template.format(book_name=book_name, chapter_title=chapter_title, page=page_num)}
  </div>
  <div class="columns">
    {''.join(f"<div class='column'>{col_html[i]}</div>" for i in range(num_columns))}
  </div>
</div>
"""
        pages_html.append(page_html)

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #666; font-family: 'Arial', sans-serif; padding: 20px; }}
  .page {{
    width: {page_width*96}px; min-height: {page_height*96}px; background: white; margin: 0 auto 20px auto;
    padding: {top_margin*96}px {right_margin*96}px {bottom_margin*96}px {left_margin*96}px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
    page-break-after: always;
  }}
  .columns {{
    display: grid;
    grid-template-columns: repeat({num_columns}, 1fr);
    gap: 20px;
    align-items: start;
  }}
  .column {{
    padding: 0 5px;
  }}
  .qblock {{ margin-bottom: 8px; padding-bottom: 7px; }}
  .qtext {{ font-size: {q_font}pt; margin-bottom: 3px; line-height: {line_spacing/72}in; }}
  .qopts {{ color: #222; margin-bottom: 2px; line-height: {line_spacing/72}in; }}
  .qans {{ font-weight: bold; margin: 3px 0 1px; }}
  .qexpl {{ color: #444; margin-top: 2px; }}
  hr {{ margin: 5px 0; border: 0; border-top: 1px dotted #ccc; }}
</style>
</head><body>
{''.join(pages_html)}
</body></html>"""

def extract_chapter_title(doc):
    for para in doc.paragraphs[:10]:
        if "अध्याय" in para.text or "CHAPTER" in para.text.upper():
            title = para.text.strip()
            if len(title) > 80:
                title = title[:80] + "..."
            return title
    return "RBD PUBLICATION — अध्याय"

# =============================================================================
# PDF GENERATION (simplified, with hanging indent)
# =============================================================================
def register_devanagari_font():
    possible_paths = [
        "C:/Windows/Fonts/Mangal.ttf",
        "C:/Windows/Fonts/Nirmala.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Mangal.ttf",
        "/usr/share/fonts/truetype/lohit/Lohit-Devanagari.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('Devanagari', path))
                return 'Devanagari'
            except:
                continue
    st.warning("⚠️ No Devanagari font found. PDF will use Helvetica.")
    return 'Helvetica'

def generate_pdf(questions, chapter_title):
    devanagari_font = register_devanagari_font()
    p_width = page_width * inch
    p_height = page_height * inch
    m_top = top_margin * inch
    m_bottom = bottom_margin * inch
    m_left = left_margin * inch
    m_right = right_margin * inch

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(p_width, p_height),
                            topMargin=m_top, bottomMargin=m_bottom,
                            leftMargin=m_left, rightMargin=m_right)
    styles = getSampleStyleSheet()
    story = []

    # Define styles with left margin for indentation
    style_q = ParagraphStyle('Question', parent=styles['Normal'], fontSize=q_font, leading=line_spacing,
                             fontName=devanagari_font, alignment=TA_LEFT, spaceAfter=para_spacing,
                             leftIndent=q_indent*inch, firstLineIndent=-q_indent*inch)
    style_opt = ParagraphStyle('Options', parent=styles['Normal'], fontSize=opt_font, leading=line_spacing,
                               fontName=devanagari_font, alignment=TA_LEFT, spaceAfter=para_spacing,
                               leftIndent=q_indent*inch)
    style_opt_right = ParagraphStyle('OptionsRight', parent=styles['Normal'], fontSize=opt_font, leading=line_spacing,
                                     fontName=devanagari_font, alignment=TA_RIGHT, spaceAfter=para_spacing,
                                     leftIndent=q_indent*inch)
    style_ans = ParagraphStyle('Answer', parent=styles['Normal'], fontSize=ans_font, leading=line_spacing,
                               fontName=devanagari_font, alignment=TA_LEFT, spaceAfter=para_spacing,
                               spaceBefore=para_spacing, leftIndent=q_indent*inch)
    style_expl = ParagraphStyle('Explanation', parent=styles['Normal'], fontSize=expl_font, leading=line_spacing,
                                fontName=devanagari_font, alignment=TA_LEFT,
                                backColor=colors.HexColor('#F5F5F5') if expl_bg else None,
                                spaceAfter=para_spacing*2, leftIndent=q_indent*inch,
                                bulletText='•' if expl_bullet else None)
    style_h = ParagraphStyle('Header', parent=styles['Normal'], fontSize=header_font, leading=header_font+2,
                             fontName=devanagari_font, alignment=TA_CENTER,
                             backColor=colors.HexColor('#E6E6E6') if header_bg else None,
                             spaceAfter=6)

    # Header
    header_text = header_template.format(book_name=book_name, chapter_title=chapter_title, page=1)
    story.append(Paragraph(header_text, style_h))

    # PDF pagination
    for q in questions:
        story.append(Paragraph(f"{q['no']}. {q['question']}", style_q))
        opt_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
        for idx, group in enumerate(opt_groups):
            if len(group) == 1:
                line = f"{group[0]['key']} {group[0]['text']}"
            else:
                line = "    ".join(f"{opt['key']} {opt['text']}" for opt in group)
            if show_correct_inline and idx == len(opt_groups)-1:
                story.append(Paragraph(line, style_opt))
                story.append(Paragraph(q['correct'], style_opt_right))
            else:
                story.append(Paragraph(line, style_opt))
        if not show_correct_inline:
            story.append(Paragraph(f"<b>उत्तर: {q['correct']}</b>", style_ans))
        if q['explanation']:
            expl_text = q['explanation'].replace('|', '<br/>')
            if expl_bullet:
                expl_text = "• " + expl_text.replace('<br/>', '<br/>• ')
            story.append(Paragraph(expl_text, style_expl))
        if show_separator:
            story.append(Spacer(1, 2))
            story.append(Paragraph("<hr/>", style_q))
            story.append(Spacer(1, 2))

    doc.build(story)
    buffer.seek(0)
    return buffer

# =============================================================================
# MAIN APP
# =============================================================================
if uploaded_file:
    doc = Document(uploaded_file)
    with st.spinner("Parsing questions..."):
        questions = parse_questions(doc)
        chapter_title = extract_chapter_title(doc)
    st.success(f"✅ {len(questions)} questions parsed!")

    # Estimate pages
    if auto_fill:
        sample_size = min(10, len(questions))
        total_lines = 0
        for q in questions[:sample_size]:
            lines = 1
            opt_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
            lines += len(opt_groups)
            if not show_correct_inline:
                lines += 1
            if q['explanation']:
                lines += 1
            total_lines += lines
        avg_lines = total_lines / sample_size if sample_size > 0 else 10
        usable_height = page_height - top_margin - bottom_margin - 1.2
        lines_per_page = usable_height / (line_spacing / 72.0)
        q_per_page_est = int(lines_per_page / avg_lines)
        total_pages_est = (len(questions) + q_per_page_est - 1) // q_per_page_est
    else:
        total_pages_est = (len(questions) + questions_per_page - 1) // questions_per_page
        q_per_page_est = questions_per_page

    st.info(f"📄 Estimated pages: {total_pages_est} ({'auto' if auto_fill else 'fixed'})")

    tab1, tab2 = st.tabs(["📄 Page Preview", "🔍 Parsed Data"])
    with tab1:
        preview_html = build_preview_with_pagination(questions, q_per_page_est, chapter_title)
        st.components.v1.html(preview_html, height=1200, scrolling=True)

    with tab2:
        for q in questions[:5]:
            with st.expander(f"Q{q['no']} – {q['question'][:60]}…"):
                st.write("**Options:**", q['options'])
                st.write("**Answer:**", q['correct'])
                st.write("**Explanation:**", q['explanation'][:500])

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Generate DOCX"):
            with st.spinner("Generating DOCX..."):
                final_doc = generate_multi_page_docx(questions, chapter_title, None if auto_fill else questions_per_page)
                filename = f"Formatted_Output_{len(questions)}Q.docx"
                final_doc.save(filename)
                with open(filename, "rb") as f:
                    st.download_button("📥 Download DOCX", f, filename,
                                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                st.success("🎉 DOCX ready!")
    with col2:
        if st.button("📑 Preview PDF"):
            with st.spinner("Generating PDF preview..."):
                pdf_buffer = generate_pdf(questions, chapter_title)
                base64_pdf = pdf_buffer.getvalue().encode("base64").decode()
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                st.download_button("📥 Download PDF", pdf_buffer, file_name="Formatted_Output.pdf",
                                   mime="application/pdf")
                st.success("🎉 PDF preview ready!")