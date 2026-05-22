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

# ================= AUTH SYSTEM =================
import sqlite3
import datetime
import random
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

# ── Persistent DB path ────────────────────────────────────────────────────
_DB_DIR = os.path.expanduser("~/.streamlit_data")
os.makedirs(_DB_DIR, exist_ok=True)
DB_PATH = os.path.join(_DB_DIR, "rbd_users.db")
# ──────────────────────────────────────────────────────────────────────────

ADMIN_EMAILS = {
    e.strip() for e in os.getenv("ADMIN_EMAIL", "").split(",") if e.strip()
}
GRANTED_USERS = {
    e.strip() for e in os.getenv("GRANTED_USERS", "").split(",") if e.strip()
}

def seed_trusted_accounts():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    for email in ADMIN_EMAILS:
        c.execute(
            "INSERT OR IGNORE INTO users (email, created_at, is_admin, can_format) VALUES (?, ?, 1, 1)",
            (email, now)
        )
        c.execute("UPDATE users SET is_admin=1, can_format=1 WHERE email=?", (email,))
    for email in GRANTED_USERS:
        c.execute(
            "INSERT OR IGNORE INTO users (email, created_at, is_admin, can_format) VALUES (?, ?, 0, 1)",
            (email, now)
        )
        c.execute("UPDATE users SET can_format=1 WHERE email=? AND is_admin=0", (email,))
    conn.commit()
    conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        created_at TEXT,
        is_admin BOOLEAN DEFAULT 0,
        can_format BOOLEAN DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS otp_codes (
        email TEXT,
        code TEXT,
        expires_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        email TEXT,
        created_at TEXT,
        expires_at TEXT,
        is_revoked BOOLEAN DEFAULT 0
    )''')
    conn.commit()
    conn.close()


def add_user(email, is_admin=False):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        now = datetime.datetime.now().isoformat()
        c.execute(
            "INSERT OR IGNORE INTO users (email, created_at, is_admin, can_format) VALUES (?, ?, ?, ?)",
            (email, now, is_admin, is_admin)
        )
        conn.commit()
    except Exception:
        pass
    conn.close()


def get_user(email):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT email, is_admin, can_format FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"email": row[0], "is_admin": bool(row[1]), "can_format": bool(row[2])}
    return None


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, code):
    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_EMAIL
        msg["To"] = email
        msg["Subject"] = "OTP – RBD Formatter"
        msg.attach(MIMEText(f"Your OTP is: {code}\n\nValid for 10 minutes.", "plain"))
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_EMAIL, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        st.error(f"SMTP ERROR: {e}")
        return False


def store_otp(email, code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM otp_codes WHERE email=?", (email,))
    expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
    c.execute("INSERT INTO otp_codes VALUES (?, ?, ?)", (email, code, expiry))
    conn.commit()
    conn.close()


def verify_otp(email, code):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT code, expires_at FROM otp_codes WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    if row and row[0] == code:
        if datetime.datetime.now() < datetime.datetime.fromisoformat(row[1]):
            return True
    return False


def create_session(email):
    token = str(uuid.uuid4())
    now = datetime.datetime.now()
    expires = now + datetime.timedelta(days=30)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sessions (token, email, created_at, expires_at, is_revoked) VALUES (?, ?, ?, ?, 0)",
        (token, email, now.isoformat(), expires.isoformat())
    )
    conn.commit()
    conn.close()
    return token


def validate_session(token):
    if not token:
        return None
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT email, expires_at, is_revoked FROM sessions WHERE token=?",
        (token,)
    ).fetchone()
    conn.close()
    if not row:
        return None
    email, expires_at, is_revoked = row
    if is_revoked:
        return None
    if datetime.datetime.now() > datetime.datetime.fromisoformat(expires_at):
        return None
    return get_user(email)


def revoke_user_sessions(email):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE sessions SET is_revoked=1 WHERE email=?", (email,))
    conn.commit()
    conn.close()


def revoke_session(token):
    if not token:
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE sessions SET is_revoked=1 WHERE token=?", (token,))
    conn.commit()
    conn.close()


def get_user_sessions(email):
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT token, created_at, expires_at FROM sessions WHERE email=? AND is_revoked=0",
        (email,)
    ).fetchall()
    conn.close()
    return rows


def login_page():
    st.title("🔐 Login")
    email = st.text_input("Email")
    if st.button("Send OTP"):
        if email:
            user = get_user(email)
            if not user:
                add_user(email, email in ADMIN_EMAILS)
            otp = generate_otp()
            sent = send_otp_email(email, otp)
            if sent:
                store_otp(email, otp)
                st.session_state["otp_email"] = email
                st.success("OTP sent to your email ✅")
            else:
                st.error("❌ Failed to send OTP email")
    if "otp_email" in st.session_state:
        code = st.text_input("Enter OTP", type="password")
        if st.button("Verify"):
            if verify_otp(st.session_state["otp_email"], code):
                user = get_user(st.session_state["otp_email"])
                token = create_session(user["email"])
                st.session_state["authenticated"] = True
                st.session_state["user_email"] = user["email"]
                st.session_state["is_admin"] = user["is_admin"]
                st.session_state["can_format"] = user["can_format"]
                st.session_state["session_token"] = token
                st.query_params["session"] = token
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid OTP")
    if not st.session_state.get("authenticated"):
        st.stop()


# =============================================================================
# TEXT UTILITIES
# =============================================================================
def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)', '', text)
    text = re.sub(r'प्रश्न\s+\d+\s*', '', text)
    text = re.sub(r'^\d+\.\s*', '', text)
    text = re.sub(r'^\.+\s*', '', text)
    text = text.replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def parse_suchi_table(text):
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()

    suchi1 = re.findall(
        r'\(([A-D])\)\s*(.*?)(?=\([A-D]\)|\([IVX]+\)|सूची-II|$)',
        text, re.DOTALL
    )
    suchi2 = re.findall(
        r'\(([IVX]+)\)\s*(.*?)(?=\([IVX]+\)|\([A-D]\)|$)',
        text, re.DOTALL
    )

    suchi1 = [(k, clean_text(v)) for k, v in suchi1]
    suchi2 = [(k, clean_text(v)) for k, v in suchi2]

    # Extract header (everything before first (A))
    header_match = re.split(r'\([A-D]\)', text, maxsplit=1)
    header = header_match[0].strip() if header_match else ""

    rows = []
    max_len = max(len(suchi1), len(suchi2)) if (suchi1 or suchi2) else 0
    for i in range(max_len):
        left  = f"({suchi1[i][0]}) {suchi1[i][1]}" if i < len(suchi1) else ""
        right = f"({suchi2[i][0]}) {suchi2[i][1]}" if i < len(suchi2) else ""
        rows.append((left, right))

    return header, rows


def format_matching_question(text):
    """Legacy: kept for HTML preview. Returns tab-separated lines."""
    if not text:
        return text
    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()

    suchi1 = re.findall(
        r'\(([A-D])\)\s*(.*?)(?=\([A-D]\)|सूची-II|$)', text, re.DOTALL
    )
    suchi2 = re.findall(
        r'\(([IVX]+)\)\s*(.*?)(?=\([IVX]+\)|$)', text, re.DOTALL
    )
    suchi1 = [(k, clean_text(v)) for k, v in suchi1]
    suchi2 = [(k, clean_text(v)) for k, v in suchi2]

    header = re.split(r'\([A-D]\)', text, maxsplit=1)[0].strip()
    lines = []
    if header:
        lines.append(header)
        lines.append("")
    max_len = max(len(suchi1), len(suchi2))
    for i in range(max_len):
        left  = f"({suchi1[i][0]}) {suchi1[i][1]}" if i < len(suchi1) else ""
        right = f"({suchi2[i][0]}) {suchi2[i][1]}" if i < len(suchi2) else ""
        if left and right:
            lines.append(f"{left}\t{right}")
        elif left:
            lines.append(left)
        elif right:
            lines.append(right)
    return "\n".join(lines)


# =============================================================================
# FONT CONFIGURATION
# =============================================================================
HINDI_FONTS = {
    "Mangal": "Mangal",
    "Nirmala UI": "Nirmala UI",
    "Kokila": "Kokila",
    "Aparajita": "Aparajita",
    "Utsaah": "Utsaah",
    "Kruti Dev 010": "Kruti Dev 010",
    "Devanagari New": "Devanagari New",
}
ENGLISH_FONTS = {
    "Arial": "Arial",
    "Times New Roman": "Times New Roman",
    "Calibri": "Calibri",
    "Georgia": "Georgia",
    "Cambria": "Cambria",
    "Garamond": "Garamond",
    "Trebuchet MS": "Trebuchet MS",
    "Verdana": "Verdana",
    "Book Antiqua": "Book Antiqua",
    "Century Gothic": "Century Gothic",
}

# =============================================================================
# PAGE CONFIG & INIT
# =============================================================================
st.set_page_config(page_title="RBD Formatter", layout="wide")
st.title("📚 RBD Publication – Smart Formatter")
init_db()

# Seed only once per session to avoid hammering DB on every rerun
if not st.session_state.get("_seeded"):
    seed_trusted_accounts()
    st.session_state["_seeded"] = True

# ── Session restore from query param ─────────────────────────────────────────
if not st.session_state.get("authenticated"):
    token = st.query_params.get("session")
    if token:
        user = validate_session(token)
        if user:
            st.session_state["authenticated"] = True
            st.session_state["user_email"] = user["email"]
            st.session_state["is_admin"] = user["is_admin"]
            st.session_state["can_format"] = user["can_format"]
            st.session_state["session_token"] = token
        else:
            st.query_params.clear()

if not st.session_state.get("authenticated"):
    login_page()

# ── Admin panel ───────────────────────────────────────────────────────────────
if st.session_state.get("is_admin"):
    st.sidebar.title("👑 Admin Panel")
    conn = sqlite3.connect(DB_PATH)
    users = conn.execute("SELECT email, can_format FROM users").fetchall()
    conn.close()
    for email, can_format in users:
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            val = st.checkbox(email, value=bool(can_format), key=f"perm_{email}")
        with col2:
            if st.sidebar.button("🚫", key=f"revoke_{email}", help=f"Revoke sessions for {email}"):
                revoke_user_sessions(email)
                st.sidebar.success(f"Sessions revoked for {email}")
                st.rerun()
        if val != bool(can_format):
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET can_format=? WHERE email=?", (val, email))
            conn.commit()
            conn.close()
            st.rerun()

if st.session_state.get("authenticated"):
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 {st.session_state.get('user_email', '')}")
    if st.sidebar.button("🚪 Logout"):
        revoke_session(st.session_state.get("session_token"))
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

# ── Access guard ──────────────────────────────────────────────────────────────
if not st.session_state.get("can_format"):
    st.error("❌ You are not allowed to use formatter")
    st.stop()

# ── File uploader (only shown to authorised users) ────────────────────────────
uploaded_file = st.file_uploader("📄 Upload Chapter DOCX", type=["docx"])

# =============================================================================
# SIDEBAR – all settings collected into a dict so functions don't rely on
# bare globals that may not exist yet.
# =============================================================================
with st.sidebar:
    st.header("📄 Page Design")
    page_width      = st.number_input("Page Width (inches)",   5.0, 12.0, 7.0,  0.1)
    page_height     = st.number_input("Page Height (inches)",  6.0, 14.0, 9.0,  0.1)
    top_margin      = st.number_input("Top Margin (inches)",   0.2,  1.0, 0.4,  0.05)
    bottom_margin   = st.number_input("Bottom Margin (inches)",0.2,  1.0, 0.4,  0.05)
    left_margin     = st.number_input("Left Margin (inches)",  0.2,  1.0, 0.4,  0.05)
    right_margin    = st.number_input("Right Margin (inches)", 0.2,  1.0, 0.4,  0.05)

    st.header("📐 Layout")
    num_columns = st.selectbox("Number of Columns", [2, 3], index=0)
    auto_fill   = st.checkbox("Auto‑fill pages", True)

    st.header("🔤 Font Settings (Output DOCX)")
    font_language = st.selectbox(
        "Select Font Language", ["Hindi (Devanagari)", "English"], index=0
    )
    if font_language == "Hindi (Devanagari)":
        selected_font_name = st.selectbox("Select Hindi Font", list(HINDI_FONTS.keys()), index=0)
        FONT_DOCX = HINDI_FONTS[selected_font_name]
    else:
        selected_font_name = st.selectbox("Select English Font", list(ENGLISH_FONTS.keys()), index=0)
        FONT_DOCX = ENGLISH_FONTS[selected_font_name]
    st.caption(f"✅ Selected font: **{FONT_DOCX}** — applied to all text in output DOCX")

    st.header("✍️ Text Styling")
    q_font = st.slider("Question font size (pt)", 5.0, 12.0, 5.5, 0.5)
    st.markdown("**Indent levels**")
    st.caption("Level-1: question number '1.' and bullet '•' sit here")
    level1_indent = st.number_input("Level-1 indent (inches)", 0.0, 0.5, 0.0, 0.05)
    st.caption("Level-2: all content text starts here")
    level2_indent = st.number_input("Level-2 indent (inches)", 0.05, 1.0, 0.15, 0.05)
    q_indent = level2_indent

    opt_font = st.slider("Options font size (pt)",     5.0, 11.0, 5.5, 0.5)
    opt_bold = st.checkbox("Bold options", False)
    ans_font = st.slider("Answer font size (pt)",      5.0, 11.0, 5.5, 0.5)
    ans_bold = st.checkbox("Bold answer", False)
    expl_font = st.slider("Explanation font size (pt)", 5.0, 10.0, 5.5, 0.5)

    st.header("📏 Spacing")
    line_spacing = st.slider("Line spacing (pt)",           8.0, 15.0,  9.5, 0.5)
    para_spacing = st.slider("Space after paragraph (pt)",  0.0,  6.0,  0.0, 0.5)
    char_spacing = st.slider("Character spacing (pt)",      0.0,  3.0,  0.0, 0.5)

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
    book_name       = st.text_input("Book name", "RBD PUBLICATION")
    topic_name      = st.text_input("Topic / Chapter Name (shown in header center)", "")
    header_font     = st.slider("Header font size (pt)", 8.0, 16.0, 11.0, 0.5)
    header_bold     = st.checkbox("Header bold", True)
    header_bg       = st.checkbox("Header grey background", True)
    header_align    = st.selectbox("Header alignment", ["Left", "Center", "Right"], index=1)

    st.header("🔢 Page Numbers")
    page_num_pos = st.selectbox(
        "Position",
        ["None","Top Left","Top Center","Top Right","Bottom Left","Bottom Center","Bottom Right"],
        index=5
    )
    hide_on_first = st.checkbox("Hide on first page", False) if page_num_pos != "None" else False

    st.header("✨ Extras")
    show_correct_inline = st.checkbox("Show correct answer on last option line (right‑aligned)", True)
    show_separator      = st.checkbox("Show line after each question", False)
    expl_bullet         = st.checkbox("Bullet before व्याख्या heading", True)
    expl_bg             = st.checkbox("Light grey background for explanation", True)

    st.header("📋 Metadata")
    include_metadata = st.checkbox("Include PYQ metadata in output", False)

    if st.checkbox("Extra compact mode", False):
        line_spacing  = 5.0
        para_spacing  = 0.0
        q_font        = 5.0
        opt_font      = 5.0
        ans_font      = 5.0
        expl_font     = 5.0


# =============================================================================
# PARSING
# =============================================================================
def parse_questions(doc):
    import io as _io
    questions = []
    current_block = []
    inside_question = False

    def is_question_start(text):
        if not text:
            return False
        text = text.strip()
        return bool(
            re.match(r'^प्रश्न\s+\d+', text) or
            re.match(r'^\d+\.\s+', text)
        )

    def extract_images_from_para(para):
        images = []
        NS = {
            'a':  'http://schemas.openxmlformats.org/drawingml/2006/main',
            'r':  'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
            'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
        }
        for run in para.runs:
            for blip in run._element.findall('.//a:blip', namespaces=NS):
                r_embed_key = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'
                rId = blip.get(r_embed_key)
                if not rId:
                    continue
                try:
                    image_part = doc.part.related_parts[rId]
                except KeyError:
                    continue
                img_bytes   = image_part.blob
                width_in = height_in = 1.0
                extent = run._element.find('.//wp:extent', namespaces=NS)
                if extent is not None:
                    width_in  = int(extent.get('cx', 914400)) / 914400.0
                    height_in = int(extent.get('cy', 914400)) / 914400.0
                else:
                    try:
                        pil_img   = PILImage.open(_io.BytesIO(img_bytes))
                        width_in  = pil_img.width  / 96.0
                        height_in = pil_img.height / 96.0
                    except Exception:
                        pass
                images.append((img_bytes, width_in, height_in))
        return images

    for para in doc.paragraphs:
        text   = para.text.strip()
        images = extract_images_from_para(para)

        if re.match(r'^\s*(अथवा|तथा)\s*$', text):
            if current_block:
                q = process_question_block(current_block)
                if q:
                    q['no'] = str(len(questions) + 1)
                    questions.append(q)
            current_block  = []
            inside_question = False
            continue

        if is_question_start(text):
            if current_block:
                q = process_question_block(current_block)
                if q:
                    q['no'] = str(len(questions) + 1)
                    questions.append(q)
            current_block   = [(text, images)]
            inside_question = True
            continue

        if inside_question:
            current_block.append((text, images))

    if current_block:
        q = process_question_block(current_block)
        if q:
            q['no'] = str(len(questions) + 1)
            questions.append(q)

    return questions


def remove_metadata_pattern(text):
    pattern = r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)'
    return re.sub(pattern, '', text).strip()


def is_matching_question(text):
    if not text:
        return False
    return bool(
        re.search(r'सूची', text, re.IGNORECASE) or
        re.search(r'\(\d\)', text)
    )


def process_question_block(block):
    full_text = "\n".join(txt for txt, _ in block).strip()

    q_no = None
    for pattern in [r'प्रश्न\s+(\d+)', r'^(\d+)\.', r'^(\d+)\s+']:
        m = re.search(pattern, full_text)
        if m:
            q_no      = m.group(1)
            full_text = full_text[m.end():].strip()
            full_text = re.sub(r'^\.+\s*', '', full_text)
            break

    if not q_no:
        return None

    ans_match = re.search(r'(?:सही उत्तर|उत्तर)\s*[:\-]\s*\(([a-dA-D])\)', full_text)
    if not ans_match:
        # Only match if the trailing "(x)" is not immediately preceded by option text
        ans_match = re.search(r'(?<=[।\.!\?\s])\(([a-dA-D])\)\s*$', full_text)
    correct = f"({ans_match.group(1).lower()})" if ans_match else ""

    explanation = ""
    expl_match  = re.search(
        r'व्याख्या\s*:\s*(.*?)(?=\n\s*(\d+\.|प्रश्न\s+\d+)|$)',
        full_text, re.DOTALL
    )
    if expl_match:
        explanation = clean_text(expl_match.group(1))

    content = full_text
    if ans_match:
        content = content[:ans_match.start()]
    if expl_match:
        content = content[:expl_match.start()]
    content = content.strip()

    suchi_block  = ""
    suchi_header = ""
    suchi_rows   = []
    # Match standalone कूट only — NOT चित्रकूट, महाकूट, etc.
    suchi_match = re.search(r'(सूची.*?)(?=(?<!\S)कूट(?!\S)|$)', content, re.DOTALL)
    if suchi_match:
        suchi_block = suchi_match.group(1)
        suchi_header, suchi_rows = parse_suchi_table(suchi_block)
        content = content.replace(suchi_match.group(1), "")

    # FIX: standalone कूट only — must be at line-start or after whitespace,
    # so चित्रकूट / महाकूट are never matched.
    koot_block  = ""
    koot_match  = re.search(
        r'(?:^|\n)(कूट\s*:?.*?)(?=सही उत्तर|उत्तर\s*:|व्याख्या\s*:|$)',
        full_text, re.DOTALL | re.MULTILINE
    )
    if koot_match:
        koot_block = koot_match.group(1).strip()

    first_opt = re.search(r'\([a-dA-D]\)', content)
    if first_opt:
        question_text = content[:first_opt.start()].strip()
        opts_raw      = content[first_opt.start():]
    else:
        question_text = content
        opts_raw      = ""

    question_text = clean_text(question_text)

    options = []
    if opts_raw:
        opts_raw = re.split(
            r'(?=\n\s*\d+\.)|'
            r'(?=\n\s*प्रश्न\s+\d+)|'
            r'(?:^|\n)(?:कूट|व्याख्या|उत्तर)',
            opts_raw
        )[0]
        matches = re.findall(
            r'\(([a-dA-D])\)\s*(.*?)(?=\([a-dA-D]\)|$)',
            opts_raw, re.DOTALL
        )
        for key, text in matches:
            text = clean_text(text)
            if re.search(r'\([a-d]\)\s*-\s*\([ivx]+\)', text, re.IGNORECASE):
                continue
            if "सूची" in text:
                continue
            if text:
                options.append({"key": f"({key.lower()})", "text": text.strip()})
    options = options[:4]

    # Build final_question — suchi_rows stored separately for DOCX table rendering
    final_question = question_text
    if suchi_header:
        final_question += "\n\n[SUCHI_HEADER]" + suchi_header
    if koot_block:
        final_question += "\n\n" + koot_block

    # Collect explanation images (paragraphs after the answer/explanation marker)
    explanation_images = []
    answer_idx = -1
    for idx, (txt, _) in enumerate(block):
        if re.search(r'(उत्तर|व्याख्या)', txt):
            answer_idx = idx
            break
    src = block[answer_idx + 1:] if answer_idx != -1 else []
    for _, imgs in src:
        explanation_images.extend(imgs)

    meta_match = re.search(
        r'\(([^)]*\d{2,4}[^)]*(?:shift|Shift|पाली|[\[\(][^)\]]*[\]\)])[^)]*)\)',
        full_text
    )
    if not meta_match:
        meta_match = re.search(r'\(([^)]*\d{4}[^)]*)\)', full_text)
    metadata_str = meta_match.group(0).strip() if meta_match else ""

    return {
        "no":                 q_no,
        "question":           final_question,
        "suchi_rows":         suchi_rows,
        "options":            options,
        "correct":            correct,
        "explanation":        explanation,
        "explanation_images": explanation_images,
        "metadata":           metadata_str,
    }


# =============================================================================
# OPTION LAYOUT
# =============================================================================
def layout_options(opts, max_per_line=2, char_limit=68):
    result = []
    i, n = 0, len(opts)
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
def set_spacing(para, line_pts, after_pts=0, before_pts=0):
    pPr = para._p.get_or_add_pPr()
    for old in pPr.findall(qn('w:spacing')):
        pPr.remove(old)
    s = OxmlElement('w:spacing')
    s.set(qn('w:line'),     str(int(line_pts * 20)))
    s.set(qn('w:lineRule'), 'atLeast')
    s.set(qn('w:before'),   str(int(before_pts * 20)))
    s.set(qn('w:after'),    str(int(after_pts  * 20)))
    pPr.append(s)


def set_char_spacing(run, spacing_pt):
    if spacing_pt > 0:
        rPr = run._r.get_or_add_rPr()
        sp  = OxmlElement('w:spacing')
        sp.set(qn('w:val'), str(int(spacing_pt * 20)))
        rPr.append(sp)


def set_paragraph_background(para, color_rgb):
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  color_rgb)
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
    _apply_ind(para, int(l2_in * 1440), int((l1_in - l2_in) * 1440))


def set_left_indent(para, left_in):
    _apply_ind(para, int(left_in * 1440), 0)


def apply_font_to_run(run):
    run.font.name = FONT_DOCX
    rPr    = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:ascii'),   FONT_DOCX)
    rFonts.set(qn('w:hAnsi'),   FONT_DOCX)
    rFonts.set(qn('w:eastAsia'), FONT_DOCX)
    rFonts.set(qn('w:cs'),      FONT_DOCX)


def add_run(para, text, bold=False, size_pt=8, italic=False):
    r = para.add_run(text)
    r.bold    = bold
    r.italic  = italic
    r.font.size = Pt(size_pt)
    apply_font_to_run(r)
    if char_spacing > 0:
        set_char_spacing(r, char_spacing)
    return r


# =============================================================================
# सूची TABLE — rendered as a proper DOCX 2-column table
# =============================================================================
def add_suchi_table(container, suchi_rows, col_width_in):
    if not suchi_rows:
        return

    half_dxa  = int((col_width_in - level2_indent) * 1440 / 2)
    total_dxa = half_dxa * 2

    tbl = OxmlElement('w:tbl')

    tblPr = OxmlElement('w:tblPr')
    tblW  = OxmlElement('w:tblW')
    tblW.set(qn('w:w'),    str(total_dxa))
    tblW.set(qn('w:type'), 'dxa')
    tblPr.append(tblW)
    tblInd = OxmlElement('w:tblInd')
    tblInd.set(qn('w:w'),    str(int(level2_indent * 1440)))
    tblInd.set(qn('w:type'), 'dxa')
    tblPr.append(tblInd)
    tblBorders = OxmlElement('w:tblBorders')
    for edge in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        b = OxmlElement(f'w:{edge}')
        b.set(qn('w:val'), 'nil')
        tblBorders.append(b)
    tblPr.append(tblBorders)
    tbl.append(tblPr)

    tblGrid = OxmlElement('w:tblGrid')
    for _ in range(2):
        gc = OxmlElement('w:gridCol')
        gc.set(qn('w:w'), str(half_dxa))
        tblGrid.append(gc)
    tbl.append(tblGrid)

    def make_tc(text_content, width_dxa):
        tc    = OxmlElement('w:tc')
        tcPr  = OxmlElement('w:tcPr')
        tcW   = OxmlElement('w:tcW')
        tcW.set(qn('w:w'),    str(width_dxa))
        tcW.set(qn('w:type'), 'dxa')
        tcPr.append(tcW)
        tcBorders = OxmlElement('w:tcBorders')
        for edge in ['top', 'left', 'bottom', 'right']:
            b = OxmlElement(f'w:{edge}')
            b.set(qn('w:val'), 'nil')
            tcBorders.append(b)
        tcPr.append(tcBorders)
        tcMar = OxmlElement('w:tcMar')
        for edge in ['top', 'left', 'bottom', 'right']:
            m = OxmlElement(f'w:{edge}')
            m.set(qn('w:w'),    '40')
            m.set(qn('w:type'), 'dxa')
            tcMar.append(m)
        tcPr.append(tcMar)
        tc.append(tcPr)

        p   = OxmlElement('w:p')
        pPr = OxmlElement('w:pPr')
        sp  = OxmlElement('w:spacing')
        sp.set(qn('w:line'),     str(int(line_spacing * 20)))
        sp.set(qn('w:lineRule'), 'atLeast')
        sp.set(qn('w:before'),   '0')
        sp.set(qn('w:after'),    '0')
        pPr.append(sp)
        p.append(pPr)

        r   = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        sz  = OxmlElement('w:sz')
        sz.set(qn('w:val'), str(int(q_font * 2)))
        rPr.append(sz)
        rF = OxmlElement('w:rFonts')
        rF.set(qn('w:ascii'),   FONT_DOCX)
        rF.set(qn('w:hAnsi'),   FONT_DOCX)
        rF.set(qn('w:cs'),      FONT_DOCX)
        rPr.insert(0, rF)
        r.append(rPr)
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text_content
        r.append(t)
        p.append(r)
        tc.append(p)
        return tc

    for left_text, right_text in suchi_rows:
        tr   = OxmlElement('w:tr')
        trPr = OxmlElement('w:trPr')
        trH  = OxmlElement('w:trHeight')
        trH.set(qn('w:val'),   str(int(line_spacing * 20)))
        trH.set(qn('w:hRule'), 'atLeast')
        trPr.append(trH)
        tr.append(trPr)
        tr.append(make_tc(left_text,  half_dxa))
        tr.append(make_tc(right_text, half_dxa))
        tbl.append(tr)

    container._element.body.append(tbl)


# =============================================================================
# FILL CELL
# =============================================================================
def fill_cell(container, q, include_metadata=False):
    content_width = page_width - left_margin - right_margin
    col_gap   = 0.08 if num_columns == 3 else 0.12
    col_width = (content_width - col_gap * (num_columns - 1)) / num_columns

    # ── Question paragraph ───────────────────────────────────────────────────
    p_q = container.add_paragraph()
    p_q.paragraph_format.left_indent       = Inches(level2_indent)
    p_q.paragraph_format.first_line_indent = Inches(level1_indent - level2_indent)

    tab_stops = p_q.paragraph_format.tab_stops
    tab_stops.add_tab_stop(Inches(level2_indent),       WD_TAB_ALIGNMENT.LEFT)
    tab_stops.add_tab_stop(Inches(col_width - 0.2),     WD_TAB_ALIGNMENT.LEFT)

    # Strip [SUCHI_HEADER] sentinel and extract visible question text
    display_question    = q['question']
    suchi_header_display = ""
    if "[SUCHI_HEADER]" in display_question:
        parts                = display_question.split("[SUCHI_HEADER]", 1)
        display_question     = parts[0].strip()
        suchi_header_display = parts[1].strip() if len(parts) > 1 else ""

    add_run(p_q, f"{q['no']}. ", bold=True,  size_pt=q_font)
    add_run(p_q, display_question, bold=True, size_pt=q_font)
    set_spacing(p_q, line_pts=line_spacing, after_pts=para_spacing)

    # ── Metadata ─────────────────────────────────────────────────────────────
    if include_metadata and q.get('metadata'):
        p_meta = container.add_paragraph()
        p_meta.paragraph_format.left_indent = Inches(level2_indent)
        p_meta.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_meta = p_meta.add_run(q['metadata'])
        r_meta.italic     = True
        r_meta.font.size  = Pt(max(q_font - 1.0, 5.0))
        apply_font_to_run(r_meta)
        set_spacing(p_meta, line_pts=line_spacing, after_pts=0)

    # ── सूची header label (e.g. "सूची-I  सूची-II") ──────────────────────────
    if suchi_header_display:
        p_sh = container.add_paragraph()
        p_sh.paragraph_format.left_indent = Inches(level2_indent)
        add_run(p_sh, suchi_header_display, bold=True, size_pt=q_font)
        set_spacing(p_sh, line_pts=line_spacing, after_pts=0)

    # ── सूची table — left col || right col ────────────────────────
    if q.get('suchi_rows'):
        add_suchi_table(container, q['suchi_rows'], col_width)

    # ── Options ──────────────────────────────────────────────────────────────
    option_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
    right_tab_pos = col_width - 0.2

    for idx, group in enumerate(option_groups):
        text  = ("    ".join(f"{o['key']} {o['text']}" for o in group)
                 if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
        p_opt = container.add_paragraph()
        p_opt.paragraph_format.left_indent = Inches(level2_indent)
        add_run(p_opt, text, bold=opt_bold, size_pt=opt_font)

        if show_correct_inline and idx == len(option_groups) - 1:
            tab_stops = p_opt.paragraph_format.tab_stops
            tab_stops.add_tab_stop(Inches(right_tab_pos), WD_TAB_ALIGNMENT.RIGHT)
            p_opt.add_run("\t")
            add_run(p_opt, q['correct'], bold=True, size_pt=opt_font + 1)

        set_spacing(p_opt, line_pts=line_spacing, after_pts=para_spacing)

    # ── Explanation ───────────────────────────────────────────────────────────
    if q['explanation']:
        p_expl = container.add_paragraph()
        p_expl.paragraph_format.left_indent       = Inches(level2_indent)
        p_expl.paragraph_format.first_line_indent = Inches(level1_indent - level2_indent)
        if expl_bg:
            set_paragraph_background(p_expl, "E6E6E6")
        prefix = "➤ व्याख्या: " if expl_bullet else "व्याख्या: "
        add_run(p_expl, prefix,          bold=True, size_pt=expl_font)
        add_run(p_expl, q['explanation'],            size_pt=expl_font)
        set_spacing(p_expl, line_pts=line_spacing, after_pts=para_spacing * 2)

    # ── Explanation images ────────────────────────────────────────────────────
    for img_bytes, width_in, height_in in q.get('explanation_images', []):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name
            max_img_w = col_width - level2_indent - 0.2
            img_w     = min(width_in if width_in > 0 else 1.5, max_img_w)
            p_img     = container.add_paragraph()
            p_img.paragraph_format.left_indent = Inches(level2_indent)
            p_img.add_run().add_picture(tmp_path, width=Inches(img_w))
            os.unlink(tmp_path)
            set_spacing(p_img, line_pts=line_spacing, after_pts=para_spacing)
        except Exception:
            p_ph = container.add_paragraph()
            p_ph.paragraph_format.left_indent = Inches(level2_indent)
            add_run(p_ph, "[चित्र यहाँ संलग्न करें]", italic=True, size_pt=expl_font)
            if expl_bg:
                set_paragraph_background(p_ph, "E6E6E6")
            set_spacing(p_ph, line_pts=line_spacing, after_pts=para_spacing)

    if show_separator:
        p_sep = container.add_paragraph()
        set_spacing(p_sep, line_pts=line_spacing, after_pts=2)


def estimate_q_lines(q):
    lines  = 1
    lines += len(layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit))
    if q['explanation']:
        lines += 1
    lines += len(q.get('suchi_rows', [])) + (1 if q.get('suchi_rows') else 0)
    lines += len(q.get('explanation_images', [])) * 3
    return lines


# =============================================================================
# PAGE GENERATION
# =============================================================================
def _add_page_number_field(para):
    for ftype, itext in [('begin', None), ('instr', ' PAGE '), ('end', None)]:
        run = para.add_run()
        if ftype == 'instr':
            instr = OxmlElement('w:instrText')
            instr.set(qn('xml:space'), 'preserve')
            instr.text = itext
            run._r.append(instr)
        else:
            fc = OxmlElement('w:fldChar')
            fc.set(qn('w:fldCharType'), ftype)
            run._r.append(fc)
        run.bold      = header_bold
        run.font.size = Pt(header_font)
        apply_font_to_run(run)
    return run


def generate_multi_page_docx(questions, chapter_title):
    doc = Document()

    sec = doc.sections[0]
    sec.page_width    = Inches(page_width)
    sec.page_height   = Inches(page_height)
    sec.top_margin    = Inches(top_margin)
    sec.bottom_margin = Inches(bottom_margin)
    sec.left_margin   = Inches(left_margin)
    sec.right_margin  = Inches(right_margin)

    sectPr = sec._sectPr
    W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    cols_list = sectPr.findall(f'{{{W_NS}}}cols')
    if cols_list:
        cols = cols_list[0]
    else:
        cols = OxmlElement('w:cols')
        sectPr.append(cols)
    cols.set(qn('w:num'),   str(num_columns))
    cols.set(qn('w:space'), "300")

    sec.header_distance = Inches(0.15)

    # Enable "Different First Page" header
    titlePg = OxmlElement('w:titlePg')
    sectPr.append(titlePg)

    BG             = "E6E6E6"
    LOGO_H_INCHES  = 0.32
    LOGO_W_INCHES  = LOGO_H_INCHES * (922 / 376)

    page_w_dxa  = int(page_width  * 1440)
    lm_dxa      = int(left_margin * 1440)
    rm_dxa      = int(right_margin * 1440)
    total_dxa   = page_w_dxa - lm_dxa - rm_dxa

    PAGE_COL_DXA  = int(0.45 * 1440)
    LOGO_COL_DXA  = int(LOGO_W_INCHES * 1440)
    TOPIC_COL_DXA = int(1.5  * 1440)
    MID_COL_DXA   = total_dxa - PAGE_COL_DXA - TOPIC_COL_DXA - LOGO_COL_DXA

    clean_chapter = re.sub(r'\*+', '', chapter_title).strip()
    topic_text    = topic_name.strip() if topic_name.strip() else clean_chapter

    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ROW_HEIGHT_RULE
    from docx.table import _Cell

    LOGO_PATH = "logo.png"

    def make_header_cell(width_dxa):
        """Bare XML table cell with grey bg, no borders, vertically centered."""
        tc    = OxmlElement('w:tc')
        tcPr  = OxmlElement('w:tcPr')
        tcW   = OxmlElement('w:tcW')
        tcW.set(qn('w:w'),    str(width_dxa))
        tcW.set(qn('w:type'), 'dxa')
        tcPr.append(tcW)
        tcBorders = OxmlElement('w:tcBorders')
        for edge in ['top', 'left', 'bottom', 'right']:
            b = OxmlElement(f'w:{edge}')
            b.set(qn('w:val'), 'nil')
            tcBorders.append(b)
        tcPr.append(tcBorders)
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'),   'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'),  BG)
        tcPr.append(shd)
        vAlign = OxmlElement('w:vAlign')
        vAlign.set(qn('w:val'), 'center')
        tcPr.append(vAlign)
        tcMar = OxmlElement('w:tcMar')
        for edge in ['top', 'left', 'bottom', 'right']:
            m = OxmlElement(f'w:{edge}')
            m.set(qn('w:w'),    '60')
            m.set(qn('w:type'), 'dxa')
            tcMar.append(m)
        tcPr.append(tcMar)
        tc.append(tcPr)
        return tc

    def make_text_para(text, align='center', bold=True, font_pt=None):
        """Return a bare <w:p> XML element with styled text."""
        fpt = font_pt or header_font
        p   = OxmlElement('w:p')
        pPr = OxmlElement('w:pPr')
        jc  = OxmlElement('w:jc')
        jc.set(qn('w:val'), align)
        pPr.append(jc)
        sp = OxmlElement('w:spacing')
        sp.set(qn('w:before'), '0')
        sp.set(qn('w:after'),  '0')
        pPr.append(sp)
        p.append(pPr)
        r   = OxmlElement('w:r')
        rPr = OxmlElement('w:rPr')
        if bold and header_bold:
            rPr.append(OxmlElement('w:b'))
        sz = OxmlElement('w:sz')
        sz.set(qn('w:val'), str(int(fpt * 2)))
        rPr.append(sz)
        rF = OxmlElement('w:rFonts')
        rF.set(qn('w:ascii'),  FONT_DOCX)
        rF.set(qn('w:hAnsi'),  FONT_DOCX)
        rF.set(qn('w:cs'),     FONT_DOCX)
        rPr.insert(0, rF)
        r.append(rPr)
        t = OxmlElement('w:t')
        t.set(qn('xml:space'), 'preserve')
        t.text = text
        r.append(t)
        p.append(r)
        return p

    def make_page_num_para(align='left', font_pt=None):
        """Return a <w:p> with an auto PAGE field."""
        fpt = font_pt or header_font
        p   = OxmlElement('w:p')
        pPr = OxmlElement('w:pPr')
        jc  = OxmlElement('w:jc')
        jc.set(qn('w:val'), align)
        pPr.append(jc)
        sp = OxmlElement('w:spacing')
        sp.set(qn('w:before'), '0')
        sp.set(qn('w:after'),  '0')
        pPr.append(sp)
        p.append(pPr)
        for ftype, itext in [('begin', None), ('instr', ' PAGE '), ('end', None)]:
            r   = OxmlElement('w:r')
            rPr = OxmlElement('w:rPr')
            rPr.append(OxmlElement('w:b'))
            sz = OxmlElement('w:sz')
            sz.set(qn('w:val'), str(int(fpt * 2)))
            rPr.append(sz)
            r.append(rPr)
            if ftype == 'instr':
                el = OxmlElement('w:instrText')
                el.set(qn('xml:space'), 'preserve')
                el.text = itext
                r.append(el)
            else:
                fc = OxmlElement('w:fldChar')
                fc.set(qn('w:fldCharType'), ftype)
                r.append(fc)
            p.append(r)
        return p

    def build_header_table(col_widths, cell_contents):
        """
        Build a borderless grey header table.
        col_widths: list of DXA widths
        cell_contents: list of <w:p> XML elements (one per cell)
        Returns <w:tbl> element.
        """
        tbl   = OxmlElement('w:tbl')
        tblPr = OxmlElement('w:tblPr')
        tblW  = OxmlElement('w:tblW')
        tblW.set(qn('w:w'),    str(sum(col_widths)))
        tblW.set(qn('w:type'), 'dxa')
        tblPr.append(tblW)
        tblBorders = OxmlElement('w:tblBorders')
        for edge in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
            b = OxmlElement(f'w:{edge}')
            b.set(qn('w:val'), 'nil')
            tblBorders.append(b)
        tblPr.append(tblBorders)
        tbl.append(tblPr)
        tblGrid = OxmlElement('w:tblGrid')
        for dxa in col_widths:
            gc = OxmlElement('w:gridCol')
            gc.set(qn('w:w'), str(dxa))
            tblGrid.append(gc)
        tbl.append(tblGrid)
        tr   = OxmlElement('w:tr')
        trPr = OxmlElement('w:trPr')
        trH  = OxmlElement('w:trHeight')
        trH.set(qn('w:val'),   str(int(LOGO_H_INCHES * 1440)))
        trH.set(qn('w:hRule'), 'exact')
        trPr.append(trH)
        tr.append(trPr)
        for dxa, para_el in zip(col_widths, cell_contents):
            tc = make_header_cell(dxa)
            tc.append(para_el)
            tr.append(tc)
        tbl.append(tr)
        return tbl

    # ── Page 1 header: chapter title centered, no logo, no page number ────────
    P1_LEFT_DXA = PAGE_COL_DXA
    P1_MID_DXA  = total_dxa - PAGE_COL_DXA - LOGO_COL_DXA

    first_header = sec.first_page_header
    for p in list(first_header.paragraphs):
        p._element.getparent().remove(p._element)

    tbl_first = build_header_table(
        [P1_LEFT_DXA, P1_MID_DXA, LOGO_COL_DXA],
        [
            make_text_para("", align='left'),
            make_text_para(clean_chapter, align='center', font_pt=header_font + 1),
            OxmlElement('w:p'),
        ]
    )
    # Add logo to cell 3 of first-page table via _Cell
    tc3_first = tbl_first.findall('.//' + qn('w:tc'))[2]
    cell3_first = _Cell(tc3_first, first_header)
    p3f = cell3_first.add_paragraph()
    p3f.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists(LOGO_PATH):
        p3f.add_run().add_picture(LOGO_PATH, width=Inches(LOGO_W_INCHES), height=Inches(LOGO_H_INCHES))
    else:
        p3f.add_run("RBD")
    first_header._element.insert(0, tbl_first)

    # ── Pages 2+ header: [Page No.] | [Book Name] | [Topic] | [Logo] ──────────
    header = sec.header
    for p in list(header.paragraphs):
        p._element.getparent().remove(p._element)

    tbl_main = build_header_table(
        [PAGE_COL_DXA, MID_COL_DXA, TOPIC_COL_DXA, LOGO_COL_DXA],
        [
            make_page_num_para(align='left'),
            make_text_para(book_name,   align='center'),
            make_text_para(topic_text,  align='right'),
            OxmlElement('w:p'),
        ]
    )
    # Add logo to cell 4 of main table
    tc4_main = tbl_main.findall('.//' + qn('w:tc'))[3]
    cell4_main = _Cell(tc4_main, header)
    p3m = cell4_main.add_paragraph()
    p3m.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists(LOGO_PATH):
        p3m.add_run().add_picture(LOGO_PATH, width=Inches(LOGO_W_INCHES), height=Inches(LOGO_H_INCHES))
    else:
        p3m.add_run("RBD")
    header._element.insert(0, tbl_main)

    # ── Write questions ────────────────────────────────────────────────────────
    for q in questions:
        fill_cell(doc, q, include_metadata=include_metadata)

    return doc


# =============================================================================
# HTML PREVIEW
# =============================================================================
def render_q_preview(q):
    l1px = level1_indent * 96
    l2px = level2_indent * 96

    option_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
    opts_html = ""
    for idx, group in enumerate(option_groups):
        text    = ("&nbsp;&nbsp;&nbsp;&nbsp;".join(f"{o['key']} {o['text']}" for o in group)
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

    suchi_html           = ""
    display_question     = q['question']
    suchi_header_display = ""
    if "[SUCHI_HEADER]" in display_question:
        parts                = display_question.split("[SUCHI_HEADER]", 1)
        display_question     = parts[0].strip()
        suchi_header_display = parts[1].strip()

    if suchi_header_display:
        suchi_html += (
            f"<div style='margin-left:{l2px}px;font-weight:bold;"
            f"font-size:{q_font}pt;'>{suchi_header_display}</div>"
        )
    if q.get('suchi_rows'):
        suchi_html += (
            f"<table style='margin-left:{l2px}px;border-collapse:collapse;"
            f"font-size:{q_font}pt;width:calc(100% - {l2px}px);'>"
        )
        for left, right in q['suchi_rows']:
            suchi_html += (
                f"<tr>"
                f"<td style='width:50%;padding:1px 4px;vertical-align:top;'>{left}</td>"
                f"<td style='width:50%;padding:1px 4px;vertical-align:top;'>{right}</td>"
                f"</tr>"
            )
        suchi_html += "</table>"

    expl_html = ""
    if q['explanation'] or q.get('explanation_images'):
        prefix   = "➤ व्याख्या: " if expl_bullet else "व्याख्या : "
        bg_style = "background-color:#F0F0F0;padding:2px 4px;border-radius:3px;" if expl_bg else ""
        expl_html += (
            f"<div style='margin-left:{l2px}px;{bg_style}font-size:{expl_font}pt;'>"
            f"<span style='font-weight:bold;'>{prefix}</span>"
        )
        if q['explanation']:
            expl_html += q['explanation'].replace('|', '<br>')
        expl_html += "</div>"
        for img_bytes, _, __ in q.get('explanation_images', []):
            b64        = base64.b64encode(img_bytes).decode()
            expl_html += (
                f'<div style="margin-left:{l2px}px;">'
                f'<img src="data:image/png;base64,{b64}" style="max-width:100%;height:auto;"></div>'
            )

    question_html = display_question.replace('\n', '<br>')
    q_html = (
        f"<div style='margin-left:{l2px}px;text-indent:{l1px - l2px}px;"
        f"font-size:{q_font}pt;font-weight:bold;margin-bottom:2px;"
        f"white-space:pre-wrap;'>"
        f"{q['no']}. {question_html}</div>"
    )
    meta_html = ""
    if include_metadata and q.get('metadata'):
        meta_html = (
            f"<div style='text-align:right;font-size:{max(q_font-1,5)}pt;"
            f"font-style:italic;margin-left:{l2px}px;color:#555;'>"
            f"{q['metadata']}</div>"
        )

    return f"""
<div class="qblock">
  {q_html}
  {meta_html}
  {suchi_html}
  {opts_html}
  {expl_html}
  {('<hr>' if show_separator else '')}
</div>"""


def build_preview_with_pagination(questions, q_per_page, chapter_title):
    total_pages = (len(questions) + q_per_page - 1) // q_per_page
    pages_html  = []
    for page_num in range(1, total_pages + 1):
        start        = (page_num - 1) * q_per_page
        end          = min(start + q_per_page, len(questions))
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
# PDF GENERATION
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
    font   = register_devanagari_font()
    buffer = BytesIO()
    doc_pdf = SimpleDocTemplate(
        buffer,
        pagesize=(page_width * inch, page_height * inch),
        topMargin=top_margin * inch, bottomMargin=bottom_margin * inch,
        leftMargin=left_margin * inch, rightMargin=right_margin * inch
    )
    styles = getSampleStyleSheet()
    l1 = level1_indent * inch
    l2 = level2_indent * inch

    sQ    = ParagraphStyle('Q',  parent=styles['Normal'], fontSize=q_font,    leading=line_spacing,
                            fontName=font, spaceAfter=para_spacing, leftIndent=l2, firstLineIndent=l1-l2)
    sMeta = ParagraphStyle('M',  parent=styles['Normal'], fontSize=6,          leading=line_spacing,
                            fontName=font, alignment=TA_RIGHT, spaceAfter=para_spacing, leftIndent=l2)
    sOpt  = ParagraphStyle('O',  parent=styles['Normal'], fontSize=opt_font,   leading=line_spacing,
                            fontName=font, spaceAfter=para_spacing, leftIndent=l2)
    sAns  = ParagraphStyle('A',  parent=styles['Normal'], fontSize=opt_font+1.5, leading=line_spacing,
                            fontName=font, alignment=TA_RIGHT, spaceAfter=para_spacing, leftIndent=l2)
    sExpl = ParagraphStyle('E',  parent=styles['Normal'], fontSize=expl_font,  leading=line_spacing,
                            fontName=font, spaceAfter=para_spacing*2, leftIndent=l2, firstLineIndent=l1-l2,
                            backColor=colors.HexColor('#F0F0F0') if expl_bg else None)
    sH    = ParagraphStyle('H',  parent=styles['Normal'], fontSize=header_font, leading=header_font+2,
                            fontName=font, alignment=TA_CENTER,
                            backColor=colors.HexColor('#E6E6E6') if header_bg else None, spaceAfter=6)
    sSuchi = ParagraphStyle('S', parent=styles['Normal'], fontSize=q_font,     leading=line_spacing,
                             fontName=font, leftIndent=l2)

    story = [Paragraph(header_template.format(book_name=book_name, chapter_title=chapter_title, page=1), sH)]

    for q in questions:
        display_question     = q['question']
        suchi_header_display = ""
        if "[SUCHI_HEADER]" in display_question:
            parts                = display_question.split("[SUCHI_HEADER]", 1)
            display_question     = parts[0].strip()
            suchi_header_display = parts[1].strip()

        story.append(Paragraph(f"<b>{q['no']}.</b> {display_question}", sQ))
        if include_metadata and q.get('metadata'):
            story.append(Paragraph(q['metadata'], sMeta))

        # सूची table in PDF
        if suchi_header_display:
            story.append(Paragraph(f"<b>{suchi_header_display}</b>", sSuchi))
        if q.get('suchi_rows'):
            content_w = page_width - left_margin - right_margin
            col_gap   = 0.08 if num_columns == 3 else 0.12
            col_w     = (content_w - col_gap * (num_columns - 1)) / num_columns
            half_w    = (col_w - level2_indent) * inch / 2
            tdata     = [[Paragraph(left, sSuchi), Paragraph(right, sSuchi)]
                         for left, right in q['suchi_rows']]
            t = Table(tdata, colWidths=[half_w, half_w])
            t.setStyle(TableStyle([
                ('VALIGN',        (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING',   (0,0), (-1,-1), 2),
                ('RIGHTPADDING',  (0,0), (-1,-1), 2),
                ('TOPPADDING',    (0,0), (-1,-1), 1),
                ('BOTTOMPADDING', (0,0), (-1,-1), 1),
                ('GRID',          (0,0), (-1,-1), 0, colors.white),
            ]))
            story.append(t)

        opt_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
        for idx, group in enumerate(opt_groups):
            text    = ("    ".join(f"{o['key']} {o['text']}" for o in group)
                       if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
            is_last = idx == len(opt_groups) - 1
            story.append(Paragraph(text, sOpt))
            if show_correct_inline and is_last:
                story.append(Paragraph(f"<b>{q['correct']}</b>", sAns))

        if q['explanation'] or q.get('explanation_images'):
            heading   = "• व्याख्या : " if expl_bullet else "व्याख्या : "
            expl_text = heading + (q['explanation'] if q['explanation'] else "")
            story.append(Paragraph(expl_text.replace('|', '<br/>'), sExpl))
            for img_bytes, width_in, height_in in q.get('explanation_images', []):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                        tmp.write(img_bytes)
                        tmp_path = tmp.name
                    content_w = page_width - left_margin - right_margin
                    col_gap   = 0.08 if num_columns == 3 else 0.12
                    col_w     = (content_w - col_gap * (num_columns - 1)) / num_columns
                    max_w     = col_w - level2_indent - 0.05
                    img_w     = min(width_in if width_in > 0 else 1.5, max_w)
                    story.append(Image(tmp_path, width=img_w * inch, height=height_in * inch))
                    os.unlink(tmp_path)
                except Exception:
                    story.append(Paragraph("[चित्र यहाँ संलग्न करें]", sExpl))

        if show_separator:
            story.append(Spacer(1, 2))

    doc_pdf.build(story)
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
        questions     = parse_questions(doc)
        chapter_title = extract_chapter_title(doc)
    st.success(f"✅ {len(questions)} questions parsed!")

    if auto_fill:
        sample_size   = min(10, len(questions))
        total_lines   = sum(estimate_q_lines(q) for q in questions[:sample_size])
        avg_lines     = total_lines / sample_size if sample_size > 0 else 10
        usable_height = page_height - top_margin - bottom_margin - 1.2
        lines_per_page   = usable_height / (line_spacing / 72.0)
        q_per_page_est   = max(1, int(lines_per_page / avg_lines))
        total_pages_est  = (len(questions) + q_per_page_est - 1) // q_per_page_est
    else:
        q_per_page_est  = 20
        total_pages_est = (len(questions) + q_per_page_est - 1) // q_per_page_est

    st.info(f"📄 Estimated pages: {total_pages_est} ({'auto' if auto_fill else 'fixed'})")

    tab1, tab2 = st.tabs(["📄 Page Preview", "🔍 Parsed Data"])
    with tab1:
        preview_html = build_preview_with_pagination(questions, q_per_page_est, chapter_title)
        st.components.v1.html(preview_html, height=1200, scrolling=True)
    with tab2:
        for q in questions[:5]:
            with st.expander(f"Q{q['no']} – {q['question'][:60]}…"):
                st.write("**Options:**",            q['options'])
                st.write("**Correct Answer:**",     q['correct'])
                st.write("**Explanation:**",        q['explanation'][:500])
                st.write(f"**Explanation images:** {len(q.get('explanation_images', []))}")
                st.write(f"**Suchi rows:** {len(q.get('suchi_rows', []))}",
                         q.get('suchi_rows', []))

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 Generate DOCX"):
            with st.spinner(f"Generating DOCX with font: {FONT_DOCX}..."):
                final_doc   = generate_multi_page_docx(questions, chapter_title)
                docx_buffer = BytesIO()
                final_doc.save(docx_buffer)
                docx_buffer.seek(0)
                filename = f"Formatted_Output_{len(questions)}Q.docx"
                st.download_button(
                    "📥 Download DOCX",
                    docx_buffer,
                    filename,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                st.success(f"🎉 DOCX ready! Font used: **{FONT_DOCX}**")
    with c2:
        if st.button("📑 Preview PDF"):
            with st.spinner("Generating PDF preview..."):
                pdf_buffer = generate_pdf(questions, chapter_title)
                pdf_b64    = base64.b64encode(pdf_buffer.getvalue()).decode()
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{pdf_b64}" '
                    f'width="100%" height="800" type="application/pdf"></iframe>',
                    unsafe_allow_html=True
                )
                st.download_button(
                    "📥 Download PDF", pdf_buffer,
                    file_name="Formatted_Output.pdf", mime="application/pdf"
                )
                st.success("🎉 PDF preview ready!")
