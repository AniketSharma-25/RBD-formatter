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
import base64
from reportlab.lib import colors
from reportlab.lib.pagesizes import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage

def is_matching_question(text):
    if not text:
        return False

    return (
        "सूची" in text and
        re.search(r'[A-D]\.', text) and
        re.search(r'[1-4]\.', text)
    )
def format_suchi_question(text):
    if not text:
        return text

    text = re.sub(r'\s+', ' ', text)

    # Split header and rest
    parts = re.split(r'(A\.)', text, maxsplit=1)

    if len(parts) < 3:
        return text

    header = parts[0].strip()
    rest = "A." + parts[2]

    # Extract A-D
    left = re.findall(r'([A-D]\.\s*.*?)(?=\s*[A-D]\.|$)', rest)

    # Extract 1-4
    right = re.findall(r'([1-4]\.\s*.*?)(?=\s*[1-4]\.|$)', rest)

    left = [l.strip() for l in left]
    right = [r.strip() for r in right]

    lines = [header, ""]

    if len(left) == len(right) and len(left) > 0:
        for l, r in zip(left, right):
            lines.append(f"{l}    {r}")

    # Add कूट:
    if "कूट:" in text:
        lines.append("")
        lines.append("कूट:")
        after = text.split("कूट:")[-1].strip()
        lines.append(after)

    return "\n".join(lines).strip()

def clean_text(text):
    if not text:
        return ""

    # Remove metadata
    text = re.sub(r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)', '', text)

    # 🔥 REMOVE TABS (MAIN FIX)
    text = text.replace('\t', ' ')

    # Remove extra spaces/newlines
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

def format_matching_question(text):
    if not text:
        return text

    text = re.sub(r'\s+', ' ', text).strip()

    # Detect matching question pattern
    if not re.search(r'सूची|सुमेलित|Match|Column', text, re.IGNORECASE):
        return text

    # Extract header line (e.g., "सूची-I को सूची-II से सुमेलित कीजिए:")
    header_match = re.match(r'(.*?(?:कीजिए|करें|करो)\s*:?)', text, re.IGNORECASE)
    header = header_match.group(1).strip() if header_match else ""
    rest = text[len(header):].strip() if header else text

    # Extract column headers (e.g., "सूची-I (बल की स्थिति) सूची-II (परिणाम/प्रभाव)")
    col_header_match = re.match(
        r'(सूची-I\s*(?:\(.*?\))?)\s+(सूची-II\s*(?:\(.*?\))?)', rest, re.IGNORECASE
    )
    col_header = ""
    if col_header_match:
        col_header = f"{col_header_match.group(1).strip()}    {col_header_match.group(2).strip()}"
        rest = rest[col_header_match.end():].strip()

    # Extract A-D items
    left_items = re.findall(r'([A-D])\.\s*(.*?)(?=\s*[A-D]\.\s|\s*[1-4]\.\s|कूट|$)', rest)

    # Extract 1-4 items
    right_items = re.findall(r'([1-4])\.\s*(.*?)(?=\s*[A-D]\.\s|\s*[1-4]\.\s|कूट|$)', rest)

    # Extract कूट section
    koot_match = re.search(r'(कूट\s*:?\s*.*)', rest, re.DOTALL)
    koot_text = koot_match.group(1).strip() if koot_match else ""

    # Build formatted output
    lines = []
    if header:
        lines.append(header)
    if col_header:
        lines.append(col_header)

    # Pair A-D with 1-4 side by side
    max_pairs = max(len(left_items), len(right_items))
    for i in range(max_pairs):
        left = f"{left_items[i][0]}. {left_items[i][1].strip()}" if i < len(left_items) else ""
        right = f"{right_items[i][0]}. {right_items[i][1].strip()}" if i < len(right_items) else ""
        if left and right:
            lines.append(f"{left}    {right}")
        elif left:
            lines.append(left)
        elif right:
            lines.append(right)

    if koot_text:
        lines.append(koot_text)

    result = "\n".join(lines)
    return result if result.strip() else text

    
st.set_page_config(page_title="RBD Formatter", layout="wide")
st.title("📚 RBD Publication – Smart Formatter")

uploaded_file = st.file_uploader("📄 Upload Chapter DOCX", type=["docx"])

# =============================================================================
# SIDEBAR
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

    st.header("✍️ Text Styling")
    q_font = st.slider("Question font size (pt)", 5.0, 12.0, 5.5, 0.5)

    st.markdown("**Indent levels**")
    st.caption("Level-1: question number '1.' and bullet '•' sit here")
    level1_indent = st.number_input("Level-1 indent (inches)", 0.0, 0.5, 0.0, 0.05)
    st.caption("Level-2: all content text starts here (question text, options, explanation)")
    level2_indent = st.number_input("Level-2 indent (inches)", 0.05, 1.0, 0.15, 0.05)

    # alias used elsewhere
    q_indent = level2_indent

    opt_font = st.slider("Options font size (pt)", 5.0, 11.0, 5.5, 0.5)
    opt_bold = st.checkbox("Bold options", False)
    ans_font = st.slider("Answer font size (pt)", 5.0, 11.0, 5.5, 0.5)
    ans_bold = st.checkbox("Bold answer", False)
    expl_font = st.slider("Explanation font size (pt)", 5.0, 10.0, 5.5, 0.5)

    st.header("📏 Spacing")
    line_spacing = st.slider("Line spacing (pt)", 5.0, 15.0, 5.0, 0.5)
    para_spacing = st.slider("Space after paragraph (pt)", 0.0, 6.0, 0.0, 0.5)
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
    expl_bullet = st.checkbox("Bullet before व्याख्या heading", True)
    expl_bg = st.checkbox("Light grey background for explanation", True)

    if st.checkbox("Extra compact mode", False):
        line_spacing = 5.0
        para_spacing = 0.0
        q_font = 5.0
        opt_font = 5.0
        ans_font = 5.0
        expl_font = 5.0

# =============================================================================
# PARSING (unchanged)
# =============================================================================
def parse_questions(doc):
    import io
    questions = []
    current_block = []
    inside_question = False

    def is_question_start(text):
        return re.match(r'प्रश्न\s+\d+', text) or re.match(r'\d+\.\s', text)

    def extract_images_from_para(para):
        images = []
        for run in para.runs:
            for blip in run._element.findall(
                    './/a:blip',
                    namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}):
                rId = blip.get(qn('r:embed'))
                image_part = doc.part.related_parts[rId]
                img_bytes = image_part.blob
                width_in = height_in = 1.0
                extent = run._element.find(
                    './/wp:extent',
                    namespaces={'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'})
                if extent is not None:
                    width_in = int(extent.get('cx')) / 914400.0
                    height_in = int(extent.get('cy')) / 914400.0
                else:
                    try:
                        pil_img = PILImage.open(io.BytesIO(img_bytes))
                        width_in = pil_img.width / 96.0
                        height_in = pil_img.height / 96.0
                    except Exception:
                        pass
                images.append((img_bytes, width_in, height_in))
        return images

    for para in doc.paragraphs:
        text = para.text.strip()
        images = extract_images_from_para(para)
        if is_question_start(text):
            if current_block:
                q = process_question_block(current_block)
                if q:
                    q['no'] = str(len(questions) + 1)
                    questions.append(q)
            current_block = []
            inside_question = True
        if inside_question:
            current_block.append((text, images))
    if current_block:
        q = process_question_block(current_block)
        if q:
            questions.append(q)
    return questions


def remove_metadata_pattern(text):
    # Strong pattern to remove exam metadata
    pattern = r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)'
    return re.sub(pattern, '', text).strip()


def process_question_block(block):
    full_text = "\n".join(txt for txt, _ in block)

    # ---------- QUESTION NUMBER ----------
    if re.search(r'प्रश्न\s+\d+', full_text):
        hdr = re.match(r'प्रश्न\s+(\d+)\s*\n?', full_text)
        if not hdr:
            return None
        q_no = hdr.group(1)
        rest = full_text[hdr.end():]
    else:
        hdr = re.match(r'(\d+)\.\s*', full_text)
        if not hdr:
            return None
        q_no = hdr.group(1)
        rest = full_text[hdr.end():]

    # ❌ REMOVE OLD METADATA LOGIC COMPLETELY
    # metadata = ""
    # (no need to extract anymore)

    # ---------- ANSWER SPLIT ----------
    ans_match = re.search(r'(सही उत्तर|उत्तर)\s*:\s*(.*?)(?=\n\s*\n|\n\d+\.|$)',
                         rest, re.IGNORECASE | re.DOTALL)

    if ans_match:
        before_ans = rest[:ans_match.start()].strip()
        after_ans = ans_match.group(2).strip()
    else:
        before_ans = rest.strip()
        after_ans = ""

    # ---------- CLEAN QUESTION TEXT ----------
    first_opt = re.search(r'\n?\(a\)', before_ans, re.IGNORECASE)

    if first_opt:
        question_text = before_ans[:first_opt.start()].strip().replace('\n', ' ')
        opts_raw = before_ans[first_opt.start():]
    else:
        question_text = before_ans.strip().replace('\n', ' ')
        opts_raw = ""

    # 🔥 REMOVE METADATA FROM QUESTION
    raw_q = clean_text(
        before_ans[:first_opt.start()] if first_opt else before_ans
    )

# 🔥 APPLY ONLY WHEN NEEDED
    if is_matching_question(raw_q):
        question_text = format_suchi_question(raw_q)
    else:
        question_text = raw_q

    # ---------- OPTIONS ----------
    options = []
    for m in re.finditer(r'\(([a-dA-D])\)\s*(.*?)(?=\s*\([a-dA-D]\)|$)', opts_raw, re.DOTALL):
        key = m.group(1).lower()
        text = clean_text(m.group(2)) # 🔥 clean options too
        if text:
            options.append({"key": f"({key})", "text": text})

    # ---------- CORRECT ANSWER ----------
    correct = ""
    if after_ans:
        m = re.match(r'\(([a-dA-D])\)', after_ans)
        if m:
            correct = f"({m.group(1).lower()})"
        else:
            m2 = re.search(r'\(([a-dA-D])\)', after_ans)
            if m2:
                correct = f"({m2.group(1).lower()})"

    # ---------- EXPLANATION ----------
    explanation_text = ""

    expl_match = re.search(r'व्याख्या\s*:\s*(.*?)(?=\n\d+\.|$)',
                           after_ans, re.DOTALL | re.IGNORECASE)

    if expl_match:
        explanation_text = clean_text(expl_match.group(1))
    else:
        source = facts = ""

        sm = re.search(r'स्रोत/स्पष्टीकरण\s*:\s*(.*?)(?=अन्य महत्वपूर्ण तथ्य|$)',
                       after_ans, re.DOTALL | re.IGNORECASE)
        fm = re.search(r'अन्य महत्वपूर्ण तथ्य\s*:\s*(.*?)(?=$)',
                       after_ans, re.DOTALL | re.IGNORECASE)

        if sm:
            source = sm.group(1).strip().replace('\n', ' ')
        if fm:
            facts = fm.group(1).strip().replace('\n', ' ')

        if source or facts:
            explanation_text = " | ".join(filter(None, [source, facts]))
        else:
            er = re.search(r'(.*?)(?=\n\d+\.|$)', after_ans, re.DOTALL)
            if er:
                explanation_text = er.group(1).strip().replace('\n', ' ')

    # 🔥 CLEAN EXPLANATION
    explanation_text = remove_metadata_pattern(explanation_text)

    # ---------- IMAGES ----------
    answer_idx = -1
    for idx, (txt, _) in enumerate(block):
        if re.search(r'(सही उत्तर|उत्तर)\s*:', txt, re.IGNORECASE):
            answer_idx = idx
            break

    explanation_images = []
    src = block[answer_idx+1:] if answer_idx != -1 else block

    for _, imgs in src:
        explanation_images.extend(imgs)

    # ---------- FINAL RETURN ----------
    return {
        "no": q_no,
        "question": question_text,
        "options": options,
        "correct": correct,
        "explanation": explanation_text,
        "explanation_images": explanation_images,
        "metadata": ""  # 🔥 always empty now
    }
# =============================================================================
# OPTION LAYOUT (unchanged)
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
                ok = all(len(opts[i+j]['text']) <= char_limit // 2 for j in range(k))
                if len(combined) <= char_limit and ok:
                    best = k
                    break
        result.append([opts[i+j] for j in range(best)])
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
        sp = OxmlElement('w:spacing')
        sp.set(qn('w:val'), str(int(spacing_pt * 20)))
        rPr.append(sp)

def set_paragraph_background(para, color_rgb):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_rgb)
    pPr = para._p.get_or_add_pPr()
    pPr.append(shd)

def _apply_ind(para, left_twips, first_twips):
    pPr = para._p.get_or_add_pPr()
    for old in pPr.findall(qn('w:ind')):
        pPr.remove(old)
    ind = OxmlElement('w:ind')
    ind.set(qn('w:left'), str(left_twips))
    if first_twips != 0:
        ind.set(qn('w:firstLine'), str(first_twips))
    pPr.append(ind)

def set_two_level_indent(para, l1_in, l2_in):
    left_twips = int(l2_in * 1440)
    first_twips = int((l1_in - l2_in) * 1440)
    _apply_ind(para, left_twips, first_twips)

def set_left_indent(para, left_in):
    _apply_ind(para, int(left_in * 1440), 0)

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

def add_run(para, text, bold=False, size_pt=8, italic=False):
    r = para.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.size = Pt(size_pt)
    r.font.name = FONT_DOCX
    if char_spacing > 0:
        set_char_spacing(r, char_spacing)
    return r

# =============================================================================
# FILL CELL – explanation uses two‑level indent
# =============================================================================

# Tab system for alignment
    tab_stops = p_q.paragraph_format.tab_stops

# 👉 Content alignment (Level-2)
    tab_stops.add_tab_stop(Inches(level2_indent), WD_TAB_ALIGNMENT.LEFT)

# 👉 Right side metadata alignment (dynamic width)
    content_width = page_width - left_margin - right_margin
    col_gap = 0.08 if num_columns == 3 else 0.12
    col_width = (content_width - col_gap * (num_columns - 1)) / num_columns

    tab_stops.add_tab_stop(Inches(col_width - 0.1), WD_TAB_ALIGNMENT.RIGHT)

# Number
    add_run(p_q, f"{q['no']}.", bold=True, size_pt=q_font)

# Move to content column
    p_q.add_run("\t")

# Question text
    add_run(p_q, q['question'], bold=True, size_pt=q_font)

# # 👉 Move to right corner
#     if q.get('metadata'):
#         p_q.add_run("\t")
#         add_run(p_q, q['metadata'], bold=False, size_pt=6.5)

    set_spacing(p_q, line_pts=line_spacing, after_pts=para_spacing)
   
    # Question
    # p_q = cell.add_paragraph()
    # set_two_level_indent(p_q, level1_indent, level2_indent)
    # add_run(p_q, f"{q['no']}. ", bold=True, size_pt=q_font)
    # add_run(p_q, q['question'], bold=True, size_pt=q_font)
    # set_spacing(p_q, line_pts=line_spacing, after_pts=para_spacing)

    # Metadata
    # if q.get('metadata'):
    #     p_m = cell.add_paragraph()
    #     p_m.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    #     set_left_indent(p_m, level2_indent)
    #     add_run(p_m, q['metadata'], bold=False, size_pt=6.0)
    #     set_spacing(p_m, line_pts=line_spacing, after_pts=para_spacing)

    # Options
    option_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
    for idx, group in enumerate(option_groups):
        text = ("    ".join(f"{o['key']} {o['text']}" for o in group)
                if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
        is_last = (idx == len(option_groups) - 1)

        p_opt = cell.add_paragraph()
        set_left_indent(p_opt, level2_indent)

        if show_correct_inline and is_last:
            add_run(p_opt, text, bold=opt_bold, size_pt=opt_font)
            tab_stops = p_opt.paragraph_format.tab_stops
            tab_stops.add_tab_stop(Inches(3.2), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)
            p_opt.add_run("\t")
            add_run(p_opt, q['correct'], bold=True, size_pt=opt_font + 1.5)
        else:
            add_run(p_opt, text, bold=opt_bold, size_pt=opt_font)

        set_spacing(p_opt, line_pts=line_spacing, after_pts=para_spacing)

    # Explanation – single paragraph with two‑level indent
    # Explanation – aligned with tab system
    if q['explanation'] or q.get('explanation_images'):
        p_expl = cell.add_paragraph()

        # Create tab alignment for content
        tab_stops = p_expl.paragraph_format.tab_stops
        tab_stops.add_tab_stop(Inches(level2_indent), WD_TAB_ALIGNMENT.LEFT)

        if expl_bg:
            set_paragraph_background(p_expl, "E6E6E6")

        # Arrow / bullet
        add_run(p_expl, "➤", bold=True, size_pt=expl_font)

        # Move to aligned content position
        p_expl.add_run("\t")

    # Heading + content~
        add_run(p_expl, "व्याख्या: ", bold=True, size_pt=expl_font)

        if q['explanation']:
            add_run(p_expl, q['explanation'].replace('|', '\n'),
                bold=False, size_pt=expl_font)

        set_spacing(p_expl, line_pts=line_spacing, after_pts=para_spacing * 2)

        # Images after the text (separate paragraphs)
        for img_bytes, width_in, height_in in q.get('explanation_images', []):
            inserted = False
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    tmp.write(img_bytes)
                    tmp_path = tmp.name
                content_w = page_width - left_margin - right_margin
                col_gap = 0.08 if num_columns == 3 else 0.12
                col_w = (content_w - col_gap * (num_columns - 1)) / num_columns
                max_img_w = col_w - level2_indent - 0.05
                img_w = min(width_in if width_in > 0 else 1.5, max_img_w)
                p_img = cell.add_paragraph()
                set_left_indent(p_img, level2_indent)
                p_img.add_run().add_picture(tmp_path, width=Inches(img_w))
                os.unlink(tmp_path)
                set_spacing(p_img, line_pts=line_spacing, after_pts=para_spacing)
                inserted = True
            except Exception:
                pass
            if not inserted:
                p_ph = cell.add_paragraph()
                set_left_indent(p_ph, level2_indent)
                add_run(p_ph, "[चित्र यहाँ संलग्न करें]", bold=False, size_pt=expl_font, italic=True)
                if expl_bg:
                    set_paragraph_background(p_ph, "E6E6E6")
                set_spacing(p_ph, line_pts=line_spacing * 3, after_pts=para_spacing)

    # Separator line
    if show_separator:
        p_sep = cell.add_paragraph()
        pPr = p_sep._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bt = OxmlElement('w:bottom')
        bt.set(qn('w:val'), 'single')
        bt.set(qn('w:sz'), '4')
        bt.set(qn('w:space'), '1')
        bt.set(qn('w:color'), 'auto')
        pBdr.append(bt)
        pPr.append(pBdr)
        set_spacing(p_sep, line_pts=line_spacing, after_pts=2)

# =============================================================================
# ESTIMATE QUESTION HEIGHT (unchanged)
# =============================================================================
def fill_cell(cell, q):
    for p in list(cell.paragraphs):
        p._p.getparent().remove(p._p)
    remove_cell_margins(cell)

    # =========================
    # QUESTION (FIXED ALIGNMENT)
    # =========================
    p_q = cell.add_paragraph()

    p_format = p_q.paragraph_format
    p_format.left_indent = Inches(level2_indent)
    p_format.first_line_indent = Inches(level1_indent - level2_indent)

    add_run(p_q, f"{q['no']}. ", bold=True, size_pt=q_font)
    for i, line in enumerate(q['question'].split('\n')):
        if i > 0:
            p_q.add_run("\n")
        add_run(p_q, line, bold=True, size_pt=q_font)

    set_spacing(p_q, line_pts=line_spacing, after_pts=para_spacing)

    # =========================
    # OPTIONS
    # =========================
    option_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)

    for idx, group in enumerate(option_groups):
        text = ("    ".join(f"{o['key']} {o['text']}" for o in group)
                if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
        is_last = (idx == len(option_groups) - 1)

        p_opt = cell.add_paragraph()
        p_opt.paragraph_format.left_indent = Inches(level2_indent)

        if show_correct_inline and is_last:
            add_run(p_opt, text, bold=opt_bold, size_pt=opt_font)

            tab_stops = p_opt.paragraph_format.tab_stops
            tab_stops.add_tab_stop(Inches(3.2), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.SPACES)

            p_opt.add_run("\t")
            add_run(p_opt, q['correct'], bold=True, size_pt=opt_font + 1.5)
        else:
            add_run(p_opt, text, bold=opt_bold, size_pt=opt_font)

        set_spacing(p_opt, line_pts=line_spacing, after_pts=para_spacing)

    # =========================
    # EXPLANATION (FIXED ALIGNMENT)
    # =========================
    if q['explanation'] or q.get('explanation_images'):

        p_expl = cell.add_paragraph()

        p_format = p_expl.paragraph_format
        p_format.left_indent = Inches(level2_indent)
        p_format.first_line_indent = Inches(level1_indent - level2_indent)

        if expl_bg:
            set_paragraph_background(p_expl, "E6E6E6")

        add_run(p_expl, "➤ ", bold=True, size_pt=expl_font)
        add_run(p_expl, "व्याख्या: ", bold=True, size_pt=expl_font)

        if q['explanation']:
            add_run(p_expl, q['explanation'], size_pt=expl_font)

        set_spacing(p_expl, line_pts=line_spacing, after_pts=para_spacing * 2)

        # =========================
        # IMAGES
        # =========================
        for img_bytes, width_in, height_in in q.get('explanation_images', []):
            inserted = False
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                    tmp.write(img_bytes)
                    tmp_path = tmp.name

                content_w = page_width - left_margin - right_margin
                col_gap = 0.08 if num_columns == 3 else 0.12
                col_w = (content_w - col_gap * (num_columns - 1)) / num_columns
                max_img_w = col_w - level2_indent - 0.05
                img_w = min(width_in if width_in > 0 else 1.5, max_img_w)

                p_img = cell.add_paragraph()
                p_img.paragraph_format.left_indent = Inches(level2_indent)
                p_img.add_run().add_picture(tmp_path, width=Inches(img_w))

                os.unlink(tmp_path)

                set_spacing(p_img, line_pts=line_spacing, after_pts=para_spacing)
                inserted = True

            except Exception:
                pass

            if not inserted:
                p_ph = cell.add_paragraph()
                p_ph.paragraph_format.left_indent = Inches(level2_indent)

                add_run(p_ph, "[चित्र यहाँ संलग्न करें]", bold=False,
                        size_pt=expl_font, italic=True)

                if expl_bg:
                    set_paragraph_background(p_ph, "E6E6E6")

                set_spacing(p_ph, line_pts=line_spacing * 3, after_pts=para_spacing)

    # =========================
    # SEPARATOR
    # =========================
    if show_separator:
        p_sep = cell.add_paragraph()
        pPr = p_sep._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')

        bt = OxmlElement('w:bottom')
        bt.set(qn('w:val'), 'single')
        bt.set(qn('w:sz'), '4')
        bt.set(qn('w:space'), '1')
        bt.set(qn('w:color'), 'auto')

        pBdr.append(bt)
        pPr.append(pBdr)

        set_spacing(p_sep, line_pts=line_spacing, after_pts=2)

def estimate_q_lines(q):
    lines = 1  # question

    # Options
    lines += len(layout_options(q['options'],
                               max_per_line=opts_per_line,
                               char_limit=opt_char_limit))

    # Explanation
    if q['explanation']:
        lines += 1  # explanation block

    # Images
    lines += len(q.get('explanation_images', [])) * 3

    return lines

# =============================================================================
# PAGE GENERATION (unchanged)
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
    hp = new_doc.add_paragraph()
    hp.alignment = (WD_ALIGN_PARAGRAPH.LEFT if header_align == "Left"
                    else WD_ALIGN_PARAGRAPH.RIGHT if header_align == "Right"
                    else WD_ALIGN_PARAGRAPH.CENTER)
    hr = hp.add_run(header_text)
    hr.bold = header_bold
    hr.font.size = Pt(header_font)
    hr.font.name = FONT_DOCX
    if header_bg:
        set_paragraph_background(hp, "E6E6E6")
    set_spacing(hp, line_pts=header_font+2, after_pts=6)

    if page_num_pos.startswith("Top") and not (hide_on_first and page_num == 1):
        tp = new_doc.add_paragraph()
        tp.alignment = (WD_ALIGN_PARAGRAPH.LEFT if "Left" in page_num_pos
                        else WD_ALIGN_PARAGRAPH.RIGHT if "Right" in page_num_pos
                        else WD_ALIGN_PARAGRAPH.CENTER)
        tp.add_run(f"पृष्ठ {page_num}").font.size = Pt(9)
        set_spacing(tp, line_pts=10, after_pts=3)

    # Column layout
    col_gap = 0.08 if num_columns == 3 else 0.12
    content_width = page_width - left_margin - right_margin
    col_width = (content_width - col_gap * (num_columns - 1)) / num_columns

    n = len(questions)
    per_col = (n + num_columns - 1) // num_columns
    col_questions = [questions[i*per_col:min((i+1)*per_col, n)] for i in range(num_columns)]

    outer_tbl = new_doc.add_table(rows=1, cols=num_columns)
    outer_tbl.autofit = False
    for i in range(num_columns):
        outer_tbl.columns[i].width = Inches(col_width)

    for col_idx, col_qs in enumerate(col_questions):
        cell = outer_tbl.cell(0, col_idx)
        for p in list(cell.paragraphs):
            p._p.getparent().remove(p._p)
        remove_cell_margins(cell)
        right_bdr = ({"val": "single", "sz": "4", "color": "CCCCCC", "space": "0"}
                     if col_idx < num_columns - 1 else no_border())
        set_cell_borders(cell, top=no_border(), bottom=no_border(),
                         left=no_border(), right=right_bdr)
        if col_qs:
            inner_tbl = cell.add_table(rows=len(col_qs), cols=1)
            inner_tbl.autofit = False
            inner_tbl.columns[0].width = Inches(col_width)
            for i, q in enumerate(col_qs):
                rc = inner_tbl.rows[i].cells[0]
                fill_cell(rc, q)
                set_cell_borders(rc, top=no_border(), bottom=no_border(),
                                 left=no_border(), right=no_border())

    if page_num_pos.startswith("Bottom") and not (hide_on_first and page_num == 1):
        bp = new_doc.add_paragraph()
        bp.alignment = (WD_ALIGN_PARAGRAPH.LEFT if "Left" in page_num_pos
                        else WD_ALIGN_PARAGRAPH.RIGHT if "Right" in page_num_pos
                        else WD_ALIGN_PARAGRAPH.CENTER)
        bp.add_run(f"पृष्ठ {page_num}").font.size = Pt(9)
        set_spacing(bp, line_pts=10, before_pts=5)

    if page_num < total_pages:
        new_doc.add_page_break()
    return new_doc

def generate_multi_page_docx(questions, chapter_title, q_per_page=None):
    if q_per_page is None:
        sample = min(10, len(questions))
        total_lines = sum(estimate_q_lines(q) for q in questions[:sample])
        avg_lines = total_lines / sample if sample > 0 else 10
        usable_height = page_height - top_margin - bottom_margin - 1.2
        lines_per_page = usable_height / (line_spacing / 72.0)
        q_per_page = max(1, int(lines_per_page / avg_lines))

    total_pages = (len(questions) + q_per_page - 1) // q_per_page
    final_doc = None
    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * q_per_page
        end = min(start + q_per_page, len(questions))
        page_doc = create_page_with_questions(questions[start:end], page_num, total_pages, chapter_title)
        if final_doc is None:
            final_doc = page_doc
        else:
            for element in page_doc.element.body:
                final_doc.element.body.append(element)
    return final_doc

# =============================================================================
# HTML PREVIEW – explanation uses hanging indent
# =============================================================================
def render_q_preview(q):
    l1px = level1_indent * 96
    l2px = level2_indent * 96
    hang_px = l1px - l2px   # negative

    option_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
    opts_html = ""
    for idx, group in enumerate(option_groups):
        text = ("&nbsp;&nbsp;&nbsp;&nbsp;".join(f"{o['key']} {o['text']}" for o in group)
                if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
        is_last = idx == len(option_groups) - 1
        if show_correct_inline and is_last:
            opts_html += (
                f"<div style='display:flex;justify-content:space-between;"
                f"margin-left:{l2px}px;font-size:{opt_font}pt;'>"
                f"<span>{text}</span>"
                f"<span style='font-weight:900;font-size:{opt_font+1.5}pt;'>{q['correct']}</span>"
                f"</div>"
            )
        else:
            opts_html += f"<div style='margin-left:{l2px}px;font-size:{opt_font}pt;'>{text}</div>"

    # Explanation – single block with hanging indent
    expl_html = ""
    if q['explanation'] or q.get('explanation_images'):
        heading_prefix = "➤ व्याख्या: " if expl_bullet else "व्याख्या : "
        bg_style = "background-color:#F0F0F0;padding:2px 4px;border-radius:3px;" if expl_bg else ""
        expl_html += (
            f"<div style='margin-left:{l2px}px;text-indent:{hang_px}px;{bg_style}font-size:{expl_font}pt;'>"
            f"<span style='font-weight:bold;'>{heading_prefix}</span>"
        )
        if q['explanation']:
            expl_html += q['explanation'].replace('|', '<br>')
        expl_html += "</div>"

        # Images after the text
        for img_bytes, _, __ in q.get('explanation_images', []):
            b64 = base64.b64encode(img_bytes).decode()
            expl_html += (
                f'<div style="margin-left:{l2px}px;">'
                f'<img src="data:image/png;base64,{b64}" style="max-width:100%;height:auto;"></div>'
            )

    question_html = q['question'].replace('\n', '<br>')

    q_html = (
        f"<div style='margin-left:{l2px}px;text-indent:{hang_px}px;"
        f"font-size:{q_font}pt;font-weight:bold;margin-bottom:2px;"
        f"white-space:pre-wrap;'>"
        f"{q['no']}. {question_html}</div>"
    )
    # meta_html = ""
    # if q.get('metadata'):
    #     meta_html = (
    #         f"<div style='text-align:right;font-size:6pt;margin-left:{l2px}px;'>"
    #         f"{q['metadata']}</div>"
    #     )

    return f"""
<div class="qblock">
  {q_html}
  {opts_html}
  {expl_html}
  {('<hr>' if show_separator else '')}
</div>"""

def build_preview_with_pagination(questions, q_per_page, chapter_title):
    total_pages = (len(questions) + q_per_page - 1) // q_per_page
    pages_html = []
    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * q_per_page
        end = min(start + q_per_page, len(questions))
        content_html = "".join(render_q_preview(q) for q in questions[start:end])
        pages_html.append(f"""
<div class="page" style="width:{page_width*96}px;min-height:{page_height*96}px;background:white;
  margin:0 auto 20px auto;padding:{top_margin*96}px {right_margin*96}px {bottom_margin*96}px {left_margin*96}px;
  box-shadow:0 4px 24px rgba(0,0,0,0.5);">
  <div style="background:#E6E6E6;padding:4px;border-radius:3px;text-align:center;
    font-weight:bold;margin-bottom:10px;">
    {header_template.format(book_name=book_name, chapter_title=chapter_title, page=page_num)}
  </div>
  <div style="column-count:{num_columns};column-gap:18px;">{content_html}</div>
</div>""")

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{background:#666;font-family:'Mangal','Nirmala UI','Noto Sans Devanagari','Arial',sans-serif;padding:20px;}}
  .qblock{{margin-bottom:5px;padding-bottom:4px;break-inside:avoid;page-break-inside:avoid;}}
  hr{{margin:4px 0;border:0;border-top:1px dotted #ccc;}}
</style>
</head><body>{''.join(pages_html)}</body></html>"""

# =============================================================================
# PDF GENERATION – explanation uses firstLineIndent
# =============================================================================
def register_devanagari_font():
    for path in [
        "C:/Windows/Fonts/Mangal.ttf",
        "C:/Windows/Fonts/Nirmala.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Mangal.ttf",
        "/usr/share/fonts/truetype/lohit/Lohit-Devanagari.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
    ]:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('Devanagari', path))
                return 'Devanagari'
            except Exception:
                continue
    st.warning("⚠️ No Devanagari font found. PDF will use Helvetica.")
    return 'Helvetica'


def generate_pdf(questions, chapter_title):
    font = register_devanagari_font()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=(page_width*inch, page_height*inch),
                            topMargin=top_margin*inch, bottomMargin=bottom_margin*inch,
                            leftMargin=left_margin*inch, rightMargin=right_margin*inch)
    styles = getSampleStyleSheet()
    l1 = level1_indent * inch
    l2 = level2_indent * inch

    sQ  = ParagraphStyle('Q',  parent=styles['Normal'], fontSize=q_font,    leading=line_spacing,
                          fontName=font, spaceAfter=para_spacing, leftIndent=l2, firstLineIndent=l1-l2)
    sMeta = ParagraphStyle('M', parent=styles['Normal'], fontSize=6,          leading=line_spacing,
                          fontName=font, alignment=TA_RIGHT, spaceAfter=para_spacing, leftIndent=l2)
    sOpt  = ParagraphStyle('O', parent=styles['Normal'], fontSize=opt_font,  leading=line_spacing,
                          fontName=font, spaceAfter=para_spacing, leftIndent=l2)
    sAns  = ParagraphStyle('A', parent=styles['Normal'], fontSize=opt_font+1.5, leading=line_spacing,
                          fontName=font, alignment=TA_RIGHT, spaceAfter=para_spacing, leftIndent=l2)
    sExpl = ParagraphStyle('E', parent=styles['Normal'], fontSize=expl_font, leading=line_spacing,
                          fontName=font, spaceAfter=para_spacing*2, leftIndent=l2, firstLineIndent=l1-l2,
                          backColor=colors.HexColor('#F0F0F0') if expl_bg else None)
    sH    = ParagraphStyle('H', parent=styles['Normal'], fontSize=header_font, leading=header_font+2,
                          fontName=font, alignment=TA_CENTER,
                          backColor=colors.HexColor('#E6E6E6') if header_bg else None, spaceAfter=6)

    story = [Paragraph(header_template.format(book_name=book_name, chapter_title=chapter_title, page=1), sH)]

    for q in questions:
        story.append(Paragraph(f"<b>{q['no']}.</b> {q['question']}", sQ))
        if q.get('metadata'):
            story.append(Paragraph(q['metadata'], sMeta))

        opt_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
        for idx, group in enumerate(opt_groups):
            text = ("    ".join(f"{o['key']} {o['text']}" for o in group)
                    if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
            is_last = idx == len(opt_groups) - 1
            story.append(Paragraph(text, sOpt))
            if show_correct_inline and is_last:
                story.append(Paragraph(f"<b>{q['correct']}</b>", sAns))

        if q['explanation'] or q.get('explanation_images'):
            heading = ("• व्याख्या : " if expl_bullet else "व्याख्या : ")
            expl_text = heading + (q['explanation'] if q['explanation'] else "")
            story.append(Paragraph(expl_text.replace('|', '<br/>'), sExpl))

            for img_bytes, width_in, height_in in q.get('explanation_images', []):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                        tmp.write(img_bytes)
                        tmp_path = tmp.name
                    content_w = page_width - left_margin - right_margin
                    col_gap = 0.08 if num_columns == 3 else 0.12
                    col_w = (content_w - col_gap * (num_columns - 1)) / num_columns
                    max_w = col_w - level2_indent - 0.05
                    img_w = min(width_in if width_in > 0 else 1.5, max_w)
                    story.append(Image(tmp_path, width=img_w*inch, height=height_in*inch))
                    os.unlink(tmp_path)
                except Exception:
                    story.append(Paragraph("[चित्र यहाँ संलग्न करें]", sExpl))

        if show_separator:
            story.append(Spacer(1, 2))

    doc.build(story)
    buffer.seek(0)
    return buffer

# =============================================================================
# CHAPTER TITLE EXTRACTION
# =============================================================================
def extract_chapter_title(doc):
    for para in doc.paragraphs[:10]:
        if "अध्याय" in para.text or "CHAPTER" in para.text.upper():
            title = para.text.strip()
            return title[:80] + "..." if len(title) > 80 else title
    return "RBD PUBLICATION — अध्याय"

# =============================================================================
# MAIN APP
# =============================================================================
if uploaded_file:
    doc = Document(uploaded_file)
    with st.spinner("Parsing questions..."):
        questions = parse_questions(doc)
        chapter_title = extract_chapter_title(doc)
    st.success(f"✅ {len(questions)} questions parsed!")

    if auto_fill:
        sample_size = min(10, len(questions))
        total_lines = sum(estimate_q_lines(q) for q in questions[:sample_size])
        avg_lines = total_lines / sample_size if sample_size > 0 else 10
        usable_height = page_height - top_margin - bottom_margin - 1.2
        lines_per_page = usable_height / (line_spacing / 72.0)
        q_per_page_est = max(1, int(lines_per_page / avg_lines))
        total_pages_est = (len(questions) + q_per_page_est - 1) // q_per_page_est
    else:
        q_per_page_est = 20
        total_pages_est = (len(questions) + q_per_page_est - 1) // q_per_page_est

    st.info(f"📄 Estimated pages: {total_pages_est} ({'auto' if auto_fill else 'fixed'})")

    tab1, tab2 = st.tabs(["📄 Page Preview", "🔍 Parsed Data"])
    with tab1:
        preview_html = build_preview_with_pagination(questions, q_per_page_est, chapter_title)
        st.components.v1.html(preview_html, height=1200, scrolling=True)
    with tab2:
        for q in questions[:5]:
            with st.expander(f"Q{q['no']} – {q['question'][:60]}…"):
                st.write("**Options:**", q['options'])
                st.write("**Correct Answer:**", q['correct'])
                st.write("**Explanation:**", q['explanation'][:500])
                st.write(f"**Explanation images:** {len(q.get('explanation_images', []))}")

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Generate DOCX"):
            with st.spinner("Generating DOCX..."):
                final_doc = generate_multi_page_docx(questions, chapter_title, None if auto_fill else q_per_page_est)
                filename = f"Formatted_Output_{len(questions)}Q.docx"
                final_doc.save(filename)
                with open(filename, "rb") as f:
                    st.download_button("📥 Download DOCX", f, filename,
                                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                st.success("🎉 DOCX ready!")
    with c2:
        if st.button("📑 Preview PDF"):
            with st.spinner("Generating PDF preview..."):
                pdf_buffer = generate_pdf(questions, chapter_title)
                pdf_b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{pdf_b64}" '
                    f'width="100%" height="800" type="application/pdf"></iframe>',
                    unsafe_allow_html=True)
                st.download_button("📥 Download PDF", pdf_buffer,
                                   file_name="Formatted_Output.pdf", mime="application/pdf")
                st.success("🎉 PDF preview ready!")