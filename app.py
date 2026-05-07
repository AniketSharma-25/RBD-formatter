# # # correct 2 
# # import streamlit as st
# # from docx import Document
# # from docx.shared import Pt, Inches
# # from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
# # from docx.oxml.ns import qn
# # from docx.oxml import OxmlElement
# # from io import BytesIO
# # import re
# # import tempfile
# # import os
# # import base64
# # from reportlab.lib import colors
# # from reportlab.lib.pagesizes import inch
# # from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# # from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
# # from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
# # from reportlab.pdfbase import pdfmetrics
# # from reportlab.pdfbase.ttfonts import TTFont
# # from PIL import Image as PILImage
# # # ================= AUTH SYSTEM =================
# # import sqlite3
# # import datetime
# # import random
# # import smtplib
# # from email.mime.text import MIMEText
# # from email.mime.multipart import MIMEMultipart
# # from dotenv import load_dotenv
# # import os

# # load_dotenv()

# # GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
# # GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
# # ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
# # # st.write("EMAIL:", GMAIL_EMAIL)
# # # st.write("PASS:", GMAIL_APP_PASSWORD)

# # DB_PATH = "rbd_users.db"

# # def init_db():
# #     conn = sqlite3.connect(DB_PATH)
# #     c = conn.cursor()

# #     c.execute('''CREATE TABLE IF NOT EXISTS users (
# #         email TEXT PRIMARY KEY,
# #         created_at TEXT,
# #         is_admin BOOLEAN DEFAULT 0,
# #         can_format BOOLEAN DEFAULT 0
# #     )''')

# #     c.execute('''CREATE TABLE IF NOT EXISTS otp_codes (
# #         email TEXT,
# #         code TEXT,
# #         expires_at TEXT
# #     )''')

# #     conn.commit()
# #     conn.close()

# # def add_user(email, is_admin=False):
# #     conn = sqlite3.connect(DB_PATH)
# #     c = conn.cursor()
# #     try:
# #         now = datetime.datetime.now().isoformat()
# #         c.execute(
# #             "INSERT INTO users (email, created_at, is_admin, can_format) VALUES (?, ?, ?, ?)",
# #             (email, now, is_admin, is_admin)
# #         )
# #         conn.commit()
# #     except:
# #         pass
# #     conn.close()

# # def get_user(email):
# #     conn = sqlite3.connect(DB_PATH)
# #     c = conn.cursor()
# #     c.execute("SELECT email, is_admin, can_format FROM users WHERE email=?", (email,))
# #     row = c.fetchone()
# #     conn.close()

# #     if row:
# #         return {"email": row[0], "is_admin": bool(row[1]), "can_format": bool(row[2])}
# #     return None

# # def generate_otp():
# #     return str(random.randint(100000, 999999))

# # def send_otp_email(email, code):
# #     try:
# #         server = smtplib.SMTP("smtp.gmail.com", 587)
# #         server.starttls()

# #         server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)

# #         msg = f"Subject: OTP\n\nYour OTP is {code}"

# #         server.sendmail(GMAIL_EMAIL, email, msg)
# #         server.quit()

# #         return True

# #     except Exception as e:
# #         st.error(f"SMTP ERROR: {e}")   # 👈 VERY IMPORTANT
# #         return False

# # def store_otp(email, code):
# #     conn = sqlite3.connect(DB_PATH)
# #     c = conn.cursor()
# #     c.execute("DELETE FROM otp_codes WHERE email=?", (email,))
# #     expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
# #     c.execute("INSERT INTO otp_codes VALUES (?, ?, ?)", (email, code, expiry))
# #     conn.commit()
# #     conn.close()

# # def verify_otp(email, code):
# #     conn = sqlite3.connect(DB_PATH)
# #     c = conn.cursor()
# #     c.execute("SELECT code, expires_at FROM otp_codes WHERE email=?", (email,))
# #     row = c.fetchone()
# #     conn.close()

# #     if row and row[0] == code:
# #         if datetime.datetime.now() < datetime.datetime.fromisoformat(row[1]):
# #             return True
# #     return False

# # def login_page():
# #     st.title("🔐 Login")

# #     email = st.text_input("Email")

# #     if st.button("Send OTP"):
# #         if email:
# #             user = get_user(email)
# #             if not user:
# #                 add_user(email, email == "admin@example.com")

# #             otp = generate_otp()

# #             # 🔥 SEND EMAIL
# #             sent = send_otp_email(email, otp)

# #             if sent:
# #                 store_otp(email, otp)
# #                 st.session_state["otp_email"] = email
# #                 st.success("OTP sent to your email ✅")
# #             else:
# #                 st.error("❌ Failed to send OTP email")

# #             # st.success(f"OTP sent: {otp}")  # remove in production

# #     if "otp_email" in st.session_state:
# #         code = st.text_input("Enter OTP", type="password")

# #         if st.button("Verify"):
# #             if verify_otp(st.session_state["otp_email"], code):
# #                 user = get_user(st.session_state["otp_email"])

# #                 st.session_state["authenticated"] = True
# #                 st.session_state["user_email"] = user["email"]
# #                 st.session_state["is_admin"] = user["is_admin"]
# #                 st.session_state["can_format"] = user["can_format"]

# #                 st.success("Logged in!")
# #                 st.rerun()
# #             else:
# #                 st.error("Invalid OTP")

# #     if not st.session_state.get("authenticated"):
# #         st.stop()
   
# # def clean_text(text):
# #     if not text:
# #         return ""
    
# #     # Remove exam metadata patterns
# #     text = re.sub(r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)', '', text)
    
# #     # Remove question numbers from inside text
# #     text = re.sub(r'प्रश्न\s+\d+\s*', '', text)
# #     text = re.sub(r'^\d+\.\s*', '', text)
    
# #     # Replace tabs and multiple spaces
# #     text = text.replace('\t', ' ')
# #     text = re.sub(r'\s+', ' ', text)
    
# #     # Remove leading/trailing spaces
# #     text = text.strip()
# #     return text
    
# # def format_matching_question(text):
# #     if not text:
# #         return text

# #     text = text.replace('\n', ' ')
# #     text = re.sub(r'\s+', ' ', text).strip()

# #     # =========================================================
# #     # 🔥 EXTRACT SUCHI-I (A–D)
# #     # =========================================================
# #     suchi1 = re.findall(
# #         r'\(([A-D])\)\s*(.*?)(?=\([A-D]\)|सूची-II|$)',
# #         text,
# #         re.DOTALL
# #     )

# #     # =========================================================
# #     # 🔥 EXTRACT SUCHI-II (I–IV)
# #     # =========================================================
# #     suchi2 = re.findall(
# #         r'\(([IVX]+)\)\s*(.*?)(?=\([IVX]+\)|$)',
# #         text,
# #         re.DOTALL
# #     )

# #     # Clean
# #     suchi1 = [(k, clean_text(v)) for k, v in suchi1]
# #     suchi2 = [(k, clean_text(v)) for k, v in suchi2]

# #     # =========================================================
# #     # 🔥 HEADER
# #     # =========================================================
# #     header = re.split(r'\([A-D]\)', text, maxsplit=1)[0].strip()

# #     lines = []
# #     if header:
# #         lines.append(header)
# #         lines.append("")

# #     # =========================================================
# #     # 🔥 PARALLEL ALIGNMENT
# #     # =========================================================
# #     max_len = max(len(suchi1), len(suchi2))

# #     for i in range(max_len):
# #         left = ""
# #         right = ""

# #         if i < len(suchi1):
# #             left = f"({suchi1[i][0]}) {suchi1[i][1]}"

# #         if i < len(suchi2):
# #             right = f"({suchi2[i][0]}) {suchi2[i][1]}"

# #         if left and right:
# #             lines.append(f"{left}\t{right}")   # 🔥 TAB = COLUMN
# #         elif left:
# #             lines.append(left)
# #         elif right:
# #             lines.append(right)

# #     return "\n".join(lines)
 

    
# # st.set_page_config(page_title="RBD Formatter", layout="wide")
# # st.title("📚 RBD Publication – Smart Formatter")
# # init_db()

# # if not st.session_state.get("authenticated"):
# #     login_page()

# # # 👑 ADMIN PANEL
# # if st.session_state.get("is_admin"):
# #     st.sidebar.title("👑 Admin Panel")

# #     conn = sqlite3.connect(DB_PATH)
# #     users = conn.execute("SELECT email, can_format FROM users").fetchall()
# #     conn.close()

# #     for email, can_format in users:
# #         val = st.sidebar.checkbox(email, value=bool(can_format))
        
# #         if val != bool(can_format):
# #             conn = sqlite3.connect(DB_PATH)
# #             conn.execute("UPDATE users SET can_format=? WHERE email=?", (val, email))
# #             conn.commit()
# #             conn.close()
# #             st.rerun()

# # # 🔐 AUTH CHECK
# # if st.session_state.get("authenticated"):

# #     if not st.session_state.get("can_format"):
# #         st.error("❌ You are not allowed to use formatter")
# #         st.stop()

# #     # =========================
# #     # YOUR ORIGINAL APP STARTS
# #     # =========================

# #     uploaded_file = st.file_uploader("📄 Upload Chapter DOCX", type=["docx"])

# # # =============================================================================
# # # SIDEBAR
# # # =============================================================================
# # with st.sidebar:
# #     st.header("📄 Page Design")
# #     page_width = st.number_input("Page Width (inches)", 5.0, 12.0, 7.0, 0.1)
# #     page_height = st.number_input("Page Height (inches)", 6.0, 14.0, 9.0, 0.1)
# #     top_margin = st.number_input("Top Margin (inches)", 0.2, 1.0, 0.4, 0.05)
# #     bottom_margin = st.number_input("Bottom Margin (inches)", 0.2, 1.0, 0.4, 0.05)
# #     left_margin = st.number_input("Left Margin (inches)", 0.2, 1.0, 0.4, 0.05)
# #     right_margin = st.number_input("Right Margin (inches)", 0.2, 1.0, 0.4, 0.05)

# #     st.header("📐 Layout")
# #     num_columns = st.selectbox("Number of Columns", [2, 3], index=0)
# #     auto_fill = st.checkbox("Auto‑fill pages", True)

# #     st.header("✍️ Text Styling")
# #     q_font = st.slider("Question font size (pt)", 5.0, 12.0, 5.5, 0.5)

# #     st.markdown("**Indent levels**")
# #     st.caption("Level-1: question number '1.' and bullet '•' sit here")
# #     level1_indent = st.number_input("Level-1 indent (inches)", 0.0, 0.5, 0.0, 0.05)
# #     st.caption("Level-2: all content text starts here (question text, options, explanation)")
# #     level2_indent = st.number_input("Level-2 indent (inches)", 0.05, 1.0, 0.15, 0.05)

# #     # alias used elsewhere
# #     q_indent = level2_indent

# #     opt_font = st.slider("Options font size (pt)", 5.0, 11.0, 5.5, 0.5)
# #     opt_bold = st.checkbox("Bold options", False)
# #     ans_font = st.slider("Answer font size (pt)", 5.0, 11.0, 5.5, 0.5)
# #     ans_bold = st.checkbox("Bold answer", False)
# #     expl_font = st.slider("Explanation font size (pt)", 5.0, 10.0, 5.5, 0.5)

# #     st.header("📏 Spacing")
# #     line_spacing = st.slider("Line spacing (pt)", 8.0, 15.0, 9.5, 0.5)
# #     para_spacing = st.slider("Space after paragraph (pt)", 0.0, 6.0, 0.0, 0.5)
# #     char_spacing = st.slider("Character spacing (pt)", 0.0, 3.0, 0.0, 0.5)

# #     st.header("🎨 Option Wrapping")
# #     opts_per_line = st.selectbox("Max options per line", [2, 3, 4], index=0)
# #     if opts_per_line == 4:
# #         default_char_limit = 80
# #     elif opts_per_line == 3:
# #         default_char_limit = 68
# #     else:
# #         default_char_limit = 68
# #     opt_char_limit = st.slider("Option line length threshold", 40, 120, default_char_limit)

# #     st.header("📝 Header & Footer")
# #     header_template = st.text_input("Header template", "{book_name} | {chapter_title} | पृष्ठ {page}")
# #     book_name = st.text_input("Book name", "RBD PUBLICATION")
# #     header_font = st.slider("Header font size (pt)", 8.0, 16.0, 11.0, 0.5)
# #     header_bold = st.checkbox("Header bold", True)
# #     header_bg = st.checkbox("Header grey background", True)
# #     header_align = st.selectbox("Header alignment", ["Left", "Center", "Right"], index=1)

# #     st.header("🔢 Page Numbers")
# #     page_num_pos = st.selectbox("Position", ["None", "Top Left", "Top Center", "Top Right",
# #                                               "Bottom Left", "Bottom Center", "Bottom Right"], index=5)
# #     hide_on_first = st.checkbox("Hide on first page", False) if page_num_pos != "None" else False

# #     st.header("✨ Extras")
# #     show_correct_inline = st.checkbox("Show correct answer on last option line (right‑aligned)", True)
# #     show_separator = st.checkbox("Show line after each question", False)
# #     expl_bullet = st.checkbox("Bullet before व्याख्या heading", True)
# #     expl_bg = st.checkbox("Light grey background for explanation", True)

# #     st.header("📋 Metadata")
# #     include_metadata = st.checkbox("Include PYQ metadata in output", False,
# #         help="If checked, exam date/shift/year info found in the source file will be shown with each question.")

# #     if st.checkbox("Extra compact mode", False):
# #         line_spacing = 5.0
# #         para_spacing = 0.0
# #         q_font = 5.0
# #         opt_font = 5.0
# #         ans_font = 5.0
# #         expl_font = 5.0

# # # =============================================================================
# # # PARSING (unchanged)
# # # =============================================================================
# # def parse_questions(doc):
# #     import io

# #     questions = []
# #     current_block = []
# #     inside_question = False

# #     # -----------------------------
# #     # ✅ FIXED QUESTION DETECTION
# #     # -----------------------------
# #     def is_question_start(text):
# #         if not text:
# #             return False
# #         text = text.strip()
# #         return bool(
# #             re.match(r'^प्रश्न\s+\d+', text) or
# #             re.match(r'^\d+\.\s+', text)
# #         )

# #     # -----------------------------
# #     # ✅ HEADING DETECTION (NEW)
# #     # -----------------------------
# #     def is_heading(text):
# #         if not text:
# #             return False

# #         return bool(
# #             re.search(r'अध्याय|CHAPTER', text, re.IGNORECASE) or
# #             re.match(r'^[^\(]*\(\d{4}\)', text)  # lines ending with year like (2010)
# #         )

# #     # -----------------------------
# #     # IMAGE EXTRACTION (UNCHANGED)
# #     # -----------------------------
# #     def extract_images_from_para(para):
# #         images = []
# #         for run in para.runs:
# #             for blip in run._element.findall(
# #                 './/a:blip',
# #                 namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
# #             ):
# #                 rId = blip.get(qn('r:embed'))
# #                 image_part = doc.part.related_parts[rId]
# #                 img_bytes = image_part.blob

# #                 width_in = height_in = 1.0

# #                 extent = run._element.find(
# #                     './/wp:extent',
# #                     namespaces={'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
# #                 )

# #                 if extent is not None:
# #                     width_in = int(extent.get('cx')) / 914400.0
# #                     height_in = int(extent.get('cy')) / 914400.0
# #                 else:
# #                     try:
# #                         pil_img = PILImage.open(io.BytesIO(img_bytes))
# #                         width_in = pil_img.width / 96.0
# #                         height_in = pil_img.height / 96.0
# #                     except Exception:
# #                         pass

# #                 images.append((img_bytes, width_in, height_in))

# #         return images

# #     # -----------------------------
# #     # MAIN LOOP
# #     # -----------------------------
# #     for para in doc.paragraphs:
# #         text = para.text.strip()
# #         images = extract_images_from_para(para)

# #         # 🚀 HANDLE 'अथवा' AS NEW QUESTION BREAK
# #         if re.match(r'^\s*(अथवा|तथा)\s*$', text):
# #             if current_block:
# #                 q = process_question_block(current_block)
# #                 if q:
# #                     q['no'] = str(len(questions) + 1)
# #                     questions.append(q)

# #             current_block = []
# #             inside_question = False
# #             continue


# #         # 🚀 NORMAL QUESTION START
# #         if is_question_start(text):
# #             if current_block:
# #                 q = process_question_block(current_block)
# #                 if q:
# #                     q['no'] = str(len(questions) + 1)
# #                     questions.append(q)

# #             current_block = [(text, images)]
# #             inside_question = True
# #             continue

# #         # 🚀 CONTINUE CURRENT QUESTION
# #         if inside_question:
# #             current_block.append((text, images))

# #     # -----------------------------
# #     # LAST BLOCK
# #     # -----------------------------
# #     if current_block:
# #         q = process_question_block(current_block)
# #         if q:
# #             q['no'] = str(len(questions) + 1)
# #             questions.append(q)

# #     return questions

# # def remove_metadata_pattern(text):
# #     # Strong pattern to remove exam metadata
# #     pattern = r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)'
# #     return re.sub(pattern, '', text).strip()

# # def is_matching_question(text):
# #     if not text:
# #         return False

# #     return bool(
# #         re.search(r'सूची', text, re.IGNORECASE) or
# #         re.search(r'\(\d\)', text)
# #     )

# #     # Detect both sides (A-D and 1-4)
# #     has_alpha = re.search(r'[A-D][\.\)]', text)
# #     has_numeric = re.search(r'[1-4][\.\)]', text)

# #     return bool(has_alpha and has_numeric)
# # # ==================
# # def process_question_block(block):
# #     full_text = "\n".join(txt for txt, _ in block).strip()

# #     # =========================================================
# #     # 1. QUESTION NUMBER
# #     # =========================================================
# #     q_no = None

# #     for pattern in [r'प्रश्न\s+(\d+)', r'^(\d+)\.', r'^(\d+)\s+']:
# #         m = re.search(pattern, full_text)
# #         if m:
# #             q_no = m.group(1)
# #             full_text = full_text[m.end():].strip()
# #             break

# #     if not q_no:
# #         return None

# #     # =========================================================
# #     # 2. ANSWER
# #     # =========================================================
# #     ans_match = re.search(r'(?:सही उत्तर|उत्तर)\s*:\s*\(([a-dA-D])\)', full_text)
# #     if not ans_match:
# #         ans_match = re.search(r'\(([a-dA-D])\)\s*$', full_text)

# #     correct = f"({ans_match.group(1).lower()})" if ans_match else ""

# #     # =========================================================
# #     # 3. EXPLANATION
# #     # =========================================================
# #     explanation = ""

# #     expl_match = re.search(
# #         r'व्याख्या\s*:\s*(.*?)(?=\n\s*(\d+\.|प्रश्न\s+\d+)|$)',
# #         full_text,
# #         re.DOTALL
# #     )

# #     if expl_match:
# #         explanation = clean_text(expl_match.group(1))

# #     # =========================================================
# #     # 4. REMOVE ANSWER + EXPLANATION
# #     # =========================================================
# #     content = full_text

# #     if ans_match:
# #         content = content[:ans_match.start()]
# #     if expl_match:
# #         content = content[:expl_match.start()]

# #     content = content.strip()

# #     # =========================================================
# #     # 5. EXTRACT SUCHI BLOCK (IMPORTANT FIX)
# #     # =========================================================
# #     suchi_block = ""
# #     suchi_match = re.search(r'(सूची.*?)(?=कूट|$)', content, re.DOTALL)

# #     if suchi_match:
# #         suchi_block = suchi_match.group(1)
# #         content = content.replace(suchi_block, "")

# #     # =========================================================
# #     # 6. EXTRACT KOOT BLOCK
# #     # =========================================================
# #     koot_block = ""
# #     koot_match = re.search(r'(कूट\s*:?.*)', full_text, re.DOTALL)

# #     if koot_match:
# #         koot_block = koot_match.group(1)

# #     # =========================================================
# #     # 7. SPLIT QUESTION + OPTIONS
# #     # =========================================================
# #     first_opt = re.search(r'\([a-dA-D]\)', content)

# #     if first_opt:
# #         question_text = content[:first_opt.start()].strip()
# #         opts_raw = content[first_opt.start():]
# #     else:
# #         question_text = content
# #         opts_raw = ""

# #     question_text = clean_text(question_text)

# #     # =========================================================
# #     # 8. CLEAN OPTIONS (ONLY TRUE MCQ OPTIONS)
# #     # =========================================================
# #     options = []

# #     if opts_raw:
# #         opts_raw = re.split(
# #             r'(?=\n\s*\d+\.)|'
# #             r'(?=\n\s*प्रश्न\s+\d+)|'
# #             r'कूट|व्याख्या|उत्तर',
# #             opts_raw
# #         )[0]

# #         matches = re.findall(
# #             r'\(([a-dA-D])\)\s*(.*?)(?=\([a-dA-D]\)|$)',
# #             opts_raw,
# #             re.DOTALL
# #         )

# #         for key, text in matches:
# #             text = clean_text(text)

# #             # ❌ remove mapping (a)-(II)
# #             if re.search(r'\([a-d]\)\s*-\s*\([ivx]+\)', text, re.IGNORECASE):
# #                 continue

# #             # ❌ remove suchi contamination
# #             if "सूची" in text:
# #                 continue

# #             if text:
# #                 options.append({
# #                     "key": f"({key.lower()})",
# #                     "text": text.strip()
# #                 })

# #     options = options[:4]

# #     # =========================================================
# #     # 9. FORMAT SUCHI (PARALLEL)
# #     # =========================================================
# #     if suchi_block:
# #         suchi_block = format_matching_question(suchi_block)

# #     # =========================================================
# #     # 10. FINAL QUESTION BUILD
# #     # =========================================================
# #     final_question = question_text

# #     if suchi_block:
# #         final_question += "\n\n" + suchi_block

# #     if koot_block:
# #         final_question += "\n\n" + koot_block.strip()

# #     # =========================================================
# #     # 11. IMAGES
# #     # =========================================================
# #     explanation_images = []
# #     answer_idx = -1

# #     for idx, (txt, _) in enumerate(block):
# #         if re.search(r'(उत्तर|व्याख्या)', txt):
# #             answer_idx = idx
# #             break

# #     src = block[answer_idx+1:] if answer_idx != -1 else block

# #     for _, imgs in src:
# #         explanation_images.extend(imgs)

# #     # =========================================================
# #     # 12. EXTRACT METADATA (PYQ exam date/shift/year)
# #     # =========================================================
# #     meta_match = re.search(
# #         r'\(([^)]*\d{2,4}[^)]*(?:shift|Shift|पाली|[\[\(][^)\]]*[\]\)])[^)]*)\)',
# #         full_text
# #     )
# #     if not meta_match:
# #         # Broader: anything like (2019, Shift-I) or (Jun 2022 [S-1] (P-1))
# #         meta_match = re.search(
# #             r'\(([^)]*\d{4}[^)]*)\)',
# #             full_text
# #         )
# #     metadata_str = meta_match.group(0).strip() if meta_match else ""

# #     # =========================================================
# #     # FINAL RETURN
# #     # =========================================================
# #     return {
# #         "no": q_no,
# #         "question": final_question,
# #         "options": options,
# #         "correct": correct,
# #         "explanation": explanation,
# #         "explanation_images": explanation_images,
# #         "metadata": metadata_str
# #     }

# # # =============================================================================
# # # OPTION LAYOUT (unchanged)
# # # =============================================================================
# # def layout_options(opts, max_per_line=2, char_limit=68):
# #     result = []
# #     i = 0
# #     n = len(opts)
# #     while i < n:
# #         best = 1
# #         for k in range(max_per_line, 1, -1):
# #             if i + k <= n:
# #                 combined = "    ".join(f"{opts[i+j]['key']} {opts[i+j]['text']}" for j in range(k))
# #                 ok = all(len(opts[i+j]['text']) <= char_limit // 2 for j in range(k))
# #                 if len(combined) <= char_limit and ok:
# #                     best = k
# #                     break
# #         result.append([opts[i+j] for j in range(best)])
# #         i += best
# #     return result

# # # =============================================================================
# # # DOCX HELPERS
# # # =============================================================================
# # FONT_DOCX = "Arial"

# # def set_spacing(para, line_pts, after_pts=0, before_pts=0):
# #     pPr = para._p.get_or_add_pPr()

# #     for old in pPr.findall(qn('w:spacing')):
# #         pPr.remove(old)

# #     s = OxmlElement('w:spacing')

# #     # 🔥 IMPORTANT CHANGE
# #     s.set(qn('w:line'), str(int(line_pts * 20)))
# #     s.set(qn('w:lineRule'), 'atLeast')   # ✅ FIX

# #     s.set(qn('w:before'), str(int(before_pts * 20)))
# #     s.set(qn('w:after'), str(int(after_pts * 20)))

# #     pPr.append(s)

# # def set_char_spacing(run, spacing_pt):
# #     if spacing_pt > 0:
# #         rPr = run._r.get_or_add_rPr()
# #         sp = OxmlElement('w:spacing')
# #         sp.set(qn('w:val'), str(int(spacing_pt * 20)))
# #         rPr.append(sp)

# # def set_paragraph_background(para, color_rgb):
# #     shd = OxmlElement('w:shd')
# #     shd.set(qn('w:val'), 'clear')
# #     shd.set(qn('w:color'), 'auto')
# #     shd.set(qn('w:fill'), color_rgb)
# #     pPr = para._p.get_or_add_pPr()
# #     pPr.append(shd)

# # def _apply_ind(para, left_twips, first_twips):
# #     pPr = para._p.get_or_add_pPr()
# #     for old in pPr.findall(qn('w:ind')):
# #         pPr.remove(old)
# #     ind = OxmlElement('w:ind')
# #     ind.set(qn('w:left'), str(left_twips))
# #     if first_twips != 0:
# #         ind.set(qn('w:firstLine'), str(first_twips))
# #     pPr.append(ind)

# # def set_two_level_indent(para, l1_in, l2_in):
# #     left_twips = int(l2_in * 1440)
# #     first_twips = int((l1_in - l2_in) * 1440)
# #     _apply_ind(para, left_twips, first_twips)

# # def set_left_indent(para, left_in):
# #     _apply_ind(para, int(left_in * 1440), 0)

# # def no_border():
# #     return {"val": "nil"}

# # def set_cell_borders(cell, **kw):
# #     tc = cell._tc
# #     tcPr = tc.get_or_add_tcPr()
# #     for old in tcPr.findall(qn('w:tcBorders')):
# #         tcPr.remove(old)
# #     tcB = OxmlElement('w:tcBorders')
# #     for edge, attrs in kw.items():
# #         tag = OxmlElement(f'w:{edge}')
# #         for k, v in attrs.items():
# #             tag.set(qn(f'w:{k}'), v)
# #         tcB.append(tag)
# #     tcPr.append(tcB)

# # def remove_cell_margins(cell):
# #     tc = cell._tc
# #     tcPr = tc.get_or_add_tcPr()
# #     for old in tcPr.findall(qn('w:tcMar')):
# #         tcPr.remove(old)
# #     tcMar = OxmlElement('w:tcMar')
# #     for edge in ['top', 'left', 'bottom', 'right']:
# #         tag = OxmlElement(f'w:{edge}')
# #         tag.set(qn('w:w'), '0')
# #         tag.set(qn('w:type'), 'dxa')
# #         tcMar.append(tag)
# #     tcPr.append(tcMar)

# # from docx.oxml.ns import qn

# # def add_run(para, text, bold=False, size_pt=8, italic=False):
# #     r = para.add_run(text)
    
# #     r.bold = bold
# #     r.italic = italic
# #     r.font.size = Pt(size_pt)

# #     # ✅ Apply font properly for Hindi + English
# #     r.font.name = FONT_DOCX
# #     r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_DOCX)

# #     # Optional: ensure consistency across all scripts
# #     r._element.rPr.rFonts.set(qn('w:ascii'), FONT_DOCX)
# #     r._element.rPr.rFonts.set(qn('w:hAnsi'), FONT_DOCX)
# #     r._element.rPr.rFonts.set(qn('w:cs'), FONT_DOCX)

# #     if char_spacing > 0:
# #         set_char_spacing(r, char_spacing)

# #     return r

# # # # =============================================================================
# # # ESTIMATE QUESTION HEIGHT (unchanged)
# # # =============================================================================
# # def fill_cell(container, q, include_metadata=False):

# #     # ================= QUESTION =================
# #     p_q = container.add_paragraph()

# #     # Indentation
# #     p_q.paragraph_format.left_indent = Inches(level2_indent)
# #     p_q.paragraph_format.first_line_indent = Inches(level1_indent - level2_indent)

# #     # 🔥 TAB SYSTEM (for match questions + alignment)
# #     tab_stops = p_q.paragraph_format.tab_stops

# #     content_width = page_width - left_margin - right_margin
# #     col_gap = 0.08 if num_columns == 3 else 0.12
# #     col_width = (content_width - col_gap * (num_columns - 1)) / num_columns

# #     # Left start
# #     tab_stops.add_tab_stop(Inches(level2_indent), WD_TAB_ALIGNMENT.LEFT)

# #     # Right side (for match pairing or alignment)
# #     tab_stops.add_tab_stop(Inches(col_width - 0.2), WD_TAB_ALIGNMENT.LEFT)

# #     # Detect match-type (contains tab or multi-line structured)
# #     is_match = "\t" in q['question']

# #     # Add question number
# #     add_run(p_q, f"{q['no']}. ", bold=True, size_pt=q_font)

# #     if is_match:
# #         # 🔥 Match question handling (multi-line)
# #         lines = q['question'].split("\n")
# #         last_line_idx = len(lines) - 1

# #         for i, line in enumerate(lines):
# #             if i == 0:
# #                 add_run(p_q, line, bold=True, size_pt=q_font)
# #                 # If single-line match question, metadata goes inline here
# #                 if i == last_line_idx and include_metadata and q.get('metadata'):
# #                     tab_stops.add_tab_stop(Inches(col_width - 0.05), WD_TAB_ALIGNMENT.RIGHT)
# #                     p_q.add_run("\t")
# #                     r_meta = add_run(p_q, q['metadata'], bold=False, size_pt=max(q_font - 1.0, 5.0))
# #                     r_meta.italic = True
# #             else:
# #                 p_line = container.add_paragraph()
# #                 p_line.paragraph_format.left_indent = Inches(level2_indent)

# #                 # Apply same tab stops
# #                 tab_stops_line = p_line.paragraph_format.tab_stops
# #                 tab_stops_line.add_tab_stop(Inches(level2_indent), WD_TAB_ALIGNMENT.LEFT)
# #                 tab_stops_line.add_tab_stop(Inches(col_width - 0.2), WD_TAB_ALIGNMENT.LEFT)

# #                 if "\t" in line:
# #                     left, right = line.split("\t", 1)
# #                     add_run(p_line, left, size_pt=q_font)
# #                     p_line.add_run("\t")
# #                     add_run(p_line, right, size_pt=q_font)
# #                 else:
# #                     add_run(p_line, line, size_pt=q_font)

# #                 # Metadata inline on last line of match question
# #                 if i == last_line_idx and include_metadata and q.get('metadata'):
# #                     tab_stops_line.add_tab_stop(Inches(col_width - 0.05), WD_TAB_ALIGNMENT.RIGHT)
# #                     p_line.add_run("\t")
# #                     r_meta = add_run(p_line, q['metadata'], bold=False, size_pt=max(q_font - 1.0, 5.0))
# #                     r_meta.italic = True

# #                 set_spacing(p_line, line_pts=line_spacing, after_pts=para_spacing)
# #     else:
# #         # Normal question — append metadata inline with right tab on same paragraph
# #         add_run(p_q, q['question'], bold=True, size_pt=q_font)

# #         if include_metadata and q.get('metadata'):
# #             # Right-align metadata at end of question line via tab stop
# #             tab_stops.add_tab_stop(Inches(col_width - 0.05), WD_TAB_ALIGNMENT.RIGHT)
# #             p_q.add_run("\t")
# #             r_meta = add_run(p_q, q['metadata'], bold=False, size_pt=max(q_font - 1.0, 5.0))
# #             r_meta.italic = True

# #     set_spacing(p_q, line_pts=line_spacing, after_pts=para_spacing)

# #     # ================= METADATA (separate paragraph fallback removed — now inline above) =================

# #     # ================= OPTIONS =================
# #     option_groups = layout_options(
# #         q['options'],
# #         max_per_line=opts_per_line,
# #         char_limit=opt_char_limit
# #     )

# #     # Dynamic right alignment
# #     right_tab_pos = col_width - 0.2

# #     for idx, group in enumerate(option_groups):

# #         text = ("    ".join(f"{o['key']} {o['text']}" for o in group)
# #                 if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")

# #         p_opt = container.add_paragraph()
# #         p_opt.paragraph_format.left_indent = Inches(level2_indent)

# #         add_run(p_opt, text, bold=opt_bold, size_pt=opt_font)

# #         # Right aligned answer
# #         if show_correct_inline and idx == len(option_groups) - 1:
# #             tab_stops = p_opt.paragraph_format.tab_stops
# #             tab_stops.add_tab_stop(Inches(right_tab_pos), WD_TAB_ALIGNMENT.RIGHT)

# #             p_opt.add_run("\t")
# #             add_run(p_opt, q['correct'], bold=True, size_pt=opt_font + 1)

# #         set_spacing(p_opt, line_pts=line_spacing, after_pts=para_spacing)

# #     # ================= EXPLANATION =================
# #     if q['explanation']:

# #         p_expl = container.add_paragraph()

# #         p_expl.paragraph_format.left_indent = Inches(level2_indent)
# #         p_expl.paragraph_format.first_line_indent = Inches(level1_indent - level2_indent)

# #         if expl_bg:
# #             set_paragraph_background(p_expl, "E6E6E6")

# #         prefix = "➤ व्याख्या: " if expl_bullet else "व्याख्या: "

# #         add_run(p_expl, prefix, bold=True, size_pt=expl_font)
# #         add_run(p_expl, q['explanation'], size_pt=expl_font)

# #         set_spacing(p_expl, line_pts=line_spacing, after_pts=para_spacing * 2)

# #     # ================= IMAGES =================
# #     for img_bytes, width_in, height_in in q.get('explanation_images', []):
# #         try:
# #             with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
# #                 tmp.write(img_bytes)
# #                 tmp_path = tmp.name

# #             max_img_w = col_width - level2_indent - 0.2
# #             img_w = min(width_in if width_in > 0 else 1.5, max_img_w)

# #             p_img = container.add_paragraph()
# #             p_img.paragraph_format.left_indent = Inches(level2_indent)
# #             p_img.add_run().add_picture(tmp_path, width=Inches(img_w))

# #             os.unlink(tmp_path)

# #             set_spacing(p_img, line_pts=line_spacing, after_pts=para_spacing)

# #         except Exception:
# #             p_ph = container.add_paragraph()
# #             p_ph.paragraph_format.left_indent = Inches(level2_indent)
# #             add_run(p_ph, "[चित्र यहाँ संलग्न करें]", italic=True, size_pt=expl_font)

# #             if expl_bg:
# #                 set_paragraph_background(p_ph, "E6E6E6")

# #             set_spacing(p_ph, line_pts=line_spacing, after_pts=para_spacing)

# #     # ================= SEPARATOR =================
# #     if show_separator:
# #         p_sep = container.add_paragraph()
# #         set_spacing(p_sep, line_pts=line_spacing, after_pts=2)

# #         # ///////////////////////////////////

# # def estimate_q_lines(q):
# #     lines = 1  # question

# #     # Options
# #     lines += len(layout_options(q['options'],
# #                                max_per_line=opts_per_line,
# #                                char_limit=opt_char_limit))

# #     # Explanation
# #     if q['explanation']:
# #         lines += 1  # explanation block

# #     # Images
# #     lines += len(q.get('explanation_images', [])) * 3

# #     return lines

# # # =============================================================================
# # # PAGE GENERATION (unchanged)
# # # =============================================================================
# # from docx import Document
# # from docx.shared import Inches, Pt
# # from docx.enum.text import WD_ALIGN_PARAGRAPH
# # from docx.oxml.ns import qn
# # from docx.enum.text import WD_BREAK

# # def create_page_with_questions(questions, page_num, total_pages, chapter_title):
# #     new_doc = Document()

# #     # ================= PAGE SETUP =================
# #     sec = new_doc.sections[0]
# #     sec.page_width = Inches(page_width)
# #     sec.page_height = Inches(page_height)
# #     sec.top_margin = Inches(top_margin)
# #     sec.bottom_margin = Inches(bottom_margin)
# #     sec.left_margin = Inches(left_margin)
# #     sec.right_margin = Inches(right_margin)

# #     # ================= COLUMN SETUP =================
# #     sectPr = sec._sectPr
# #     cols = sectPr.xpath('./w:cols')[0]
# #     cols.set(qn('w:num'), str(num_columns))
# #     cols.set(qn('w:space'), "300")

# #     # ================= HEADER (real page header) =================
# #     header_text = header_template.format(
# #         book_name=book_name,
# #         chapter_title=chapter_title,
# #         page=page_num
# #     )

# #     sec.header_distance = Inches(0.2)
# #     header = sec.header
# #     for p in header.paragraphs:
# #         p._element.getparent().remove(p._element)

# #     hp = header.add_paragraph()
# #     hp.alignment = (
# #         WD_ALIGN_PARAGRAPH.LEFT if header_align == "Left"
# #         else WD_ALIGN_PARAGRAPH.RIGHT if header_align == "Right"
# #         else WD_ALIGN_PARAGRAPH.CENTER
# #     )

# #     hr = hp.add_run(header_text)
# #     hr.bold = header_bold
# #     hr.font.size = Pt(header_font)
# #     hr.font.name = FONT_DOCX
# #     hr._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_DOCX)
# #     hr._element.rPr.rFonts.set(qn('w:ascii'), FONT_DOCX)
# #     hr._element.rPr.rFonts.set(qn('w:hAnsi'), FONT_DOCX)
# #     hr._element.rPr.rFonts.set(qn('w:cs'), FONT_DOCX)

# #     if header_bg:
# #         set_paragraph_background(hp, "E6E6E6")

# #     set_spacing(hp, line_pts=header_font + 2, after_pts=4)

# #     # ================= TOP PAGE NUMBER =================
# #     if page_num_pos.startswith("Top") and not (hide_on_first and page_num == 1):
# #         tp = new_doc.add_paragraph()
# #         tp.alignment = (
# #             WD_ALIGN_PARAGRAPH.LEFT if "Left" in page_num_pos
# #             else WD_ALIGN_PARAGRAPH.RIGHT if "Right" in page_num_pos
# #             else WD_ALIGN_PARAGRAPH.CENTER
# #         )
# #         run = tp.add_run(f"पृष्ठ {page_num}")
# #         run.font.size = Pt(9)
# #         run.font.name = FONT_DOCX
# #         set_spacing(tp, line_pts=10, after_pts=3)

# #     # ================= CONTENT (FIXED) =================
# #     # 🔥 IMPORTANT: No manual column breaks
# #     # Word will auto flow content across columns

# #     for q in questions:
# #         fill_cell(new_doc, q, include_metadata=include_metadata)

# #     # ================= BOTTOM PAGE NUMBER =================
# #     if page_num_pos.startswith("Bottom") and not (hide_on_first and page_num == 1):
# #         bp = new_doc.add_paragraph()
# #         bp.alignment = (
# #             WD_ALIGN_PARAGRAPH.LEFT if "Left" in page_num_pos
# #             else WD_ALIGN_PARAGRAPH.RIGHT if "Right" in page_num_pos
# #             else WD_ALIGN_PARAGRAPH.CENTER
# #         )
# #         run = bp.add_run(f"पृष्ठ {page_num}")
# #         run.font.size = Pt(9)
# #         run.font.name = FONT_DOCX
# #         set_spacing(bp, line_pts=10, before_pts=5)

# #     # ================= PAGE BREAK =================
# #     if page_num < total_pages:
# #         new_doc.add_page_break()

# #     return new_doc
  
    

# # def generate_multi_page_docx(questions, chapter_title):
# #     doc = Document()

# #     # ================= PAGE SETUP =================
# #     sec = doc.sections[0]
# #     sec.page_width = Inches(page_width)
# #     sec.page_height = Inches(page_height)
# #     sec.top_margin = Inches(top_margin)
# #     sec.bottom_margin = Inches(bottom_margin)
# #     sec.left_margin = Inches(left_margin)
# #     sec.right_margin = Inches(right_margin)

# #     # ================= COLUMN SETUP =================
# #     sectPr = sec._sectPr
# #     cols = sectPr.xpath('./w:cols')[0]
# #     cols.set(qn('w:num'), str(num_columns))
# #     cols.set(qn('w:space'), "300")

# #     # ================= REAL PAGE HEADER (appears on every page) =================
# #     header_text = header_template.format(
# #         book_name=book_name,
# #         chapter_title=chapter_title,
# #         page=""  # page numbers handled separately via page_num_pos
# #     ).rstrip()

# #     sec.header_distance = Inches(0.2)
# #     header = sec.header
# #     # Clear any default empty paragraph
# #     for p in header.paragraphs:
# #         p._element.getparent().remove(p._element)

# #     hp = header.add_paragraph()
# #     hp.alignment = (
# #         WD_ALIGN_PARAGRAPH.LEFT if header_align == "Left"
# #         else WD_ALIGN_PARAGRAPH.RIGHT if header_align == "Right"
# #         else WD_ALIGN_PARAGRAPH.CENTER
# #     )

# #     hr = hp.add_run(header_text)
# #     hr.bold = header_bold
# #     hr.font.size = Pt(header_font)
# #     hr.font.name = FONT_DOCX
# #     hr._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_DOCX)
# #     hr._element.rPr.rFonts.set(qn('w:ascii'), FONT_DOCX)
# #     hr._element.rPr.rFonts.set(qn('w:hAnsi'), FONT_DOCX)
# #     hr._element.rPr.rFonts.set(qn('w:cs'), FONT_DOCX)

# #     if header_bg:
# #         set_paragraph_background(hp, "E6E6E6")

# #     set_spacing(hp, line_pts=header_font + 2, after_pts=4)

# #     # ================= CONTENT =================
# #     for q in questions:
# #         fill_cell(doc, q, include_metadata=include_metadata)

# #     return doc

# # # =============================================================================
# # # HTML PREVIEW – explanation uses hanging indent
# # # =============================================================================
# # def render_q_preview(q):
# #     l1px = level1_indent * 96
# #     l2px = level2_indent * 96
# #     hang_px = l1px - l2px   # negative

# #     option_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
# #     opts_html = ""
# #     for idx, group in enumerate(option_groups):
# #         text = ("&nbsp;&nbsp;&nbsp;&nbsp;".join(f"{o['key']} {o['text']}" for o in group)
# #                 if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
# #         is_last = idx == len(option_groups) - 1
# #         if show_correct_inline and is_last:
# #             opts_html += (
# #                 f"<div style='display:flex;justify-content:space-between;"
# #                 f"margin-left:{l2px}px;font-size:{opt_font}pt;'>"
# #                 f"<span>{text}</span>"
# #                 f"<span style='font-weight:900;font-size:{opt_font+1.5}pt;'>{q['correct']}</span>"
# #                 f"</div>"
# #             )
# #         else:
# #             opts_html += f"<div style='margin-left:{l2px}px;font-size:{opt_font}pt;'>{text}</div>"

# #     # Explanation – single block with hanging indent
# #     expl_html = ""
# #     if q['explanation'] or q.get('explanation_images'):
# #         heading_prefix = "➤ व्याख्या: " if expl_bullet else "व्याख्या : "
# #         bg_style = "background-color:#F0F0F0;padding:2px 4px;border-radius:3px;" if expl_bg else ""
# #         expl_html += (
# #             f"<div style='margin-left:{l2px}px;text-indent:{hang_px}px;{bg_style}font-size:{expl_font}pt;'>"
# #             f"<span style='font-weight:bold;'>{heading_prefix}</span>"
# #         )
# #         if q['explanation']:
# #             expl_html += q['explanation'].replace('|', '<br>')
# #         expl_html += "</div>"

# #         # Images after the text
# #         for img_bytes, _, __ in q.get('explanation_images', []):
# #             b64 = base64.b64encode(img_bytes).decode()
# #             expl_html += (
# #                 f'<div style="margin-left:{l2px}px;">'
# #                 f'<img src="data:image/png;base64,{b64}" style="max-width:100%;height:auto;"></div>'
# #             )

# #     question_html = q['question'].replace('\n', '<br>')

# #     # Build inline metadata: appended right after question text using flex
# #     # If the question text + metadata fit on one line → same line (space-between)
# #     # If not → metadata wraps to its own right-aligned line naturally
# #     if include_metadata and q.get('metadata'):
# #         meta_span = (
# #             f"<span style='font-weight:normal;font-style:italic;"
# #             f"font-size:{max(q_font-1,5)}pt;color:#555;white-space:nowrap;'>"
# #             f"&nbsp;&nbsp;{q['metadata']}</span>"
# #         )
# #         q_html = (
# #             f"<div style='margin-left:{l2px}px;text-indent:{hang_px}px;"
# #             f"font-size:{q_font}pt;font-weight:bold;margin-bottom:2px;"
# #             f"display:flex;justify-content:space-between;align-items:flex-end;'>"
# #             f"<span style='white-space:pre-wrap;flex:1;'>{q['no']}. {question_html}</span>"
# #             f"{meta_span}"
# #             f"</div>"
# #         )
# #     else:
# #         q_html = (
# #             f"<div style='margin-left:{l2px}px;text-indent:{hang_px}px;"
# #             f"font-size:{q_font}pt;font-weight:bold;margin-bottom:2px;"
# #             f"white-space:pre-wrap;'>"
# #             f"{q['no']}. {question_html}</div>"
# #         )

# #     return f"""
# # <div class="qblock">
# #   {q_html}
# #   {opts_html}
# #   {expl_html}
# #   {('<hr>' if show_separator else '')}
# # </div>"""

# # def build_preview_with_pagination(questions, q_per_page, chapter_title):
# #     total_pages = (len(questions) + q_per_page - 1) // q_per_page
# #     pages_html = []
# #     for page_num in range(1, total_pages + 1):
# #         start = (page_num - 1) * q_per_page
# #         end = min(start + q_per_page, len(questions))
# #         content_html = "".join(render_q_preview(q) for q in questions[start:end])
# #         pages_html.append(f"""
# # <div class="page" style="width:{page_width*96}px;min-height:{page_height*96}px;background:white;
# #   margin:0 auto 20px auto;padding:{top_margin*96}px {right_margin*96}px {bottom_margin*96}px {left_margin*96}px;
# #   box-shadow:0 4px 24px rgba(0,0,0,0.5);">
# #   <div style="background:#E6E6E6;padding:4px;border-radius:3px;text-align:center;
# #     font-weight:bold;margin-bottom:10px;">
# #     {header_template.format(book_name=book_name, chapter_title=chapter_title, page=page_num)}
# #   </div>
# #   <div style="column-count:{num_columns};column-gap:18px;">{content_html}</div>
# # </div>""")

# #     return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
# # <style>
# #   *{{box-sizing:border-box;margin:0;padding:0;}}
# #   body{{background:#666;font-family:'Mangal','Arial','Noto Sans Devanagari','Arial',sans-serif;padding:20px;}}
# #   .qblock{{margin-bottom:5px;padding-bottom:4px;break-inside:avoid;page-break-inside:avoid;}}
# #   hr{{margin:4px 0;border:0;border-top:1px dotted #ccc;}}
# # </style>
# # </head><body>{''.join(pages_html)}</body></html>"""

# # # =============================================================================
# # # PDF GENERATION – explanation uses firstLineIndent
# # # =============================================================================
# # def register_devanagari_font():
# #     for path in [
# #         "C:/Windows/Fonts/Mangal.ttf",
# #         "C:/Windows/Fonts/Nirmala.ttf",
# #         "/usr/share/fonts/truetype/msttcorefonts/Mangal.ttf",
# #         "/usr/share/fonts/truetype/lohit/Lohit-Devanagari.ttf",
# #         "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
# #     ]:
# #         if os.path.exists(path):
# #             try:
# #                 pdfmetrics.registerFont(TTFont('Devanagari', path))
# #                 return 'Devanagari'
# #             except Exception:
# #                 continue
# #     st.warning("⚠️ No Devanagari font found. PDF will use Helvetica.")
# #     return 'Helvetica'


# # def generate_pdf(questions, chapter_title):
# #     font = register_devanagari_font()
# #     buffer = BytesIO()
# #     doc = SimpleDocTemplate(buffer,
# #                             pagesize=(page_width*inch, page_height*inch),
# #                             topMargin=top_margin*inch, bottomMargin=bottom_margin*inch,
# #                             leftMargin=left_margin*inch, rightMargin=right_margin*inch)
# #     styles = getSampleStyleSheet()
# #     l1 = level1_indent * inch
# #     l2 = level2_indent * inch

# #     sQ  = ParagraphStyle('Q',  parent=styles['Normal'], fontSize=q_font,    leading=line_spacing,
# #                           fontName=font, spaceAfter=para_spacing, leftIndent=l2, firstLineIndent=l1-l2)
# #     sMeta = ParagraphStyle('M', parent=styles['Normal'], fontSize=6,          leading=line_spacing,
# #                           fontName=font, alignment=TA_RIGHT, spaceAfter=para_spacing, leftIndent=l2)
# #     sOpt  = ParagraphStyle('O', parent=styles['Normal'], fontSize=opt_font,  leading=line_spacing,
# #                           fontName=font, spaceAfter=para_spacing, leftIndent=l2)
# #     sAns  = ParagraphStyle('A', parent=styles['Normal'], fontSize=opt_font+1.5, leading=line_spacing,
# #                           fontName=font, alignment=TA_RIGHT, spaceAfter=para_spacing, leftIndent=l2)
# #     sExpl = ParagraphStyle('E', parent=styles['Normal'], fontSize=expl_font, leading=line_spacing,
# #                           fontName=font, spaceAfter=para_spacing*2, leftIndent=l2, firstLineIndent=l1-l2,
# #                           backColor=colors.HexColor('#F0F0F0') if expl_bg else None)
# #     sH    = ParagraphStyle('H', parent=styles['Normal'], fontSize=header_font, leading=header_font+2,
# #                           fontName=font, alignment=TA_CENTER,
# #                           backColor=colors.HexColor('#E6E6E6') if header_bg else None, spaceAfter=6)

# #     story = [Paragraph(header_template.format(book_name=book_name, chapter_title=chapter_title, page=1), sH)]

# #     for q in questions:
# #         story.append(Paragraph(f"<b>{q['no']}.</b> {q['question']}", sQ))
# #         if include_metadata and q.get('metadata'):
# #             story.append(Paragraph(q['metadata'], sMeta))

# #         opt_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
# #         for idx, group in enumerate(opt_groups):
# #             text = ("    ".join(f"{o['key']} {o['text']}" for o in group)
# #                     if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
# #             is_last = idx == len(opt_groups) - 1
# #             story.append(Paragraph(text, sOpt))
# #             if show_correct_inline and is_last:
# #                 story.append(Paragraph(f"<b>{q['correct']}</b>", sAns))

# #         if q['explanation'] or q.get('explanation_images'):
# #             heading = ("• व्याख्या : " if expl_bullet else "व्याख्या : ")
# #             expl_text = heading + (q['explanation'] if q['explanation'] else "")
# #             story.append(Paragraph(expl_text.replace('|', '<br/>'), sExpl))

# #             for img_bytes, width_in, height_in in q.get('explanation_images', []):
# #                 try:
# #                     with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
# #                         tmp.write(img_bytes)
# #                         tmp_path = tmp.name
# #                     content_w = page_width - left_margin - right_margin
# #                     col_gap = 0.08 if num_columns == 3 else 0.12
# #                     col_w = (content_w - col_gap * (num_columns - 1)) / num_columns
# #                     max_w = col_w - level2_indent - 0.05
# #                     img_w = min(width_in if width_in > 0 else 1.5, max_w)
# #                     story.append(Image(tmp_path, width=img_w*inch, height=height_in*inch))
# #                     os.unlink(tmp_path)
# #                 except Exception:
# #                     story.append(Paragraph("[चित्र यहाँ संलग्न करें]", sExpl))

# #         if show_separator:
# #             story.append(Spacer(1, 2))

# #     doc.build(story)
# #     buffer.seek(0)
# #     return buffer

# # # =============================================================================
# # # CHAPTER TITLE EXTRACTION
# # # =============================================================================
# # def extract_chapter_title(doc):
# #     for para in doc.paragraphs[:10]:
# #         if "अध्याय" in para.text or "CHAPTER" in para.text.upper():
# #             title = para.text.strip()
# #             return title[:80] + "..." if len(title) > 80 else title
# #     return "RBD PUBLICATION — अध्याय"

# # # =============================================================================
# # # MAIN APP
# # # =============================================================================
# # if uploaded_file:
# #     doc = Document(uploaded_file)
# #     with st.spinner("Parsing questions..."):
# #         questions = parse_questions(doc)
# #         chapter_title = extract_chapter_title(doc)
# #     st.success(f"✅ {len(questions)} questions parsed!")

# #     if auto_fill:
# #         sample_size = min(10, len(questions))
# #         total_lines = sum(estimate_q_lines(q) for q in questions[:sample_size])
# #         avg_lines = total_lines / sample_size if sample_size > 0 else 10
# #         usable_height = page_height - top_margin - bottom_margin - 1.2
# #         lines_per_page = usable_height / (line_spacing / 72.0)
# #         q_per_page_est = max(1, int(lines_per_page / avg_lines))
# #         total_pages_est = (len(questions) + q_per_page_est - 1) // q_per_page_est
# #     else:
# #         q_per_page_est = 20
# #         total_pages_est = (len(questions) + q_per_page_est - 1) // q_per_page_est

# #     st.info(f"📄 Estimated pages: {total_pages_est} ({'auto' if auto_fill else 'fixed'})")

# #     tab1, tab2 = st.tabs(["📄 Page Preview", "🔍 Parsed Data"])
# #     with tab1:
# #         preview_html = build_preview_with_pagination(questions, q_per_page_est, chapter_title)
# #         st.components.v1.html(preview_html, height=1200, scrolling=True)
# #     with tab2:
# #         for q in questions[:5]:
# #             with st.expander(f"Q{q['no']} – {q['question'][:60]}…"):
# #                 st.write("**Options:**", q['options'])
# #                 st.write("**Correct Answer:**", q['correct'])
# #                 st.write("**Explanation:**", q['explanation'][:500])
# #                 st.write(f"**Explanation images:** {len(q.get('explanation_images', []))}")

# #     st.markdown("---")
# #     c1, c2 = st.columns(2)
# #     with c1:
# #         if st.button("🚀 Generate DOCX"):
# #             with st.spinner("Generating DOCX..."):
# #                 final_doc = generate_multi_page_docx(questions, chapter_title)
# #                 filename = f"Formatted_Output_{len(questions)}Q.docx"
# #                 final_doc.save(filename)
# #                 with open(filename, "rb") as f:
# #                     st.download_button("📥 Download DOCX", f, filename,
# #                                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
# #                 st.success("🎉 DOCX ready!")
# #     with c2:
# #         if st.button("📑 Preview PDF"):
# #             with st.spinner("Generating PDF preview..."):
# #                 pdf_buffer = generate_pdf(questions, chapter_title)
# #                 pdf_b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
# #                 st.markdown(
# #                     f'<iframe src="data:application/pdf;base64,{pdf_b64}" '
# #                     f'width="100%" height="800" type="application/pdf"></iframe>',
# #                     unsafe_allow_html=True)
# #                 st.download_button("📥 Download PDF", pdf_buffer,
# #                                    file_name="Formatted_Output.pdf", mime="application/pdf")
# #                 st.success("🎉 PDF preview ready!")


# # # #  correctv 2 - Font Selection + No file save to disk
# import streamlit as st
# from docx import Document
# from docx.shared import Pt, Inches
# from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
# from docx.oxml.ns import qn
# from docx.oxml import OxmlElement
# from io import BytesIO
# import re
# import tempfile
# import os
# import base64
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import inch
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
# from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from PIL import Image as PILImage
# # ================= AUTH SYSTEM =================
# import sqlite3
# import datetime
# import random
# import smtplib
# import uuid
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from dotenv import load_dotenv
# import os

# load_dotenv()

# GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
# GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
# ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

# DB_PATH = "rbd_users.db"

# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()

#     c.execute('''CREATE TABLE IF NOT EXISTS users (
#         email TEXT PRIMARY KEY,
#         created_at TEXT,
#         is_admin BOOLEAN DEFAULT 0,
#         can_format BOOLEAN DEFAULT 0
#     )''')

#     c.execute('''CREATE TABLE IF NOT EXISTS otp_codes (
#         email TEXT,
#         code TEXT,
#         expires_at TEXT
#     )''')

#     c.execute('''CREATE TABLE IF NOT EXISTS sessions (
#         token TEXT PRIMARY KEY,
#         email TEXT,
#         created_at TEXT,
#         expires_at TEXT,
#         is_revoked BOOLEAN DEFAULT 0
#     )''')

#     conn.commit()
#     conn.close()

# def add_user(email, is_admin=False):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     try:
#         now = datetime.datetime.now().isoformat()
#         c.execute(
#             "INSERT INTO users (email, created_at, is_admin, can_format) VALUES (?, ?, ?, ?)",
#             (email, now, is_admin, is_admin)
#         )
#         conn.commit()
#     except:
#         pass
#     conn.close()

# def get_user(email):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT email, is_admin, can_format FROM users WHERE email=?", (email,))
#     row = c.fetchone()
#     conn.close()

#     if row:
#         return {"email": row[0], "is_admin": bool(row[1]), "can_format": bool(row[2])}
#     return None

# def generate_otp():
#     return str(random.randint(100000, 999999))

# def send_otp_email(email, code):
#     try:
#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()

#         server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)

#         msg = f"Subject: OTP\n\nYour OTP is {code}"

#         server.sendmail(GMAIL_EMAIL, email, msg)
#         server.quit()

#         return True

#     except Exception as e:
#         st.error(f"SMTP ERROR: {e}")
#         return False

# def store_otp(email, code):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("DELETE FROM otp_codes WHERE email=?", (email,))
#     expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
#     c.execute("INSERT INTO otp_codes VALUES (?, ?, ?)", (email, code, expiry))
#     conn.commit()
#     conn.close()

# def verify_otp(email, code):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT code, expires_at FROM otp_codes WHERE email=?", (email,))
#     row = c.fetchone()
#     conn.close()

#     if row and row[0] == code:
#         if datetime.datetime.now() < datetime.datetime.fromisoformat(row[1]):
#             return True
#     return False

# def create_session(email):
#     """Create a persistent session token valid for 30 days."""
#     token = str(uuid.uuid4())
#     now = datetime.datetime.now()
#     expires = now + datetime.timedelta(days=30)
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute(
#         "INSERT INTO sessions (token, email, created_at, expires_at, is_revoked) VALUES (?, ?, ?, ?, 0)",
#         (token, email, now.isoformat(), expires.isoformat())
#     )
#     conn.commit()
#     conn.close()
#     return token

# def validate_session(token):
#     """Return user dict if token is valid and not expired/revoked, else None."""
#     if not token:
#         return None
#     conn = sqlite3.connect(DB_PATH)
#     row = conn.execute(
#         "SELECT email, expires_at, is_revoked FROM sessions WHERE token=?",
#         (token,)
#     ).fetchone()
#     conn.close()
#     if not row:
#         return None
#     email, expires_at, is_revoked = row
#     if is_revoked:
#         return None
#     if datetime.datetime.now() > datetime.datetime.fromisoformat(expires_at):
#         return None
#     return get_user(email)

# def revoke_user_sessions(email):
#     """Revoke all active sessions for a user (admin action)."""
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("UPDATE sessions SET is_revoked=1 WHERE email=?", (email,))
#     conn.commit()
#     conn.close()

# def revoke_session(token):
#     """Revoke a single session token (logout)."""
#     if not token:
#         return
#     conn = sqlite3.connect(DB_PATH)
#     conn.execute("UPDATE sessions SET is_revoked=1 WHERE token=?", (token,))
#     conn.commit()
#     conn.close()

# def get_user_sessions(email):
#     """Get all active sessions for a user."""
#     conn = sqlite3.connect(DB_PATH)
#     rows = conn.execute(
#         "SELECT token, created_at, expires_at FROM sessions WHERE email=? AND is_revoked=0",
#         (email,)
#     ).fetchall()
#     conn.close()
#     return rows

# def login_page():

#     st.title("🔐 Login")

#     email = st.text_input("Email")

#     if st.button("Send OTP"):
#         if email:
#             user = get_user(email)
#             if not user:
#                 add_user(email, email == "admin@example.com")

#             otp = generate_otp()

#             sent = send_otp_email(email, otp)

#             if sent:
#                 store_otp(email, otp)
#                 st.session_state["otp_email"] = email
#                 st.success("OTP sent to your email ✅")
#             else:
#                 st.error("❌ Failed to send OTP email")

#     if "otp_email" in st.session_state:
#         code = st.text_input("Enter OTP", type="password")

#         if st.button("Verify"):
#             if verify_otp(st.session_state["otp_email"], code):
#                 user = get_user(st.session_state["otp_email"])

#                 # Create a persistent session token
#                 token = create_session(user["email"])

#                 st.session_state["authenticated"] = True
#                 st.session_state["user_email"] = user["email"]
#                 st.session_state["is_admin"] = user["is_admin"]
#                 st.session_state["can_format"] = user["can_format"]
#                 st.session_state["session_token"] = token

#                 # Store token in URL query params so it survives page refresh
#                 st.query_params["session"] = token

#                 st.success("Logged in!")
#                 st.rerun()
#             else:
#                 st.error("Invalid OTP")

#     if not st.session_state.get("authenticated"):
#         st.stop()
   
# def clean_text(text):
#     if not text:
#         return ""
    
#     text = re.sub(r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)', '', text)
#     text = re.sub(r'प्रश्न\s+\d+\s*', '', text)
#     text = re.sub(r'^\d+\.\s*', '', text)
#     text = re.sub(r'^\.+\s*', '', text)
#     text = text.replace('\t', ' ')
#     text = re.sub(r'\s+', ' ', text)
#     text = text.strip()
#     return text
    
# def format_matching_question(text):
#     if not text:
#         return text

#     text = text.replace('\n', ' ')
#     text = re.sub(r'\s+', ' ', text).strip()

#     suchi1 = re.findall(
#         r'\(([A-D])\)\s*(.*?)(?=\([A-D]\)|सूची-II|$)',
#         text,
#         re.DOTALL
#     )

#     suchi2 = re.findall(
#         r'\(([IVX]+)\)\s*(.*?)(?=\([IVX]+\)|$)',
#         text,
#         re.DOTALL
#     )

#     suchi1 = [(k, clean_text(v)) for k, v in suchi1]
#     suchi2 = [(k, clean_text(v)) for k, v in suchi2]

#     header = re.split(r'\([A-D]\)', text, maxsplit=1)[0].strip()

#     lines = []
#     if header:
#         lines.append(header)
#         lines.append("")

#     max_len = max(len(suchi1), len(suchi2))

#     for i in range(max_len):
#         left = ""
#         right = ""

#         if i < len(suchi1):
#             left = f"({suchi1[i][0]}) {suchi1[i][1]}"

#         if i < len(suchi2):
#             right = f"({suchi2[i][0]}) {suchi2[i][1]}"

#         if left and right:
#             lines.append(f"{left}\t{right}")
#         elif left:
#             lines.append(left)
#         elif right:
#             lines.append(right)

#     return "\n".join(lines)
 

# # =============================================================================
# # FONT CONFIGURATION
# # =============================================================================

# # Hindi fonts
# HINDI_FONTS = {
#     "Mangal": "Mangal",
#     "Nirmala UI": "Nirmala UI",
#     "Kokila": "Kokila",
#     "Aparajita": "Aparajita",
#     "Utsaah": "Utsaah",
#     "Kruti Dev 010": "Kruti Dev 010",
#     "Devanagari New": "Devanagari New",
# }

# # English fonts
# ENGLISH_FONTS = {
#     "Arial": "Arial",
#     "Times New Roman": "Times New Roman",
#     "Calibri": "Calibri",
#     "Georgia": "Georgia",
#     "Cambria": "Cambria",
#     "Garamond": "Garamond",
#     "Trebuchet MS": "Trebuchet MS",
#     "Verdana": "Verdana",
#     "Book Antiqua": "Book Antiqua",
#     "Century Gothic": "Century Gothic",
# }

# st.set_page_config(page_title="RBD Formatter", layout="wide")
# st.title("📚 RBD Publication – Smart Formatter")
# init_db()

# # ── Auto-restore session from URL query param ──────────────────────────────
# if not st.session_state.get("authenticated"):
#     token = st.query_params.get("session")
#     if token:
#         user = validate_session(token)
#         if user:
#             st.session_state["authenticated"] = True
#             st.session_state["user_email"] = user["email"]
#             st.session_state["is_admin"] = user["is_admin"]
#             st.session_state["can_format"] = user["can_format"]
#             st.session_state["session_token"] = token
#         else:
#             # Token invalid/revoked – clear it from URL
#             st.query_params.clear()
# # ──────────────────────────────────────────────────────────────────────────

# if not st.session_state.get("authenticated"):
#     login_page()

# # 👑 ADMIN PANEL
# if st.session_state.get("is_admin"):
#     st.sidebar.title("👑 Admin Panel")

#     conn = sqlite3.connect(DB_PATH)
#     users = conn.execute("SELECT email, can_format FROM users").fetchall()
#     conn.close()

#     for email, can_format in users:
#         col1, col2 = st.sidebar.columns([3, 1])
#         with col1:
#             val = st.checkbox(email, value=bool(can_format), key=f"perm_{email}")
#         with col2:
#             if st.button("🚫", key=f"revoke_{email}", help=f"Revoke all sessions for {email}"):
#                 revoke_user_sessions(email)
#                 st.sidebar.success(f"Sessions revoked for {email}")
#                 st.rerun()

#         if val != bool(can_format):
#             conn = sqlite3.connect(DB_PATH)
#             conn.execute("UPDATE users SET can_format=? WHERE email=?", (val, email))
#             conn.commit()
#             conn.close()
#             st.rerun()

# # 🚪 Logout button (shown to all authenticated users)
# if st.session_state.get("authenticated"):
#     st.sidebar.markdown("---")
#     st.sidebar.write(f"👤 {st.session_state.get('user_email', '')}")
#     if st.sidebar.button("🚪 Logout"):
#         revoke_session(st.session_state.get("session_token"))
#         st.session_state.clear()
#         st.query_params.clear()
#         st.rerun()

# # 🔐 AUTH CHECK
# if st.session_state.get("authenticated"):

#     if not st.session_state.get("can_format"):
#         st.error("❌ You are not allowed to use formatter")
#         st.stop()

#     uploaded_file = st.file_uploader("📄 Upload Chapter DOCX", type=["docx"])

# # =============================================================================
# # SIDEBAR
# # =============================================================================
# with st.sidebar:
#     st.header("📄 Page Design")
#     page_width = st.number_input("Page Width (inches)", 5.0, 12.0, 7.0, 0.1)
#     page_height = st.number_input("Page Height (inches)", 6.0, 14.0, 9.0, 0.1)
#     top_margin = st.number_input("Top Margin (inches)", 0.2, 1.0, 0.4, 0.05)
#     bottom_margin = st.number_input("Bottom Margin (inches)", 0.2, 1.0, 0.4, 0.05)
#     left_margin = st.number_input("Left Margin (inches)", 0.2, 1.0, 0.4, 0.05)
#     right_margin = st.number_input("Right Margin (inches)", 0.2, 1.0, 0.4, 0.05)

#     st.header("📐 Layout")
#     num_columns = st.selectbox("Number of Columns", [2, 3], index=0)
#     auto_fill = st.checkbox("Auto‑fill pages", True)

#     # =============================================================================
#     # FONT SELECTION FOR OUTPUT DOCX
#     # =============================================================================
#     st.header("🔤 Font Settings (Output DOCX)")

#     font_language = st.selectbox(
#         "Select Font Language",
#         ["Hindi (Devanagari)", "English"],
#         index=0,
#         help="Choose the language/script of your document to apply appropriate fonts"
#     )

#     if font_language == "Hindi (Devanagari)":
#         selected_font_name = st.selectbox(
#             "Select Hindi Font",
#             list(HINDI_FONTS.keys()),
#             index=0,
#             help="These fonts support Devanagari script for Hindi content"
#         )
#         FONT_DOCX = HINDI_FONTS[selected_font_name]
#     else:
#         selected_font_name = st.selectbox(
#             "Select English Font",
#             list(ENGLISH_FONTS.keys()),
#             index=0,
#             help="Standard English fonts for Latin script content"
#         )
#         FONT_DOCX = ENGLISH_FONTS[selected_font_name]

#     st.caption(f"✅ Selected font: **{FONT_DOCX}** — will be applied to all text in output DOCX")

#     st.header("✍️ Text Styling")
#     q_font = st.slider("Question font size (pt)", 5.0, 12.0, 5.5, 0.5)

#     st.markdown("**Indent levels**")
#     st.caption("Level-1: question number '1.' and bullet '•' sit here")
#     level1_indent = st.number_input("Level-1 indent (inches)", 0.0, 0.5, 0.0, 0.05)
#     st.caption("Level-2: all content text starts here (question text, options, explanation)")
#     level2_indent = st.number_input("Level-2 indent (inches)", 0.05, 1.0, 0.15, 0.05)

#     q_indent = level2_indent

#     opt_font = st.slider("Options font size (pt)", 5.0, 11.0, 5.5, 0.5)
#     opt_bold = st.checkbox("Bold options", False)
#     ans_font = st.slider("Answer font size (pt)", 5.0, 11.0, 5.5, 0.5)
#     ans_bold = st.checkbox("Bold answer", False)
#     expl_font = st.slider("Explanation font size (pt)", 5.0, 10.0, 5.5, 0.5)

#     st.header("📏 Spacing")
#     line_spacing = st.slider("Line spacing (pt)", 8.0, 15.0, 9.5, 0.5)
#     para_spacing = st.slider("Space after paragraph (pt)", 0.0, 6.0, 0.0, 0.5)
#     char_spacing = st.slider("Character spacing (pt)", 0.0, 3.0, 0.0, 0.5)

#     st.header("🎨 Option Wrapping")
#     opts_per_line = st.selectbox("Max options per line", [2, 3, 4], index=0)
#     if opts_per_line == 4:
#         default_char_limit = 80
#     elif opts_per_line == 3:
#         default_char_limit = 68
#     else:
#         default_char_limit = 68
#     opt_char_limit = st.slider("Option line length threshold", 40, 120, default_char_limit)

#     st.header("📝 Header & Footer")
#     header_template = st.text_input("Header template", "{book_name} | {chapter_title} | पृष्ठ {page}")
#     book_name = st.text_input("Book name", "RBD PUBLICATION")
#     header_font = st.slider("Header font size (pt)", 8.0, 16.0, 11.0, 0.5)
#     header_bold = st.checkbox("Header bold", True)
#     header_bg = st.checkbox("Header grey background", True)
#     header_align = st.selectbox("Header alignment", ["Left", "Center", "Right"], index=1)

#     st.header("🔢 Page Numbers")
#     page_num_pos = st.selectbox("Position", ["None", "Top Left", "Top Center", "Top Right",
#                                               "Bottom Left", "Bottom Center", "Bottom Right"], index=5)
#     hide_on_first = st.checkbox("Hide on first page", False) if page_num_pos != "None" else False

#     st.header("✨ Extras")
#     show_correct_inline = st.checkbox("Show correct answer on last option line (right‑aligned)", True)
#     show_separator = st.checkbox("Show line after each question", False)
#     expl_bullet = st.checkbox("Bullet before व्याख्या heading", True)
#     expl_bg = st.checkbox("Light grey background for explanation", True)

#     st.header("📋 Metadata")
#     include_metadata = st.checkbox("Include PYQ metadata in output", False,
#         help="If checked, exam date/shift/year info found in the source file will be shown with each question.")

#     if st.checkbox("Extra compact mode", False):
#         line_spacing = 5.0
#         para_spacing = 0.0
#         q_font = 5.0
#         opt_font = 5.0
#         ans_font = 5.0
#         expl_font = 5.0

# # =============================================================================
# # PARSING
# # =============================================================================
# def parse_questions(doc):
#     import io

#     questions = []
#     current_block = []
#     inside_question = False

#     def is_question_start(text):
#         if not text:
#             return False
#         text = text.strip()
#         return bool(
#             re.match(r'^प्रश्न\s+\d+', text) or
#             re.match(r'^\d+\.\s+', text)
#         )

#     def is_heading(text):
#         if not text:
#             return False

#         return bool(
#             re.search(r'अध्याय|CHAPTER', text, re.IGNORECASE) or
#             re.match(r'^[^\(]*\(\d{4}\)', text)
#         )

#     def extract_images_from_para(para):
#         images = []
#         for run in para.runs:
#             for blip in run._element.findall(
#                 './/a:blip',
#                 namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
#             ):
#                 rId = blip.get(qn('r:embed'))
#                 image_part = doc.part.related_parts[rId]
#                 img_bytes = image_part.blob

#                 width_in = height_in = 1.0

#                 extent = run._element.find(
#                     './/wp:extent',
#                     namespaces={'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
#                 )

#                 if extent is not None:
#                     width_in = int(extent.get('cx')) / 914400.0
#                     height_in = int(extent.get('cy')) / 914400.0
#                 else:
#                     try:
#                         pil_img = PILImage.open(io.BytesIO(img_bytes))
#                         width_in = pil_img.width / 96.0
#                         height_in = pil_img.height / 96.0
#                     except Exception:
#                         pass

#                 images.append((img_bytes, width_in, height_in))

#         return images

#     for para in doc.paragraphs:
#         text = para.text.strip()
#         images = extract_images_from_para(para)

#         if re.match(r'^\s*(अथवा|तथा)\s*$', text):
#             if current_block:
#                 q = process_question_block(current_block)
#                 if q:
#                     q['no'] = str(len(questions) + 1)
#                     questions.append(q)

#             current_block = []
#             inside_question = False
#             continue

#         if is_question_start(text):
#             if current_block:
#                 q = process_question_block(current_block)
#                 if q:
#                     q['no'] = str(len(questions) + 1)
#                     questions.append(q)

#             current_block = [(text, images)]
#             inside_question = True
#             continue

#         if inside_question:
#             current_block.append((text, images))

#     if current_block:
#         q = process_question_block(current_block)
#         if q:
#             q['no'] = str(len(questions) + 1)
#             questions.append(q)

#     return questions

# def remove_metadata_pattern(text):
#     pattern = r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)'
#     return re.sub(pattern, '', text).strip()

# def is_matching_question(text):
#     if not text:
#         return False

#     return bool(
#         re.search(r'सूची', text, re.IGNORECASE) or
#         re.search(r'\(\d\)', text)
#     )

# def process_question_block(block):
#     full_text = "\n".join(txt for txt, _ in block).strip()

#     q_no = None

#     for pattern in [r'प्रश्न\s+(\d+)', r'^(\d+)\.', r'^(\d+)\s+']:
#         m = re.search(pattern, full_text)
#         if m:
#             q_no = m.group(1)
#             full_text = full_text[m.end():].strip()
#             # Remove any stray leading dot left after stripping the question number
#             full_text = re.sub(r'^\.+\s*', '', full_text)
#             break

#     if not q_no:
#         return None

#     ans_match = re.search(r'(?:सही उत्तर|उत्तर)\s*:\s*\(([a-dA-D])\)', full_text)
#     if not ans_match:
#         ans_match = re.search(r'\(([a-dA-D])\)\s*$', full_text)

#     correct = f"({ans_match.group(1).lower()})" if ans_match else ""

#     explanation = ""

#     expl_match = re.search(
#         r'व्याख्या\s*:\s*(.*?)(?=\n\s*(\d+\.|प्रश्न\s+\d+)|$)',
#         full_text,
#         re.DOTALL
#     )

#     if expl_match:
#         explanation = clean_text(expl_match.group(1))

#     content = full_text

#     if ans_match:
#         content = content[:ans_match.start()]
#     if expl_match:
#         content = content[:expl_match.start()]

#     content = content.strip()

#     suchi_block = ""
#     suchi_match = re.search(r'(सूची.*?)(?=कूट|$)', content, re.DOTALL)

#     if suchi_match:
#         suchi_block = suchi_match.group(1)
#         content = content.replace(suchi_block, "")

#     koot_block = ""
#     koot_match = re.search(r'(कूट\s*:?.*)', full_text, re.DOTALL)

#     if koot_match:
#         koot_block = koot_match.group(1)

#     first_opt = re.search(r'\([a-dA-D]\)', content)

#     if first_opt:
#         question_text = content[:first_opt.start()].strip()
#         opts_raw = content[first_opt.start():]
#     else:
#         question_text = content
#         opts_raw = ""

#     question_text = clean_text(question_text)

#     options = []

#     if opts_raw:
#         opts_raw = re.split(
#             r'(?=\n\s*\d+\.)|'
#             r'(?=\n\s*प्रश्न\s+\d+)|'
#             r'कूट|व्याख्या|उत्तर',
#             opts_raw
#         )[0]

#         matches = re.findall(
#             r'\(([a-dA-D])\)\s*(.*?)(?=\([a-dA-D]\)|$)',
#             opts_raw,
#             re.DOTALL
#         )

#         for key, text in matches:
#             text = clean_text(text)

#             if re.search(r'\([a-d]\)\s*-\s*\([ivx]+\)', text, re.IGNORECASE):
#                 continue

#             if "सूची" in text:
#                 continue

#             if text:
#                 options.append({
#                     "key": f"({key.lower()})",
#                     "text": text.strip()
#                 })

#     options = options[:4]

#     if suchi_block:
#         suchi_block = format_matching_question(suchi_block)

#     final_question = question_text

#     if suchi_block:
#         final_question += "\n\n" + suchi_block

#     if koot_block:
#         final_question += "\n\n" + koot_block.strip()

#     explanation_images = []
#     answer_idx = -1

#     for idx, (txt, _) in enumerate(block):
#         if re.search(r'(उत्तर|व्याख्या)', txt):
#             answer_idx = idx
#             break

#     src = block[answer_idx+1:] if answer_idx != -1 else block

#     for _, imgs in src:
#         explanation_images.extend(imgs)

#     meta_match = re.search(
#         r'\(([^)]*\d{2,4}[^)]*(?:shift|Shift|पाली|[\[\(][^)\]]*[\]\)])[^)]*)\)',
#         full_text
#     )
#     if not meta_match:
#         meta_match = re.search(
#             r'\(([^)]*\d{4}[^)]*)\)',
#             full_text
#         )
#     metadata_str = meta_match.group(0).strip() if meta_match else ""

#     return {
#         "no": q_no,
#         "question": final_question,
#         "options": options,
#         "correct": correct,
#         "explanation": explanation,
#         "explanation_images": explanation_images,
#         "metadata": metadata_str
#     }

# # =============================================================================
# # OPTION LAYOUT
# # =============================================================================
# def layout_options(opts, max_per_line=2, char_limit=68):
#     result = []
#     i = 0
#     n = len(opts)
#     while i < n:
#         best = 1
#         for k in range(max_per_line, 1, -1):
#             if i + k <= n:
#                 combined = "    ".join(f"{opts[i+j]['key']} {opts[i+j]['text']}" for j in range(k))
#                 ok = all(len(opts[i+j]['text']) <= char_limit // 2 for j in range(k))
#                 if len(combined) <= char_limit and ok:
#                     best = k
#                     break
#         result.append([opts[i+j] for j in range(best)])
#         i += best
#     return result

# # =============================================================================
# # DOCX HELPERS
# # =============================================================================

# def set_spacing(para, line_pts, after_pts=0, before_pts=0):
#     pPr = para._p.get_or_add_pPr()

#     for old in pPr.findall(qn('w:spacing')):
#         pPr.remove(old)

#     s = OxmlElement('w:spacing')

#     s.set(qn('w:line'), str(int(line_pts * 20)))
#     s.set(qn('w:lineRule'), 'atLeast')

#     s.set(qn('w:before'), str(int(before_pts * 20)))
#     s.set(qn('w:after'), str(int(after_pts * 20)))

#     pPr.append(s)

# def set_char_spacing(run, spacing_pt):
#     if spacing_pt > 0:
#         rPr = run._r.get_or_add_rPr()
#         sp = OxmlElement('w:spacing')
#         sp.set(qn('w:val'), str(int(spacing_pt * 20)))
#         rPr.append(sp)

# def set_paragraph_background(para, color_rgb):
#     shd = OxmlElement('w:shd')
#     shd.set(qn('w:val'), 'clear')
#     shd.set(qn('w:color'), 'auto')
#     shd.set(qn('w:fill'), color_rgb)
#     pPr = para._p.get_or_add_pPr()
#     pPr.append(shd)

# def _apply_ind(para, left_twips, first_twips):
#     pPr = para._p.get_or_add_pPr()
#     for old in pPr.findall(qn('w:ind')):
#         pPr.remove(old)
#     ind = OxmlElement('w:ind')
#     ind.set(qn('w:left'), str(left_twips))
#     if first_twips != 0:
#         ind.set(qn('w:firstLine'), str(first_twips))
#     pPr.append(ind)

# def set_two_level_indent(para, l1_in, l2_in):
#     left_twips = int(l2_in * 1440)
#     first_twips = int((l1_in - l2_in) * 1440)
#     _apply_ind(para, left_twips, first_twips)

# def set_left_indent(para, left_in):
#     _apply_ind(para, int(left_in * 1440), 0)

# def no_border():
#     return {"val": "nil"}

# def set_cell_borders(cell, **kw):
#     tc = cell._tc
#     tcPr = tc.get_or_add_tcPr()
#     for old in tcPr.findall(qn('w:tcBorders')):
#         tcPr.remove(old)
#     tcB = OxmlElement('w:tcBorders')
#     for edge, attrs in kw.items():
#         tag = OxmlElement(f'w:{edge}')
#         for k, v in attrs.items():
#             tag.set(qn(f'w:{k}'), v)
#         tcB.append(tag)
#     tcPr.append(tcB)

# def remove_cell_margins(cell):
#     tc = cell._tc
#     tcPr = tc.get_or_add_tcPr()
#     for old in tcPr.findall(qn('w:tcMar')):
#         tcPr.remove(old)
#     tcMar = OxmlElement('w:tcMar')
#     for edge in ['top', 'left', 'bottom', 'right']:
#         tag = OxmlElement(f'w:{edge}')
#         tag.set(qn('w:w'), '0')
#         tag.set(qn('w:type'), 'dxa')
#         tcMar.append(tag)
#     tcPr.append(tcMar)

# def apply_font_to_run(run):
#     """Apply the selected FONT_DOCX to all font slots of a run."""
#     run.font.name = FONT_DOCX
#     rPr = run._element.get_or_add_rPr()
#     rFonts = rPr.find(qn('w:rFonts'))
#     if rFonts is None:
#         rFonts = OxmlElement('w:rFonts')
#         rPr.insert(0, rFonts)
#     rFonts.set(qn('w:ascii'), FONT_DOCX)
#     rFonts.set(qn('w:hAnsi'), FONT_DOCX)
#     rFonts.set(qn('w:eastAsia'), FONT_DOCX)
#     rFonts.set(qn('w:cs'), FONT_DOCX)

# def add_run(para, text, bold=False, size_pt=8, italic=False):
#     r = para.add_run(text)
    
#     r.bold = bold
#     r.italic = italic
#     r.font.size = Pt(size_pt)

#     apply_font_to_run(r)

#     if char_spacing > 0:
#         set_char_spacing(r, char_spacing)

#     return r

# # =============================================================================
# # ESTIMATE QUESTION HEIGHT
# # =============================================================================
# def fill_cell(container, q, include_metadata=False):

#     p_q = container.add_paragraph()

#     p_q.paragraph_format.left_indent = Inches(level2_indent)
#     p_q.paragraph_format.first_line_indent = Inches(level1_indent - level2_indent)

#     tab_stops = p_q.paragraph_format.tab_stops

#     content_width = page_width - left_margin - right_margin
#     col_gap = 0.08 if num_columns == 3 else 0.12
#     col_width = (content_width - col_gap * (num_columns - 1)) / num_columns

#     tab_stops.add_tab_stop(Inches(level2_indent), WD_TAB_ALIGNMENT.LEFT)
#     tab_stops.add_tab_stop(Inches(col_width - 0.2), WD_TAB_ALIGNMENT.LEFT)

#     is_match = "\t" in q['question']

#     add_run(p_q, f"{q['no']}. ", bold=True, size_pt=q_font)

#     if is_match:
#         lines = q['question'].split("\n")

#         for i, line in enumerate(lines):
#             if i == 0:
#                 add_run(p_q, line, bold=True, size_pt=q_font)
#             else:
#                 p_line = container.add_paragraph()
#                 p_line.paragraph_format.left_indent = Inches(level2_indent)

#                 tab_stops = p_line.paragraph_format.tab_stops
#                 tab_stops.add_tab_stop(Inches(level2_indent), WD_TAB_ALIGNMENT.LEFT)
#                 tab_stops.add_tab_stop(Inches(col_width - 0.2), WD_TAB_ALIGNMENT.LEFT)

#                 if "\t" in line:
#                     left, right = line.split("\t", 1)
#                     add_run(p_line, left, size_pt=q_font)
#                     p_line.add_run("\t")
#                     add_run(p_line, right, size_pt=q_font)
#                 else:
#                     add_run(p_line, line, size_pt=q_font)

#                 set_spacing(p_line, line_pts=line_spacing, after_pts=para_spacing)
#     else:
#         add_run(p_q, q['question'], bold=True, size_pt=q_font)

#     set_spacing(p_q, line_pts=line_spacing, after_pts=para_spacing)

#     if include_metadata and q.get('metadata'):
#         p_meta = container.add_paragraph()
#         p_meta.paragraph_format.left_indent = Inches(level2_indent)
#         p_meta.alignment = WD_ALIGN_PARAGRAPH.RIGHT
#         r_meta = p_meta.add_run(q['metadata'])
#         r_meta.italic = True
#         r_meta.font.size = Pt(max(q_font - 1.0, 5.0))
#         apply_font_to_run(r_meta)
#         set_spacing(p_meta, line_pts=line_spacing, after_pts=0)

#     option_groups = layout_options(
#         q['options'],
#         max_per_line=opts_per_line,
#         char_limit=opt_char_limit
#     )

#     right_tab_pos = col_width - 0.2

#     for idx, group in enumerate(option_groups):

#         text = ("    ".join(f"{o['key']} {o['text']}" for o in group)
#                 if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")

#         p_opt = container.add_paragraph()
#         p_opt.paragraph_format.left_indent = Inches(level2_indent)

#         add_run(p_opt, text, bold=opt_bold, size_pt=opt_font)

#         if show_correct_inline and idx == len(option_groups) - 1:
#             tab_stops = p_opt.paragraph_format.tab_stops
#             tab_stops.add_tab_stop(Inches(right_tab_pos), WD_TAB_ALIGNMENT.RIGHT)

#             p_opt.add_run("\t")
#             add_run(p_opt, q['correct'], bold=True, size_pt=opt_font + 1)

#         set_spacing(p_opt, line_pts=line_spacing, after_pts=para_spacing)

#     if q['explanation']:

#         p_expl = container.add_paragraph()

#         p_expl.paragraph_format.left_indent = Inches(level2_indent)
#         p_expl.paragraph_format.first_line_indent = Inches(level1_indent - level2_indent)

#         if expl_bg:
#             set_paragraph_background(p_expl, "E6E6E6")

#         prefix = "➤ व्याख्या: " if expl_bullet else "व्याख्या: "

#         add_run(p_expl, prefix, bold=True, size_pt=expl_font)
#         add_run(p_expl, q['explanation'], size_pt=expl_font)

#         set_spacing(p_expl, line_pts=line_spacing, after_pts=para_spacing * 2)

#     for img_bytes, width_in, height_in in q.get('explanation_images', []):
#         try:
#             with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
#                 tmp.write(img_bytes)
#                 tmp_path = tmp.name

#             max_img_w = col_width - level2_indent - 0.2
#             img_w = min(width_in if width_in > 0 else 1.5, max_img_w)

#             p_img = container.add_paragraph()
#             p_img.paragraph_format.left_indent = Inches(level2_indent)
#             p_img.add_run().add_picture(tmp_path, width=Inches(img_w))

#             os.unlink(tmp_path)

#             set_spacing(p_img, line_pts=line_spacing, after_pts=para_spacing)

#         except Exception:
#             p_ph = container.add_paragraph()
#             p_ph.paragraph_format.left_indent = Inches(level2_indent)
#             add_run(p_ph, "[चित्र यहाँ संलग्न करें]", italic=True, size_pt=expl_font)

#             if expl_bg:
#                 set_paragraph_background(p_ph, "E6E6E6")

#             set_spacing(p_ph, line_pts=line_spacing, after_pts=para_spacing)

#     if show_separator:
#         p_sep = container.add_paragraph()
#         set_spacing(p_sep, line_pts=line_spacing, after_pts=2)

    
# def estimate_q_lines(q):
#     lines = 1

#     lines += len(layout_options(q['options'],
#                                max_per_line=opts_per_line,
#                                char_limit=opt_char_limit))

#     if q['explanation']:
#         lines += 1

#     lines += len(q.get('explanation_images', [])) * 3

#     return lines

# # =============================================================================
# # PAGE GENERATION
# # =============================================================================
# from docx import Document
# from docx.shared import Inches, Pt
# from docx.enum.text import WD_ALIGN_PARAGRAPH
# from docx.oxml.ns import qn
# from docx.enum.text import WD_BREAK

# def create_page_with_questions(questions, page_num, total_pages, chapter_title):
#     new_doc = Document()

#     sec = new_doc.sections[0]
#     sec.page_width = Inches(page_width)
#     sec.page_height = Inches(page_height)
#     sec.top_margin = Inches(top_margin)
#     sec.bottom_margin = Inches(bottom_margin)
#     sec.left_margin = Inches(left_margin)
#     sec.right_margin = Inches(right_margin)

#     sectPr = sec._sectPr
#     cols = sectPr.xpath('./w:cols')[0]
#     cols.set(qn('w:num'), str(num_columns))
#     cols.set(qn('w:space'), "300")

#     header_text = header_template.format(
#         book_name=book_name,
#         chapter_title=chapter_title,
#         page=page_num
#     )

#     sec.header_distance = Inches(0.2)
#     header = sec.header
#     for p in header.paragraphs:
#         p._element.getparent().remove(p._element)

#     hp = header.add_paragraph()
#     hp.alignment = (
#         WD_ALIGN_PARAGRAPH.LEFT if header_align == "Left"
#         else WD_ALIGN_PARAGRAPH.RIGHT if header_align == "Right"
#         else WD_ALIGN_PARAGRAPH.CENTER
#     )

#     hr = hp.add_run(header_text)
#     hr.bold = header_bold
#     hr.font.size = Pt(header_font)
#     apply_font_to_run(hr)

#     if header_bg:
#         set_paragraph_background(hp, "E6E6E6")

#     set_spacing(hp, line_pts=header_font + 2, after_pts=4)

#     if page_num_pos.startswith("Top") and not (hide_on_first and page_num == 1):
#         tp = new_doc.add_paragraph()
#         tp.alignment = (
#             WD_ALIGN_PARAGRAPH.LEFT if "Left" in page_num_pos
#             else WD_ALIGN_PARAGRAPH.RIGHT if "Right" in page_num_pos
#             else WD_ALIGN_PARAGRAPH.CENTER
#         )
#         run = tp.add_run(f"पृष्ठ {page_num}")
#         run.font.size = Pt(9)
#         apply_font_to_run(run)
#         set_spacing(tp, line_pts=10, after_pts=3)

#     for q in questions:
#         fill_cell(new_doc, q, include_metadata=include_metadata)

#     if page_num_pos.startswith("Bottom") and not (hide_on_first and page_num == 1):
#         bp = new_doc.add_paragraph()
#         bp.alignment = (
#             WD_ALIGN_PARAGRAPH.LEFT if "Left" in page_num_pos
#             else WD_ALIGN_PARAGRAPH.RIGHT if "Right" in page_num_pos
#             else WD_ALIGN_PARAGRAPH.CENTER
#         )
#         run = bp.add_run(f"पृष्ठ {page_num}")
#         run.font.size = Pt(9)
#         apply_font_to_run(run)
#         set_spacing(bp, line_pts=10, before_pts=5)

#     if page_num < total_pages:
#         new_doc.add_page_break()

#     return new_doc
  
    

# def generate_multi_page_docx(questions, chapter_title):
#     doc = Document()

#     sec = doc.sections[0]
#     sec.page_width = Inches(page_width)
#     sec.page_height = Inches(page_height)
#     sec.top_margin = Inches(top_margin)
#     sec.bottom_margin = Inches(bottom_margin)
#     sec.left_margin = Inches(left_margin)
#     sec.right_margin = Inches(right_margin)

#     sectPr = sec._sectPr
#     cols = sectPr.xpath('./w:cols')[0]
#     cols.set(qn('w:num'), str(num_columns))
#     cols.set(qn('w:space'), "300")

#     header_text = header_template.format(
#         book_name=book_name,
#         chapter_title=chapter_title,
#         page=""
#     ).rstrip()

#     sec.header_distance = Inches(0.2)
#     header = sec.header
#     for p in header.paragraphs:
#         p._element.getparent().remove(p._element)

#     hp = header.add_paragraph()
#     hp.alignment = (
#         WD_ALIGN_PARAGRAPH.LEFT if header_align == "Left"
#         else WD_ALIGN_PARAGRAPH.RIGHT if header_align == "Right"
#         else WD_ALIGN_PARAGRAPH.CENTER
#     )

#     hr = hp.add_run(header_text)
#     hr.bold = header_bold
#     hr.font.size = Pt(header_font)
#     apply_font_to_run(hr)

#     if header_bg:
#         set_paragraph_background(hp, "E6E6E6")

#     set_spacing(hp, line_pts=header_font + 2, after_pts=4)

#     for q in questions:
#         fill_cell(doc, q, include_metadata=include_metadata)

#     return doc

# # =============================================================================
# # HTML PREVIEW
# # =============================================================================
# def render_q_preview(q):
#     l1px = level1_indent * 96
#     l2px = level2_indent * 96
#     hang_px = l1px - l2px

#     option_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
#     opts_html = ""
#     for idx, group in enumerate(option_groups):
#         text = ("&nbsp;&nbsp;&nbsp;&nbsp;".join(f"{o['key']} {o['text']}" for o in group)
#                 if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
#         is_last = idx == len(option_groups) - 1
#         if show_correct_inline and is_last:
#             opts_html += (
#                 f"<div style='display:flex;justify-content:space-between;"
#                 f"margin-left:{l2px}px;font-size:{opt_font}pt;'>"
#                 f"<span>{text}</span>"
#                 f"<span style='font-weight:900;font-size:{opt_font+1.5}pt;'>{q['correct']}</span>"
#                 f"</div>"
#             )
#         else:
#             opts_html += f"<div style='margin-left:{l2px}px;font-size:{opt_font}pt;'>{text}</div>"

#     expl_html = ""
#     if q['explanation'] or q.get('explanation_images'):
#         heading_prefix = "➤ व्याख्या: " if expl_bullet else "व्याख्या : "
#         bg_style = "background-color:#F0F0F0;padding:2px 4px;border-radius:3px;" if expl_bg else ""
#         expl_html += (
#             f"<div style='margin-left:{l2px}px;text-indent:{hang_px}px;{bg_style}font-size:{expl_font}pt;'>"
#             f"<span style='font-weight:bold;'>{heading_prefix}</span>"
#         )
#         if q['explanation']:
#             expl_html += q['explanation'].replace('|', '<br>')
#         expl_html += "</div>"

#         for img_bytes, _, __ in q.get('explanation_images', []):
#             b64 = base64.b64encode(img_bytes).decode()
#             expl_html += (
#                 f'<div style="margin-left:{l2px}px;">'
#                 f'<img src="data:image/png;base64,{b64}" style="max-width:100%;height:auto;"></div>'
#             )

#     question_html = q['question'].replace('\n', '<br>')

#     q_html = (
#         f"<div style='margin-left:{l2px}px;text-indent:{hang_px}px;"
#         f"font-size:{q_font}pt;font-weight:bold;margin-bottom:2px;"
#         f"white-space:pre-wrap;'>"
#         f"{q['no']}. {question_html}</div>"
#     )
#     meta_html = ""
#     if include_metadata and q.get('metadata'):
#         meta_html = (
#             f"<div style='text-align:right;font-size:{max(q_font-1,5)}pt;"
#             f"font-style:italic;margin-left:{l2px}px;color:#555;'>"
#             f"{q['metadata']}</div>"
#         )

#     return f"""
# <div class="qblock">
#   {q_html}
#   {meta_html}
#   {opts_html}
#   {expl_html}
#   {('<hr>' if show_separator else '')}
# </div>"""

# def build_preview_with_pagination(questions, q_per_page, chapter_title):
#     total_pages = (len(questions) + q_per_page - 1) // q_per_page
#     pages_html = []
#     for page_num in range(1, total_pages + 1):
#         start = (page_num - 1) * q_per_page
#         end = min(start + q_per_page, len(questions))
#         content_html = "".join(render_q_preview(q) for q in questions[start:end])
#         pages_html.append(f"""
# <div class="page" style="width:{page_width*96}px;min-height:{page_height*96}px;background:white;
#   margin:0 auto 20px auto;padding:{top_margin*96}px {right_margin*96}px {bottom_margin*96}px {left_margin*96}px;
#   box-shadow:0 4px 24px rgba(0,0,0,0.5);">
#   <div style="background:#E6E6E6;padding:4px;border-radius:3px;text-align:center;
#     font-weight:bold;margin-bottom:10px;">
#     {header_template.format(book_name=book_name, chapter_title=chapter_title, page=page_num)}
#   </div>
#   <div style="column-count:{num_columns};column-gap:18px;">{content_html}</div>
# </div>""")

#     return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
# <style>
#   *{{box-sizing:border-box;margin:0;padding:0;}}
#   body{{background:#666;font-family:'Mangal','Arial','Noto Sans Devanagari','Arial',sans-serif;padding:20px;}}
#   .qblock{{margin-bottom:5px;padding-bottom:4px;break-inside:avoid;page-break-inside:avoid;}}
#   hr{{margin:4px 0;border:0;border-top:1px dotted #ccc;}}
# </style>
# </head><body>{''.join(pages_html)}</body></html>"""

# # =============================================================================
# # PDF GENERATION
# # =============================================================================
# def register_devanagari_font():
#     for path in [
#         "C:/Windows/Fonts/Mangal.ttf",
#         "C:/Windows/Fonts/Nirmala.ttf",
#         "/usr/share/fonts/truetype/msttcorefonts/Mangal.ttf",
#         "/usr/share/fonts/truetype/lohit/Lohit-Devanagari.ttf",
#         "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
#     ]:
#         if os.path.exists(path):
#             try:
#                 pdfmetrics.registerFont(TTFont('Devanagari', path))
#                 return 'Devanagari'
#             except Exception:
#                 continue
#     st.warning("⚠️ No Devanagari font found. PDF will use Helvetica.")
#     return 'Helvetica'


# def generate_pdf(questions, chapter_title):
#     font = register_devanagari_font()
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(buffer,
#                             pagesize=(page_width*inch, page_height*inch),
#                             topMargin=top_margin*inch, bottomMargin=bottom_margin*inch,
#                             leftMargin=left_margin*inch, rightMargin=right_margin*inch)
#     styles = getSampleStyleSheet()
#     l1 = level1_indent * inch
#     l2 = level2_indent * inch

#     sQ  = ParagraphStyle('Q',  parent=styles['Normal'], fontSize=q_font,    leading=line_spacing,
#                           fontName=font, spaceAfter=para_spacing, leftIndent=l2, firstLineIndent=l1-l2)
#     sMeta = ParagraphStyle('M', parent=styles['Normal'], fontSize=6,          leading=line_spacing,
#                           fontName=font, alignment=TA_RIGHT, spaceAfter=para_spacing, leftIndent=l2)
#     sOpt  = ParagraphStyle('O', parent=styles['Normal'], fontSize=opt_font,  leading=line_spacing,
#                           fontName=font, spaceAfter=para_spacing, leftIndent=l2)
#     sAns  = ParagraphStyle('A', parent=styles['Normal'], fontSize=opt_font+1.5, leading=line_spacing,
#                           fontName=font, alignment=TA_RIGHT, spaceAfter=para_spacing, leftIndent=l2)
#     sExpl = ParagraphStyle('E', parent=styles['Normal'], fontSize=expl_font, leading=line_spacing,
#                           fontName=font, spaceAfter=para_spacing*2, leftIndent=l2, firstLineIndent=l1-l2,
#                           backColor=colors.HexColor('#F0F0F0') if expl_bg else None)
#     sH    = ParagraphStyle('H', parent=styles['Normal'], fontSize=header_font, leading=header_font+2,
#                           fontName=font, alignment=TA_CENTER,
#                           backColor=colors.HexColor('#E6E6E6') if header_bg else None, spaceAfter=6)

#     story = [Paragraph(header_template.format(book_name=book_name, chapter_title=chapter_title, page=1), sH)]

#     for q in questions:
#         story.append(Paragraph(f"<b>{q['no']}.</b> {q['question']}", sQ))
#         if include_metadata and q.get('metadata'):
#             story.append(Paragraph(q['metadata'], sMeta))

#         opt_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
#         for idx, group in enumerate(opt_groups):
#             text = ("    ".join(f"{o['key']} {o['text']}" for o in group)
#                     if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
#             is_last = idx == len(opt_groups) - 1
#             story.append(Paragraph(text, sOpt))
#             if show_correct_inline and is_last:
#                 story.append(Paragraph(f"<b>{q['correct']}</b>", sAns))

#         if q['explanation'] or q.get('explanation_images'):
#             heading = ("• व्याख्या : " if expl_bullet else "व्याख्या : ")
#             expl_text = heading + (q['explanation'] if q['explanation'] else "")
#             story.append(Paragraph(expl_text.replace('|', '<br/>'), sExpl))

#             for img_bytes, width_in, height_in in q.get('explanation_images', []):
#                 try:
#                     with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
#                         tmp.write(img_bytes)
#                         tmp_path = tmp.name
#                     content_w = page_width - left_margin - right_margin
#                     col_gap = 0.08 if num_columns == 3 else 0.12
#                     col_w = (content_w - col_gap * (num_columns - 1)) / num_columns
#                     max_w = col_w - level2_indent - 0.05
#                     img_w = min(width_in if width_in > 0 else 1.5, max_w)
#                     story.append(Image(tmp_path, width=img_w*inch, height=height_in*inch))
#                     os.unlink(tmp_path)
#                 except Exception:
#                     story.append(Paragraph("[चित्र यहाँ संलग्न करें]", sExpl))

#         if show_separator:
#             story.append(Spacer(1, 2))

#     doc.build(story)
#     buffer.seek(0)
#     return buffer

# # =============================================================================
# # CHAPTER TITLE EXTRACTION
# # =============================================================================
# def extract_chapter_title(doc):
#     for para in doc.paragraphs[:10]:
#         if "अध्याय" in para.text or "CHAPTER" in para.text.upper():
#             title = para.text.strip()
#             return title[:80] + "..." if len(title) > 80 else title
#     return "RBD PUBLICATION — अध्याय"

# # =============================================================================
# # MAIN APP
# # =============================================================================
# if uploaded_file:
#     doc = Document(uploaded_file)
#     with st.spinner("Parsing questions..."):
#         questions = parse_questions(doc)
#         chapter_title = extract_chapter_title(doc)
#     st.success(f"✅ {len(questions)} questions parsed!")

#     if auto_fill:
#         sample_size = min(10, len(questions))
#         total_lines = sum(estimate_q_lines(q) for q in questions[:sample_size])
#         avg_lines = total_lines / sample_size if sample_size > 0 else 10
#         usable_height = page_height - top_margin - bottom_margin - 1.2
#         lines_per_page = usable_height / (line_spacing / 72.0)
#         q_per_page_est = max(1, int(lines_per_page / avg_lines))
#         total_pages_est = (len(questions) + q_per_page_est - 1) // q_per_page_est
#     else:
#         q_per_page_est = 20
#         total_pages_est = (len(questions) + q_per_page_est - 1) // q_per_page_est

#     st.info(f"📄 Estimated pages: {total_pages_est} ({'auto' if auto_fill else 'fixed'})")

#     tab1, tab2 = st.tabs(["📄 Page Preview", "🔍 Parsed Data"])
#     with tab1:
#         preview_html = build_preview_with_pagination(questions, q_per_page_est, chapter_title)
#         st.components.v1.html(preview_html, height=1200, scrolling=True)
#     with tab2:
#         for q in questions[:5]:
#             with st.expander(f"Q{q['no']} – {q['question'][:60]}…"):
#                 st.write("**Options:**", q['options'])
#                 st.write("**Correct Answer:**", q['correct'])
#                 st.write("**Explanation:**", q['explanation'][:500])
#                 st.write(f"**Explanation images:** {len(q.get('explanation_images', []))}")

#     st.markdown("---")
#     c1, c2 = st.columns(2)
#     with c1:
#         if st.button("🚀 Generate DOCX"):
#             with st.spinner(f"Generating DOCX with font: {FONT_DOCX}..."):
#                 final_doc = generate_multi_page_docx(questions, chapter_title)
#                 # ✅ Save to BytesIO - NO file saved to disk
#                 docx_buffer = BytesIO()
#                 final_doc.save(docx_buffer)
#                 docx_buffer.seek(0)
#                 filename = f"Formatted_Output_{len(questions)}Q.docx"
#                 st.download_button(
#                     "📥 Download DOCX",
#                     docx_buffer,
#                     filename,
#                     "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
#                 )
#                 st.success(f"🎉 DOCX ready! Font used: **{FONT_DOCX}**")
#     with c2:
#         if st.button("📑 Preview PDF"):
#             with st.spinner("Generating PDF preview..."):
#                 pdf_buffer = generate_pdf(questions, chapter_title)
#                 pdf_b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
#                 st.markdown(
#                     f'<iframe src="data:application/pdf;base64,{pdf_b64}" '
#                     f'width="100%" height="800" type="application/pdf"></iframe>',
#                     unsafe_allow_html=True)
#                 st.download_button("📥 Download PDF", pdf_buffer,
#                                    file_name="Formatted_Output.pdf", mime="application/pdf")
#                 st.success("🎉 PDF preview ready!")


#  chandni ma'am permission issue 
# # correct 2 
# import streamlit as st
# from docx import Document
# from docx.shared import Pt, Inches
# from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
# from docx.oxml.ns import qn
# from docx.oxml import OxmlElement
# from io import BytesIO
# import re
# import tempfile
# import os
# import base64
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import inch
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
# from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from PIL import Image as PILImage
# # ================= AUTH SYSTEM =================
# import sqlite3
# import datetime
# import random
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from dotenv import load_dotenv
# import os

# load_dotenv()

# GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
# GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
# ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
# # st.write("EMAIL:", GMAIL_EMAIL)
# # st.write("PASS:", GMAIL_APP_PASSWORD)

# DB_PATH = "rbd_users.db"

# def init_db():
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()

#     c.execute('''CREATE TABLE IF NOT EXISTS users (
#         email TEXT PRIMARY KEY,
#         created_at TEXT,
#         is_admin BOOLEAN DEFAULT 0,
#         can_format BOOLEAN DEFAULT 0
#     )''')

#     c.execute('''CREATE TABLE IF NOT EXISTS otp_codes (
#         email TEXT,
#         code TEXT,
#         expires_at TEXT
#     )''')

#     conn.commit()
#     conn.close()

# def add_user(email, is_admin=False):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     try:
#         now = datetime.datetime.now().isoformat()
#         c.execute(
#             "INSERT INTO users (email, created_at, is_admin, can_format) VALUES (?, ?, ?, ?)",
#             (email, now, is_admin, is_admin)
#         )
#         conn.commit()
#     except:
#         pass
#     conn.close()

# def get_user(email):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT email, is_admin, can_format FROM users WHERE email=?", (email,))
#     row = c.fetchone()
#     conn.close()

#     if row:
#         return {"email": row[0], "is_admin": bool(row[1]), "can_format": bool(row[2])}
#     return None

# def generate_otp():
#     return str(random.randint(100000, 999999))

# def send_otp_email(email, code):
#     try:
#         server = smtplib.SMTP("smtp.gmail.com", 587)
#         server.starttls()

#         server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)

#         msg = f"Subject: OTP\n\nYour OTP is {code}"

#         server.sendmail(GMAIL_EMAIL, email, msg)
#         server.quit()

#         return True

#     except Exception as e:
#         st.error(f"SMTP ERROR: {e}")   # 👈 VERY IMPORTANT
#         return False

# def store_otp(email, code):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("DELETE FROM otp_codes WHERE email=?", (email,))
#     expiry = (datetime.datetime.now() + datetime.timedelta(minutes=10)).isoformat()
#     c.execute("INSERT INTO otp_codes VALUES (?, ?, ?)", (email, code, expiry))
#     conn.commit()
#     conn.close()

# def verify_otp(email, code):
#     conn = sqlite3.connect(DB_PATH)
#     c = conn.cursor()
#     c.execute("SELECT code, expires_at FROM otp_codes WHERE email=?", (email,))
#     row = c.fetchone()
#     conn.close()

#     if row and row[0] == code:
#         if datetime.datetime.now() < datetime.datetime.fromisoformat(row[1]):
#             return True
#     return False

# def login_page():
#     st.title("🔐 Login")

#     email = st.text_input("Email")

#     if st.button("Send OTP"):
#         if email:
#             user = get_user(email)
#             if not user:
#                 add_user(email, email == "admin@example.com")

#             otp = generate_otp()

#             # 🔥 SEND EMAIL
#             sent = send_otp_email(email, otp)

#             if sent:
#                 store_otp(email, otp)
#                 st.session_state["otp_email"] = email
#                 st.success("OTP sent to your email ✅")
#             else:
#                 st.error("❌ Failed to send OTP email")

#             # st.success(f"OTP sent: {otp}")  # remove in production

#     if "otp_email" in st.session_state:
#         code = st.text_input("Enter OTP", type="password")

#         if st.button("Verify"):
#             if verify_otp(st.session_state["otp_email"], code):
#                 user = get_user(st.session_state["otp_email"])

#                 st.session_state["authenticated"] = True
#                 st.session_state["user_email"] = user["email"]
#                 st.session_state["is_admin"] = user["is_admin"]
#                 st.session_state["can_format"] = user["can_format"]

#                 st.success("Logged in!")
#                 st.rerun()
#             else:
#                 st.error("Invalid OTP")

#     if not st.session_state.get("authenticated"):
#         st.stop()
   
# def clean_text(text):
#     if not text:
#         return ""
    
#     # Remove exam metadata patterns
#     text = re.sub(r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)', '', text)
    
#     # Remove question numbers from inside text
#     text = re.sub(r'प्रश्न\s+\d+\s*', '', text)
#     text = re.sub(r'^\d+\.\s*', '', text)
    
#     # Replace tabs and multiple spaces
#     text = text.replace('\t', ' ')
#     text = re.sub(r'\s+', ' ', text)
    
#     # Remove leading/trailing spaces
#     text = text.strip()
#     return text
    
# def format_matching_question(text):
#     if not text:
#         return text

#     text = text.replace('\n', ' ')
#     text = re.sub(r'\s+', ' ', text).strip()

#     # =========================================================
#     # 🔥 EXTRACT SUCHI-I (A–D)
#     # =========================================================
#     suchi1 = re.findall(
#         r'\(([A-D])\)\s*(.*?)(?=\([A-D]\)|सूची-II|$)',
#         text,
#         re.DOTALL
#     )

#     # =========================================================
#     # 🔥 EXTRACT SUCHI-II (I–IV)
#     # =========================================================
#     suchi2 = re.findall(
#         r'\(([IVX]+)\)\s*(.*?)(?=\([IVX]+\)|$)',
#         text,
#         re.DOTALL
#     )

#     # Clean
#     suchi1 = [(k, clean_text(v)) for k, v in suchi1]
#     suchi2 = [(k, clean_text(v)) for k, v in suchi2]

#     # =========================================================
#     # 🔥 HEADER
#     # =========================================================
#     header = re.split(r'\([A-D]\)', text, maxsplit=1)[0].strip()

#     lines = []
#     if header:
#         lines.append(header)
#         lines.append("")

#     # =========================================================
#     # 🔥 PARALLEL ALIGNMENT
#     # =========================================================
#     max_len = max(len(suchi1), len(suchi2))

#     for i in range(max_len):
#         left = ""
#         right = ""

#         if i < len(suchi1):
#             left = f"({suchi1[i][0]}) {suchi1[i][1]}"

#         if i < len(suchi2):
#             right = f"({suchi2[i][0]}) {suchi2[i][1]}"

#         if left and right:
#             lines.append(f"{left}\t{right}")   # 🔥 TAB = COLUMN
#         elif left:
#             lines.append(left)
#         elif right:
#             lines.append(right)

#     return "\n".join(lines)
 

    
# st.set_page_config(page_title="RBD Formatter", layout="wide")
# st.title("📚 RBD Publication – Smart Formatter")
# init_db()

# if not st.session_state.get("authenticated"):
#     login_page()

# # 👑 ADMIN PANEL
# if st.session_state.get("is_admin"):
#     st.sidebar.title("👑 Admin Panel")

#     conn = sqlite3.connect(DB_PATH)
#     users = conn.execute("SELECT email, can_format FROM users").fetchall()
#     conn.close()

#     for email, can_format in users:
#         val = st.sidebar.checkbox(email, value=bool(can_format))
        
#         if val != bool(can_format):
#             conn = sqlite3.connect(DB_PATH)
#             conn.execute("UPDATE users SET can_format=? WHERE email=?", (val, email))
#             conn.commit()
#             conn.close()
#             st.rerun()

# # 🔐 AUTH CHECK
# if st.session_state.get("authenticated"):

#     if not st.session_state.get("can_format"):
#         st.error("❌ You are not allowed to use formatter")
#         st.stop()

#     # =========================
#     # YOUR ORIGINAL APP STARTS
#     # =========================

#     uploaded_file = st.file_uploader("📄 Upload Chapter DOCX", type=["docx"])

# # =============================================================================
# # SIDEBAR
# # =============================================================================
# with st.sidebar:
#     st.header("📄 Page Design")
#     page_width = st.number_input("Page Width (inches)", 5.0, 12.0, 7.0, 0.1)
#     page_height = st.number_input("Page Height (inches)", 6.0, 14.0, 9.0, 0.1)
#     top_margin = st.number_input("Top Margin (inches)", 0.2, 1.0, 0.4, 0.05)
#     bottom_margin = st.number_input("Bottom Margin (inches)", 0.2, 1.0, 0.4, 0.05)
#     left_margin = st.number_input("Left Margin (inches)", 0.2, 1.0, 0.4, 0.05)
#     right_margin = st.number_input("Right Margin (inches)", 0.2, 1.0, 0.4, 0.05)

#     st.header("📐 Layout")
#     num_columns = st.selectbox("Number of Columns", [2, 3], index=0)
#     auto_fill = st.checkbox("Auto‑fill pages", True)

#     st.header("✍️ Text Styling")
#     q_font = st.slider("Question font size (pt)", 5.0, 12.0, 5.5, 0.5)

#     st.markdown("**Indent levels**")
#     st.caption("Level-1: question number '1.' and bullet '•' sit here")
#     level1_indent = st.number_input("Level-1 indent (inches)", 0.0, 0.5, 0.0, 0.05)
#     st.caption("Level-2: all content text starts here (question text, options, explanation)")
#     level2_indent = st.number_input("Level-2 indent (inches)", 0.05, 1.0, 0.15, 0.05)

#     # alias used elsewhere
#     q_indent = level2_indent

#     opt_font = st.slider("Options font size (pt)", 5.0, 11.0, 5.5, 0.5)
#     opt_bold = st.checkbox("Bold options", False)
#     ans_font = st.slider("Answer font size (pt)", 5.0, 11.0, 5.5, 0.5)
#     ans_bold = st.checkbox("Bold answer", False)
#     expl_font = st.slider("Explanation font size (pt)", 5.0, 10.0, 5.5, 0.5)

#     st.header("📏 Spacing")
#     line_spacing = st.slider("Line spacing (pt)", 8.0, 15.0, 9.5, 0.5)
#     para_spacing = st.slider("Space after paragraph (pt)", 0.0, 6.0, 0.0, 0.5)
#     char_spacing = st.slider("Character spacing (pt)", 0.0, 3.0, 0.0, 0.5)

#     st.header("🎨 Option Wrapping")
#     opts_per_line = st.selectbox("Max options per line", [2, 3, 4], index=0)
#     if opts_per_line == 4:
#         default_char_limit = 80
#     elif opts_per_line == 3:
#         default_char_limit = 68
#     else:
#         default_char_limit = 68
#     opt_char_limit = st.slider("Option line length threshold", 40, 120, default_char_limit)

#     st.header("📝 Header & Footer")
#     header_template = st.text_input("Header template", "{book_name} | {chapter_title} | पृष्ठ {page}")
#     book_name = st.text_input("Book name", "RBD PUBLICATION")
#     header_font = st.slider("Header font size (pt)", 8.0, 16.0, 11.0, 0.5)
#     header_bold = st.checkbox("Header bold", True)
#     header_bg = st.checkbox("Header grey background", True)
#     header_align = st.selectbox("Header alignment", ["Left", "Center", "Right"], index=1)

#     st.header("🔢 Page Numbers")
#     page_num_pos = st.selectbox("Position", ["None", "Top Left", "Top Center", "Top Right",
#                                               "Bottom Left", "Bottom Center", "Bottom Right"], index=5)
#     hide_on_first = st.checkbox("Hide on first page", False) if page_num_pos != "None" else False

#     st.header("✨ Extras")
#     show_correct_inline = st.checkbox("Show correct answer on last option line (right‑aligned)", True)
#     show_separator = st.checkbox("Show line after each question", False)
#     expl_bullet = st.checkbox("Bullet before व्याख्या heading", True)
#     expl_bg = st.checkbox("Light grey background for explanation", True)

#     st.header("📋 Metadata")
#     include_metadata = st.checkbox("Include PYQ metadata in output", False,
#         help="If checked, exam date/shift/year info found in the source file will be shown with each question.")

#     if st.checkbox("Extra compact mode", False):
#         line_spacing = 5.0
#         para_spacing = 0.0
#         q_font = 5.0
#         opt_font = 5.0
#         ans_font = 5.0
#         expl_font = 5.0

# # =============================================================================
# # PARSING (unchanged)
# # =============================================================================
# def parse_questions(doc):
#     import io

#     questions = []
#     current_block = []
#     inside_question = False

#     # -----------------------------
#     # ✅ FIXED QUESTION DETECTION
#     # -----------------------------
#     def is_question_start(text):
#         if not text:
#             return False
#         text = text.strip()
#         return bool(
#             re.match(r'^प्रश्न\s+\d+', text) or
#             re.match(r'^\d+\.\s+', text)
#         )

#     # -----------------------------
#     # ✅ HEADING DETECTION (NEW)
#     # -----------------------------
#     def is_heading(text):
#         if not text:
#             return False

#         return bool(
#             re.search(r'अध्याय|CHAPTER', text, re.IGNORECASE) or
#             re.match(r'^[^\(]*\(\d{4}\)', text)  # lines ending with year like (2010)
#         )

#     # -----------------------------
#     # IMAGE EXTRACTION (UNCHANGED)
#     # -----------------------------
#     def extract_images_from_para(para):
#         images = []
#         for run in para.runs:
#             for blip in run._element.findall(
#                 './/a:blip',
#                 namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
#             ):
#                 rId = blip.get(qn('r:embed'))
#                 image_part = doc.part.related_parts[rId]
#                 img_bytes = image_part.blob

#                 width_in = height_in = 1.0

#                 extent = run._element.find(
#                     './/wp:extent',
#                     namespaces={'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
#                 )

#                 if extent is not None:
#                     width_in = int(extent.get('cx')) / 914400.0
#                     height_in = int(extent.get('cy')) / 914400.0
#                 else:
#                     try:
#                         pil_img = PILImage.open(io.BytesIO(img_bytes))
#                         width_in = pil_img.width / 96.0
#                         height_in = pil_img.height / 96.0
#                     except Exception:
#                         pass

#                 images.append((img_bytes, width_in, height_in))

#         return images

#     # -----------------------------
#     # MAIN LOOP
#     # -----------------------------
#     for para in doc.paragraphs:
#         text = para.text.strip()
#         images = extract_images_from_para(para)

#         # 🚀 HANDLE 'अथवा' AS NEW QUESTION BREAK
#         if re.match(r'^\s*(अथवा|तथा)\s*$', text):
#             if current_block:
#                 q = process_question_block(current_block)
#                 if q:
#                     q['no'] = str(len(questions) + 1)
#                     questions.append(q)

#             current_block = []
#             inside_question = False
#             continue


#         # 🚀 NORMAL QUESTION START
#         if is_question_start(text):
#             if current_block:
#                 q = process_question_block(current_block)
#                 if q:
#                     q['no'] = str(len(questions) + 1)
#                     questions.append(q)

#             current_block = [(text, images)]
#             inside_question = True
#             continue

#         # 🚀 CONTINUE CURRENT QUESTION
#         if inside_question:
#             current_block.append((text, images))

#     # -----------------------------
#     # LAST BLOCK
#     # -----------------------------
#     if current_block:
#         q = process_question_block(current_block)
#         if q:
#             q['no'] = str(len(questions) + 1)
#             questions.append(q)

#     return questions

# def remove_metadata_pattern(text):
#     # Strong pattern to remove exam metadata
#     pattern = r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)'
#     return re.sub(pattern, '', text).strip()

# def is_matching_question(text):
#     if not text:
#         return False

#     return bool(
#         re.search(r'सूची', text, re.IGNORECASE) or
#         re.search(r'\(\d\)', text)
#     )

#     # Detect both sides (A-D and 1-4)
#     has_alpha = re.search(r'[A-D][\.\)]', text)
#     has_numeric = re.search(r'[1-4][\.\)]', text)

#     return bool(has_alpha and has_numeric)
# # ==================
# def process_question_block(block):
#     full_text = "\n".join(txt for txt, _ in block).strip()

#     # =========================================================
#     # 1. QUESTION NUMBER
#     # =========================================================
#     q_no = None

#     for pattern in [r'प्रश्न\s+(\d+)', r'^(\d+)\.', r'^(\d+)\s+']:
#         m = re.search(pattern, full_text)
#         if m:
#             q_no = m.group(1)
#             full_text = full_text[m.end():].strip()
#             break

#     if not q_no:
#         return None

#     # =========================================================
#     # 2. ANSWER
#     # =========================================================
#     ans_match = re.search(r'(?:सही उत्तर|उत्तर)\s*:\s*\(([a-dA-D])\)', full_text)
#     if not ans_match:
#         ans_match = re.search(r'\(([a-dA-D])\)\s*$', full_text)

#     correct = f"({ans_match.group(1).lower()})" if ans_match else ""

#     # =========================================================
#     # 3. EXPLANATION
#     # =========================================================
#     explanation = ""

#     expl_match = re.search(
#         r'व्याख्या\s*:\s*(.*?)(?=\n\s*(\d+\.|प्रश्न\s+\d+)|$)',
#         full_text,
#         re.DOTALL
#     )

#     if expl_match:
#         explanation = clean_text(expl_match.group(1))

#     # =========================================================
#     # 4. REMOVE ANSWER + EXPLANATION
#     # =========================================================
#     content = full_text

#     if ans_match:
#         content = content[:ans_match.start()]
#     if expl_match:
#         content = content[:expl_match.start()]

#     content = content.strip()

#     # =========================================================
#     # 5. EXTRACT SUCHI BLOCK (IMPORTANT FIX)
#     # =========================================================
#     suchi_block = ""
#     suchi_match = re.search(r'(सूची.*?)(?=कूट|$)', content, re.DOTALL)

#     if suchi_match:
#         suchi_block = suchi_match.group(1)
#         content = content.replace(suchi_block, "")

#     # =========================================================
#     # 6. EXTRACT KOOT BLOCK
#     # =========================================================
#     koot_block = ""
#     koot_match = re.search(r'(कूट\s*:?.*)', full_text, re.DOTALL)

#     if koot_match:
#         koot_block = koot_match.group(1)

#     # =========================================================
#     # 7. SPLIT QUESTION + OPTIONS
#     # =========================================================
#     first_opt = re.search(r'\([a-dA-D]\)', content)

#     if first_opt:
#         question_text = content[:first_opt.start()].strip()
#         opts_raw = content[first_opt.start():]
#     else:
#         question_text = content
#         opts_raw = ""

#     question_text = clean_text(question_text)

#     # =========================================================
#     # 8. CLEAN OPTIONS (ONLY TRUE MCQ OPTIONS)
#     # =========================================================
#     options = []

#     if opts_raw:
#         opts_raw = re.split(
#             r'(?=\n\s*\d+\.)|'
#             r'(?=\n\s*प्रश्न\s+\d+)|'
#             r'कूट|व्याख्या|उत्तर',
#             opts_raw
#         )[0]

#         matches = re.findall(
#             r'\(([a-dA-D])\)\s*(.*?)(?=\([a-dA-D]\)|$)',
#             opts_raw,
#             re.DOTALL
#         )

#         for key, text in matches:
#             text = clean_text(text)

#             # ❌ remove mapping (a)-(II)
#             if re.search(r'\([a-d]\)\s*-\s*\([ivx]+\)', text, re.IGNORECASE):
#                 continue

#             # ❌ remove suchi contamination
#             if "सूची" in text:
#                 continue

#             if text:
#                 options.append({
#                     "key": f"({key.lower()})",
#                     "text": text.strip()
#                 })

#     options = options[:4]

#     # =========================================================
#     # 9. FORMAT SUCHI (PARALLEL)
#     # =========================================================
#     if suchi_block:
#         suchi_block = format_matching_question(suchi_block)

#     # =========================================================
#     # 10. FINAL QUESTION BUILD
#     # =========================================================
#     final_question = question_text

#     if suchi_block:
#         final_question += "\n\n" + suchi_block

#     if koot_block:
#         final_question += "\n\n" + koot_block.strip()

#     # =========================================================
#     # 11. IMAGES
#     # =========================================================
#     explanation_images = []
#     answer_idx = -1

#     for idx, (txt, _) in enumerate(block):
#         if re.search(r'(उत्तर|व्याख्या)', txt):
#             answer_idx = idx
#             break

#     src = block[answer_idx+1:] if answer_idx != -1 else block

#     for _, imgs in src:
#         explanation_images.extend(imgs)

#     # =========================================================
#     # 12. EXTRACT METADATA (PYQ exam date/shift/year)
#     # =========================================================
#     meta_match = re.search(
#         r'\(([^)]*\d{2,4}[^)]*(?:shift|Shift|पाली|[\[\(][^)\]]*[\]\)])[^)]*)\)',
#         full_text
#     )
#     if not meta_match:
#         # Broader: anything like (2019, Shift-I) or (Jun 2022 [S-1] (P-1))
#         meta_match = re.search(
#             r'\(([^)]*\d{4}[^)]*)\)',
#             full_text
#         )
#     metadata_str = meta_match.group(0).strip() if meta_match else ""

#     # =========================================================
#     # FINAL RETURN
#     # =========================================================
#     return {
#         "no": q_no,
#         "question": final_question,
#         "options": options,
#         "correct": correct,
#         "explanation": explanation,
#         "explanation_images": explanation_images,
#         "metadata": metadata_str
#     }

# # =============================================================================
# # OPTION LAYOUT (unchanged)
# # =============================================================================
# def layout_options(opts, max_per_line=2, char_limit=68):
#     result = []
#     i = 0
#     n = len(opts)
#     while i < n:
#         best = 1
#         for k in range(max_per_line, 1, -1):
#             if i + k <= n:
#                 combined = "    ".join(f"{opts[i+j]['key']} {opts[i+j]['text']}" for j in range(k))
#                 ok = all(len(opts[i+j]['text']) <= char_limit // 2 for j in range(k))
#                 if len(combined) <= char_limit and ok:
#                     best = k
#                     break
#         result.append([opts[i+j] for j in range(best)])
#         i += best
#     return result

# # =============================================================================
# # DOCX HELPERS
# # =============================================================================
# FONT_DOCX = "Arial"

# def set_spacing(para, line_pts, after_pts=0, before_pts=0):
#     pPr = para._p.get_or_add_pPr()

#     for old in pPr.findall(qn('w:spacing')):
#         pPr.remove(old)

#     s = OxmlElement('w:spacing')

#     # 🔥 IMPORTANT CHANGE
#     s.set(qn('w:line'), str(int(line_pts * 20)))
#     s.set(qn('w:lineRule'), 'atLeast')   # ✅ FIX

#     s.set(qn('w:before'), str(int(before_pts * 20)))
#     s.set(qn('w:after'), str(int(after_pts * 20)))

#     pPr.append(s)

# def set_char_spacing(run, spacing_pt):
#     if spacing_pt > 0:
#         rPr = run._r.get_or_add_rPr()
#         sp = OxmlElement('w:spacing')
#         sp.set(qn('w:val'), str(int(spacing_pt * 20)))
#         rPr.append(sp)

# def set_paragraph_background(para, color_rgb):
#     shd = OxmlElement('w:shd')
#     shd.set(qn('w:val'), 'clear')
#     shd.set(qn('w:color'), 'auto')
#     shd.set(qn('w:fill'), color_rgb)
#     pPr = para._p.get_or_add_pPr()
#     pPr.append(shd)

# def _apply_ind(para, left_twips, first_twips):
#     pPr = para._p.get_or_add_pPr()
#     for old in pPr.findall(qn('w:ind')):
#         pPr.remove(old)
#     ind = OxmlElement('w:ind')
#     ind.set(qn('w:left'), str(left_twips))
#     if first_twips != 0:
#         ind.set(qn('w:firstLine'), str(first_twips))
#     pPr.append(ind)

# def set_two_level_indent(para, l1_in, l2_in):
#     left_twips = int(l2_in * 1440)
#     first_twips = int((l1_in - l2_in) * 1440)
#     _apply_ind(para, left_twips, first_twips)

# def set_left_indent(para, left_in):
#     _apply_ind(para, int(left_in * 1440), 0)

# def no_border():
#     return {"val": "nil"}

# def set_cell_borders(cell, **kw):
#     tc = cell._tc
#     tcPr = tc.get_or_add_tcPr()
#     for old in tcPr.findall(qn('w:tcBorders')):
#         tcPr.remove(old)
#     tcB = OxmlElement('w:tcBorders')
#     for edge, attrs in kw.items():
#         tag = OxmlElement(f'w:{edge}')
#         for k, v in attrs.items():
#             tag.set(qn(f'w:{k}'), v)
#         tcB.append(tag)
#     tcPr.append(tcB)

# def remove_cell_margins(cell):
#     tc = cell._tc
#     tcPr = tc.get_or_add_tcPr()
#     for old in tcPr.findall(qn('w:tcMar')):
#         tcPr.remove(old)
#     tcMar = OxmlElement('w:tcMar')
#     for edge in ['top', 'left', 'bottom', 'right']:
#         tag = OxmlElement(f'w:{edge}')
#         tag.set(qn('w:w'), '0')
#         tag.set(qn('w:type'), 'dxa')
#         tcMar.append(tag)
#     tcPr.append(tcMar)

# from docx.oxml.ns import qn

# def add_run(para, text, bold=False, size_pt=8, italic=False):
#     r = para.add_run(text)
    
#     r.bold = bold
#     r.italic = italic
#     r.font.size = Pt(size_pt)

#     # ✅ Apply font properly for Hindi + English
#     r.font.name = FONT_DOCX
#     r._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_DOCX)

#     # Optional: ensure consistency across all scripts
#     r._element.rPr.rFonts.set(qn('w:ascii'), FONT_DOCX)
#     r._element.rPr.rFonts.set(qn('w:hAnsi'), FONT_DOCX)
#     r._element.rPr.rFonts.set(qn('w:cs'), FONT_DOCX)

#     if char_spacing > 0:
#         set_char_spacing(r, char_spacing)

#     return r

# # # =============================================================================
# # ESTIMATE QUESTION HEIGHT (unchanged)
# # =============================================================================
# def fill_cell(container, q, include_metadata=False):

#     # ================= QUESTION =================
#     p_q = container.add_paragraph()

#     # Indentation
#     p_q.paragraph_format.left_indent = Inches(level2_indent)
#     p_q.paragraph_format.first_line_indent = Inches(level1_indent - level2_indent)

#     # 🔥 TAB SYSTEM (for match questions + alignment)
#     tab_stops = p_q.paragraph_format.tab_stops

#     content_width = page_width - left_margin - right_margin
#     col_gap = 0.08 if num_columns == 3 else 0.12
#     col_width = (content_width - col_gap * (num_columns - 1)) / num_columns

#     # Left start
#     tab_stops.add_tab_stop(Inches(level2_indent), WD_TAB_ALIGNMENT.LEFT)

#     # Right side (for match pairing or alignment)
#     tab_stops.add_tab_stop(Inches(col_width - 0.2), WD_TAB_ALIGNMENT.LEFT)

#     # Detect match-type (contains tab or multi-line structured)
#     is_match = "\t" in q['question']

#     # Add question number
#     add_run(p_q, f"{q['no']}. ", bold=True, size_pt=q_font)

#     if is_match:
#         # 🔥 Match question handling (multi-line)
#         lines = q['question'].split("\n")
#         last_line_idx = len(lines) - 1

#         for i, line in enumerate(lines):
#             if i == 0:
#                 add_run(p_q, line, bold=True, size_pt=q_font)
#                 # If single-line match question, metadata goes inline here
#                 if i == last_line_idx and include_metadata and q.get('metadata'):
#                     tab_stops.add_tab_stop(Inches(col_width - 0.05), WD_TAB_ALIGNMENT.RIGHT)
#                     p_q.add_run("\t")
#                     r_meta = add_run(p_q, q['metadata'], bold=False, size_pt=max(q_font - 1.0, 5.0))
#                     r_meta.italic = True
#             else:
#                 p_line = container.add_paragraph()
#                 p_line.paragraph_format.left_indent = Inches(level2_indent)

#                 # Apply same tab stops
#                 tab_stops_line = p_line.paragraph_format.tab_stops
#                 tab_stops_line.add_tab_stop(Inches(level2_indent), WD_TAB_ALIGNMENT.LEFT)
#                 tab_stops_line.add_tab_stop(Inches(col_width - 0.2), WD_TAB_ALIGNMENT.LEFT)

#                 if "\t" in line:
#                     left, right = line.split("\t", 1)
#                     add_run(p_line, left, size_pt=q_font)
#                     p_line.add_run("\t")
#                     add_run(p_line, right, size_pt=q_font)
#                 else:
#                     add_run(p_line, line, size_pt=q_font)

#                 # Metadata inline on last line of match question
#                 if i == last_line_idx and include_metadata and q.get('metadata'):
#                     tab_stops_line.add_tab_stop(Inches(col_width - 0.05), WD_TAB_ALIGNMENT.RIGHT)
#                     p_line.add_run("\t")
#                     r_meta = add_run(p_line, q['metadata'], bold=False, size_pt=max(q_font - 1.0, 5.0))
#                     r_meta.italic = True

#                 set_spacing(p_line, line_pts=line_spacing, after_pts=para_spacing)
#     else:
#         # Normal question — append metadata inline with right tab on same paragraph
#         add_run(p_q, q['question'], bold=True, size_pt=q_font)

#         if include_metadata and q.get('metadata'):
#             # Right-align metadata at end of question line via tab stop
#             tab_stops.add_tab_stop(Inches(col_width - 0.05), WD_TAB_ALIGNMENT.RIGHT)
#             p_q.add_run("\t")
#             r_meta = add_run(p_q, q['metadata'], bold=False, size_pt=max(q_font - 1.0, 5.0))
#             r_meta.italic = True

#     set_spacing(p_q, line_pts=line_spacing, after_pts=para_spacing)

#     # ================= METADATA (separate paragraph fallback removed — now inline above) =================

#     # ================= OPTIONS =================
#     option_groups = layout_options(
#         q['options'],
#         max_per_line=opts_per_line,
#         char_limit=opt_char_limit
#     )

#     # Dynamic right alignment
#     right_tab_pos = col_width - 0.2

#     for idx, group in enumerate(option_groups):

#         text = ("    ".join(f"{o['key']} {o['text']}" for o in group)
#                 if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")

#         p_opt = container.add_paragraph()
#         p_opt.paragraph_format.left_indent = Inches(level2_indent)

#         add_run(p_opt, text, bold=opt_bold, size_pt=opt_font)

#         # Right aligned answer
#         if show_correct_inline and idx == len(option_groups) - 1:
#             tab_stops = p_opt.paragraph_format.tab_stops
#             tab_stops.add_tab_stop(Inches(right_tab_pos), WD_TAB_ALIGNMENT.RIGHT)

#             p_opt.add_run("\t")
#             add_run(p_opt, q['correct'], bold=True, size_pt=opt_font + 1)

#         set_spacing(p_opt, line_pts=line_spacing, after_pts=para_spacing)

#     # ================= EXPLANATION =================
#     if q['explanation']:

#         p_expl = container.add_paragraph()

#         p_expl.paragraph_format.left_indent = Inches(level2_indent)
#         p_expl.paragraph_format.first_line_indent = Inches(level1_indent - level2_indent)

#         if expl_bg:
#             set_paragraph_background(p_expl, "E6E6E6")

#         prefix = "➤ व्याख्या: " if expl_bullet else "व्याख्या: "

#         add_run(p_expl, prefix, bold=True, size_pt=expl_font)
#         add_run(p_expl, q['explanation'], size_pt=expl_font)

#         set_spacing(p_expl, line_pts=line_spacing, after_pts=para_spacing * 2)

#     # ================= IMAGES =================
#     for img_bytes, width_in, height_in in q.get('explanation_images', []):
#         try:
#             with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
#                 tmp.write(img_bytes)
#                 tmp_path = tmp.name

#             max_img_w = col_width - level2_indent - 0.2
#             img_w = min(width_in if width_in > 0 else 1.5, max_img_w)

#             p_img = container.add_paragraph()
#             p_img.paragraph_format.left_indent = Inches(level2_indent)
#             p_img.add_run().add_picture(tmp_path, width=Inches(img_w))

#             os.unlink(tmp_path)

#             set_spacing(p_img, line_pts=line_spacing, after_pts=para_spacing)

#         except Exception:
#             p_ph = container.add_paragraph()
#             p_ph.paragraph_format.left_indent = Inches(level2_indent)
#             add_run(p_ph, "[चित्र यहाँ संलग्न करें]", italic=True, size_pt=expl_font)

#             if expl_bg:
#                 set_paragraph_background(p_ph, "E6E6E6")

#             set_spacing(p_ph, line_pts=line_spacing, after_pts=para_spacing)

#     # ================= SEPARATOR =================
#     if show_separator:
#         p_sep = container.add_paragraph()
#         set_spacing(p_sep, line_pts=line_spacing, after_pts=2)

#         # ///////////////////////////////////

# def estimate_q_lines(q):
#     lines = 1  # question

#     # Options
#     lines += len(layout_options(q['options'],
#                                max_per_line=opts_per_line,
#                                char_limit=opt_char_limit))

#     # Explanation
#     if q['explanation']:
#         lines += 1  # explanation block

#     # Images
#     lines += len(q.get('explanation_images', [])) * 3

#     return lines

# # =============================================================================
# # PAGE GENERATION (unchanged)
# # =============================================================================
# from docx import Document
# from docx.shared import Inches, Pt
# from docx.enum.text import WD_ALIGN_PARAGRAPH
# from docx.oxml.ns import qn
# from docx.enum.text import WD_BREAK

# def create_page_with_questions(questions, page_num, total_pages, chapter_title):
#     new_doc = Document()

#     # ================= PAGE SETUP =================
#     sec = new_doc.sections[0]
#     sec.page_width = Inches(page_width)
#     sec.page_height = Inches(page_height)
#     sec.top_margin = Inches(top_margin)
#     sec.bottom_margin = Inches(bottom_margin)
#     sec.left_margin = Inches(left_margin)
#     sec.right_margin = Inches(right_margin)

#     # ================= COLUMN SETUP =================
#     sectPr = sec._sectPr
#     cols = sectPr.xpath('./w:cols')[0]
#     cols.set(qn('w:num'), str(num_columns))
#     cols.set(qn('w:space'), "300")

#     # ================= HEADER (real page header) =================
#     header_text = header_template.format(
#         book_name=book_name,
#         chapter_title=chapter_title,
#         page=page_num
#     )

#     sec.header_distance = Inches(0.2)
#     header = sec.header
#     for p in header.paragraphs:
#         p._element.getparent().remove(p._element)

#     hp = header.add_paragraph()
#     hp.alignment = (
#         WD_ALIGN_PARAGRAPH.LEFT if header_align == "Left"
#         else WD_ALIGN_PARAGRAPH.RIGHT if header_align == "Right"
#         else WD_ALIGN_PARAGRAPH.CENTER
#     )

#     hr = hp.add_run(header_text)
#     hr.bold = header_bold
#     hr.font.size = Pt(header_font)
#     hr.font.name = FONT_DOCX
#     hr._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_DOCX)
#     hr._element.rPr.rFonts.set(qn('w:ascii'), FONT_DOCX)
#     hr._element.rPr.rFonts.set(qn('w:hAnsi'), FONT_DOCX)
#     hr._element.rPr.rFonts.set(qn('w:cs'), FONT_DOCX)

#     if header_bg:
#         set_paragraph_background(hp, "E6E6E6")

#     set_spacing(hp, line_pts=header_font + 2, after_pts=4)

#     # ================= TOP PAGE NUMBER =================
#     if page_num_pos.startswith("Top") and not (hide_on_first and page_num == 1):
#         tp = new_doc.add_paragraph()
#         tp.alignment = (
#             WD_ALIGN_PARAGRAPH.LEFT if "Left" in page_num_pos
#             else WD_ALIGN_PARAGRAPH.RIGHT if "Right" in page_num_pos
#             else WD_ALIGN_PARAGRAPH.CENTER
#         )
#         run = tp.add_run(f"पृष्ठ {page_num}")
#         run.font.size = Pt(9)
#         run.font.name = FONT_DOCX
#         set_spacing(tp, line_pts=10, after_pts=3)

#     # ================= CONTENT (FIXED) =================
#     # 🔥 IMPORTANT: No manual column breaks
#     # Word will auto flow content across columns

#     for q in questions:
#         fill_cell(new_doc, q, include_metadata=include_metadata)

#     # ================= BOTTOM PAGE NUMBER =================
#     if page_num_pos.startswith("Bottom") and not (hide_on_first and page_num == 1):
#         bp = new_doc.add_paragraph()
#         bp.alignment = (
#             WD_ALIGN_PARAGRAPH.LEFT if "Left" in page_num_pos
#             else WD_ALIGN_PARAGRAPH.RIGHT if "Right" in page_num_pos
#             else WD_ALIGN_PARAGRAPH.CENTER
#         )
#         run = bp.add_run(f"पृष्ठ {page_num}")
#         run.font.size = Pt(9)
#         run.font.name = FONT_DOCX
#         set_spacing(bp, line_pts=10, before_pts=5)

#     # ================= PAGE BREAK =================
#     if page_num < total_pages:
#         new_doc.add_page_break()

#     return new_doc
  
    

# def generate_multi_page_docx(questions, chapter_title):
#     doc = Document()

#     # ================= PAGE SETUP =================
#     sec = doc.sections[0]
#     sec.page_width = Inches(page_width)
#     sec.page_height = Inches(page_height)
#     sec.top_margin = Inches(top_margin)
#     sec.bottom_margin = Inches(bottom_margin)
#     sec.left_margin = Inches(left_margin)
#     sec.right_margin = Inches(right_margin)

#     # ================= COLUMN SETUP =================
#     sectPr = sec._sectPr
#     cols = sectPr.xpath('./w:cols')[0]
#     cols.set(qn('w:num'), str(num_columns))
#     cols.set(qn('w:space'), "300")

#     # ================= REAL PAGE HEADER (appears on every page) =================
#     header_text = header_template.format(
#         book_name=book_name,
#         chapter_title=chapter_title,
#         page=""  # page numbers handled separately via page_num_pos
#     ).rstrip()

#     sec.header_distance = Inches(0.2)
#     header = sec.header
#     # Clear any default empty paragraph
#     for p in header.paragraphs:
#         p._element.getparent().remove(p._element)

#     hp = header.add_paragraph()
#     hp.alignment = (
#         WD_ALIGN_PARAGRAPH.LEFT if header_align == "Left"
#         else WD_ALIGN_PARAGRAPH.RIGHT if header_align == "Right"
#         else WD_ALIGN_PARAGRAPH.CENTER
#     )

#     hr = hp.add_run(header_text)
#     hr.bold = header_bold
#     hr.font.size = Pt(header_font)
#     hr.font.name = FONT_DOCX
#     hr._element.rPr.rFonts.set(qn('w:eastAsia'), FONT_DOCX)
#     hr._element.rPr.rFonts.set(qn('w:ascii'), FONT_DOCX)
#     hr._element.rPr.rFonts.set(qn('w:hAnsi'), FONT_DOCX)
#     hr._element.rPr.rFonts.set(qn('w:cs'), FONT_DOCX)

#     if header_bg:
#         set_paragraph_background(hp, "E6E6E6")

#     set_spacing(hp, line_pts=header_font + 2, after_pts=4)

#     # ================= CONTENT =================
#     for q in questions:
#         fill_cell(doc, q, include_metadata=include_metadata)

#     return doc

# # =============================================================================
# # HTML PREVIEW – explanation uses hanging indent
# # =============================================================================
# def render_q_preview(q):
#     l1px = level1_indent * 96
#     l2px = level2_indent * 96
#     hang_px = l1px - l2px   # negative

#     option_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
#     opts_html = ""
#     for idx, group in enumerate(option_groups):
#         text = ("&nbsp;&nbsp;&nbsp;&nbsp;".join(f"{o['key']} {o['text']}" for o in group)
#                 if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
#         is_last = idx == len(option_groups) - 1
#         if show_correct_inline and is_last:
#             opts_html += (
#                 f"<div style='display:flex;justify-content:space-between;"
#                 f"margin-left:{l2px}px;font-size:{opt_font}pt;'>"
#                 f"<span>{text}</span>"
#                 f"<span style='font-weight:900;font-size:{opt_font+1.5}pt;'>{q['correct']}</span>"
#                 f"</div>"
#             )
#         else:
#             opts_html += f"<div style='margin-left:{l2px}px;font-size:{opt_font}pt;'>{text}</div>"

#     # Explanation – single block with hanging indent
#     expl_html = ""
#     if q['explanation'] or q.get('explanation_images'):
#         heading_prefix = "➤ व्याख्या: " if expl_bullet else "व्याख्या : "
#         bg_style = "background-color:#F0F0F0;padding:2px 4px;border-radius:3px;" if expl_bg else ""
#         expl_html += (
#             f"<div style='margin-left:{l2px}px;text-indent:{hang_px}px;{bg_style}font-size:{expl_font}pt;'>"
#             f"<span style='font-weight:bold;'>{heading_prefix}</span>"
#         )
#         if q['explanation']:
#             expl_html += q['explanation'].replace('|', '<br>')
#         expl_html += "</div>"

#         # Images after the text
#         for img_bytes, _, __ in q.get('explanation_images', []):
#             b64 = base64.b64encode(img_bytes).decode()
#             expl_html += (
#                 f'<div style="margin-left:{l2px}px;">'
#                 f'<img src="data:image/png;base64,{b64}" style="max-width:100%;height:auto;"></div>'
#             )

#     question_html = q['question'].replace('\n', '<br>')

#     # Build inline metadata: appended right after question text using flex
#     # If the question text + metadata fit on one line → same line (space-between)
#     # If not → metadata wraps to its own right-aligned line naturally
#     if include_metadata and q.get('metadata'):
#         meta_span = (
#             f"<span style='font-weight:normal;font-style:italic;"
#             f"font-size:{max(q_font-1,5)}pt;color:#555;white-space:nowrap;'>"
#             f"&nbsp;&nbsp;{q['metadata']}</span>"
#         )
#         q_html = (
#             f"<div style='margin-left:{l2px}px;text-indent:{hang_px}px;"
#             f"font-size:{q_font}pt;font-weight:bold;margin-bottom:2px;"
#             f"display:flex;justify-content:space-between;align-items:flex-end;'>"
#             f"<span style='white-space:pre-wrap;flex:1;'>{q['no']}. {question_html}</span>"
#             f"{meta_span}"
#             f"</div>"
#         )
#     else:
#         q_html = (
#             f"<div style='margin-left:{l2px}px;text-indent:{hang_px}px;"
#             f"font-size:{q_font}pt;font-weight:bold;margin-bottom:2px;"
#             f"white-space:pre-wrap;'>"
#             f"{q['no']}. {question_html}</div>"
#         )

#     return f"""
# <div class="qblock">
#   {q_html}
#   {opts_html}
#   {expl_html}
#   {('<hr>' if show_separator else '')}
# </div>"""

# def build_preview_with_pagination(questions, q_per_page, chapter_title):
#     total_pages = (len(questions) + q_per_page - 1) // q_per_page
#     pages_html = []
#     for page_num in range(1, total_pages + 1):
#         start = (page_num - 1) * q_per_page
#         end = min(start + q_per_page, len(questions))
#         content_html = "".join(render_q_preview(q) for q in questions[start:end])
#         pages_html.append(f"""
# <div class="page" style="width:{page_width*96}px;min-height:{page_height*96}px;background:white;
#   margin:0 auto 20px auto;padding:{top_margin*96}px {right_margin*96}px {bottom_margin*96}px {left_margin*96}px;
#   box-shadow:0 4px 24px rgba(0,0,0,0.5);">
#   <div style="background:#E6E6E6;padding:4px;border-radius:3px;text-align:center;
#     font-weight:bold;margin-bottom:10px;">
#     {header_template.format(book_name=book_name, chapter_title=chapter_title, page=page_num)}
#   </div>
#   <div style="column-count:{num_columns};column-gap:18px;">{content_html}</div>
# </div>""")

#     return f"""<!DOCTYPE html><html><head><meta charset="utf-8">
# <style>
#   *{{box-sizing:border-box;margin:0;padding:0;}}
#   body{{background:#666;font-family:'Mangal','Arial','Noto Sans Devanagari','Arial',sans-serif;padding:20px;}}
#   .qblock{{margin-bottom:5px;padding-bottom:4px;break-inside:avoid;page-break-inside:avoid;}}
#   hr{{margin:4px 0;border:0;border-top:1px dotted #ccc;}}
# </style>
# </head><body>{''.join(pages_html)}</body></html>"""

# # =============================================================================
# # PDF GENERATION – explanation uses firstLineIndent
# # =============================================================================
# def register_devanagari_font():
#     for path in [
#         "C:/Windows/Fonts/Mangal.ttf",
#         "C:/Windows/Fonts/Nirmala.ttf",
#         "/usr/share/fonts/truetype/msttcorefonts/Mangal.ttf",
#         "/usr/share/fonts/truetype/lohit/Lohit-Devanagari.ttf",
#         "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf",
#     ]:
#         if os.path.exists(path):
#             try:
#                 pdfmetrics.registerFont(TTFont('Devanagari', path))
#                 return 'Devanagari'
#             except Exception:
#                 continue
#     st.warning("⚠️ No Devanagari font found. PDF will use Helvetica.")
#     return 'Helvetica'


# def generate_pdf(questions, chapter_title):
#     font = register_devanagari_font()
#     buffer = BytesIO()
#     doc = SimpleDocTemplate(buffer,
#                             pagesize=(page_width*inch, page_height*inch),
#                             topMargin=top_margin*inch, bottomMargin=bottom_margin*inch,
#                             leftMargin=left_margin*inch, rightMargin=right_margin*inch)
#     styles = getSampleStyleSheet()
#     l1 = level1_indent * inch
#     l2 = level2_indent * inch

#     sQ  = ParagraphStyle('Q',  parent=styles['Normal'], fontSize=q_font,    leading=line_spacing,
#                           fontName=font, spaceAfter=para_spacing, leftIndent=l2, firstLineIndent=l1-l2)
#     sMeta = ParagraphStyle('M', parent=styles['Normal'], fontSize=6,          leading=line_spacing,
#                           fontName=font, alignment=TA_RIGHT, spaceAfter=para_spacing, leftIndent=l2)
#     sOpt  = ParagraphStyle('O', parent=styles['Normal'], fontSize=opt_font,  leading=line_spacing,
#                           fontName=font, spaceAfter=para_spacing, leftIndent=l2)
#     sAns  = ParagraphStyle('A', parent=styles['Normal'], fontSize=opt_font+1.5, leading=line_spacing,
#                           fontName=font, alignment=TA_RIGHT, spaceAfter=para_spacing, leftIndent=l2)
#     sExpl = ParagraphStyle('E', parent=styles['Normal'], fontSize=expl_font, leading=line_spacing,
#                           fontName=font, spaceAfter=para_spacing*2, leftIndent=l2, firstLineIndent=l1-l2,
#                           backColor=colors.HexColor('#F0F0F0') if expl_bg else None)
#     sH    = ParagraphStyle('H', parent=styles['Normal'], fontSize=header_font, leading=header_font+2,
#                           fontName=font, alignment=TA_CENTER,
#                           backColor=colors.HexColor('#E6E6E6') if header_bg else None, spaceAfter=6)

#     story = [Paragraph(header_template.format(book_name=book_name, chapter_title=chapter_title, page=1), sH)]

#     for q in questions:
#         story.append(Paragraph(f"<b>{q['no']}.</b> {q['question']}", sQ))
#         if include_metadata and q.get('metadata'):
#             story.append(Paragraph(q['metadata'], sMeta))

#         opt_groups = layout_options(q['options'], max_per_line=opts_per_line, char_limit=opt_char_limit)
#         for idx, group in enumerate(opt_groups):
#             text = ("    ".join(f"{o['key']} {o['text']}" for o in group)
#                     if len(group) > 1 else f"{group[0]['key']} {group[0]['text']}")
#             is_last = idx == len(opt_groups) - 1
#             story.append(Paragraph(text, sOpt))
#             if show_correct_inline and is_last:
#                 story.append(Paragraph(f"<b>{q['correct']}</b>", sAns))

#         if q['explanation'] or q.get('explanation_images'):
#             heading = ("• व्याख्या : " if expl_bullet else "व्याख्या : ")
#             expl_text = heading + (q['explanation'] if q['explanation'] else "")
#             story.append(Paragraph(expl_text.replace('|', '<br/>'), sExpl))

#             for img_bytes, width_in, height_in in q.get('explanation_images', []):
#                 try:
#                     with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
#                         tmp.write(img_bytes)
#                         tmp_path = tmp.name
#                     content_w = page_width - left_margin - right_margin
#                     col_gap = 0.08 if num_columns == 3 else 0.12
#                     col_w = (content_w - col_gap * (num_columns - 1)) / num_columns
#                     max_w = col_w - level2_indent - 0.05
#                     img_w = min(width_in if width_in > 0 else 1.5, max_w)
#                     story.append(Image(tmp_path, width=img_w*inch, height=height_in*inch))
#                     os.unlink(tmp_path)
#                 except Exception:
#                     story.append(Paragraph("[चित्र यहाँ संलग्न करें]", sExpl))

#         if show_separator:
#             story.append(Spacer(1, 2))

#     doc.build(story)
#     buffer.seek(0)
#     return buffer

# # =============================================================================
# # CHAPTER TITLE EXTRACTION
# # =============================================================================
# def extract_chapter_title(doc):
#     for para in doc.paragraphs[:10]:
#         if "अध्याय" in para.text or "CHAPTER" in para.text.upper():
#             title = para.text.strip()
#             return title[:80] + "..." if len(title) > 80 else title
#     return "RBD PUBLICATION — अध्याय"

# # =============================================================================
# # MAIN APP
# # =============================================================================
# if uploaded_file:
#     doc = Document(uploaded_file)
#     with st.spinner("Parsing questions..."):
#         questions = parse_questions(doc)
#         chapter_title = extract_chapter_title(doc)
#     st.success(f"✅ {len(questions)} questions parsed!")

#     if auto_fill:
#         sample_size = min(10, len(questions))
#         total_lines = sum(estimate_q_lines(q) for q in questions[:sample_size])
#         avg_lines = total_lines / sample_size if sample_size > 0 else 10
#         usable_height = page_height - top_margin - bottom_margin - 1.2
#         lines_per_page = usable_height / (line_spacing / 72.0)
#         q_per_page_est = max(1, int(lines_per_page / avg_lines))
#         total_pages_est = (len(questions) + q_per_page_est - 1) // q_per_page_est
#     else:
#         q_per_page_est = 20
#         total_pages_est = (len(questions) + q_per_page_est - 1) // q_per_page_est

#     st.info(f"📄 Estimated pages: {total_pages_est} ({'auto' if auto_fill else 'fixed'})")

#     tab1, tab2 = st.tabs(["📄 Page Preview", "🔍 Parsed Data"])
#     with tab1:
#         preview_html = build_preview_with_pagination(questions, q_per_page_est, chapter_title)
#         st.components.v1.html(preview_html, height=1200, scrolling=True)
#     with tab2:
#         for q in questions[:5]:
#             with st.expander(f"Q{q['no']} – {q['question'][:60]}…"):
#                 st.write("**Options:**", q['options'])
#                 st.write("**Correct Answer:**", q['correct'])
#                 st.write("**Explanation:**", q['explanation'][:500])
#                 st.write(f"**Explanation images:** {len(q.get('explanation_images', []))}")

#     st.markdown("---")
#     c1, c2 = st.columns(2)
#     with c1:
#         if st.button("🚀 Generate DOCX"):
#             with st.spinner("Generating DOCX..."):
#                 final_doc = generate_multi_page_docx(questions, chapter_title)
#                 filename = f"Formatted_Output_{len(questions)}Q.docx"
#                 final_doc.save(filename)
#                 with open(filename, "rb") as f:
#                     st.download_button("📥 Download DOCX", f, filename,
#                                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
#                 st.success("🎉 DOCX ready!")
#     with c2:
#         if st.button("📑 Preview PDF"):
#             with st.spinner("Generating PDF preview..."):
#                 pdf_buffer = generate_pdf(questions, chapter_title)
#                 pdf_b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
#                 st.markdown(
#                     f'<iframe src="data:application/pdf;base64,{pdf_b64}" '
#                     f'width="100%" height="800" type="application/pdf"></iframe>',
#                     unsafe_allow_html=True)
#                 st.download_button("📥 Download PDF", pdf_buffer,
#                                    file_name="Formatted_Output.pdf", mime="application/pdf")
#                 st.success("🎉 PDF preview ready!")


# # #  correctv 2 - Font Selection + No file save to disk
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
import os

load_dotenv()

GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

# ── Persistent DB path ────────────────────────────────────────────────────
_DB_DIR = os.path.expanduser("~/.streamlit_data")
os.makedirs(_DB_DIR, exist_ok=True)
DB_PATH = os.path.join(_DB_DIR, "rbd_users.db")
# ──────────────────────────────────────────────────────────────────────────

# ── Hardcoded trusted accounts (survive any redeployment) ─────────────────
# Emails are loaded from .env / Streamlit secrets — never hardcoded here.
ADMIN_EMAILS = {
    e.strip() for e in os.getenv("ADMIN_EMAIL", "").split(",") if e.strip()
}
GRANTED_USERS = {
    e.strip() for e in os.getenv("GRANTED_USERS", "").split(",") if e.strip()
}
# ──────────────────────────────────────────────────────────────────────────

def seed_trusted_accounts():
    """Ensure hardcoded admins and granted users always exist in the DB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.datetime.now().isoformat()
    for email in ADMIN_EMAILS:
        c.execute(
            "INSERT OR IGNORE INTO users (email, created_at, is_admin, can_format) VALUES (?, ?, 1, 1)",
            (email, now)
        )
        # Also upgrade existing row in case it was demoted somehow
        c.execute(
            "UPDATE users SET is_admin=1, can_format=1 WHERE email=?",
            (email,)
        )
    for email in GRANTED_USERS:
        c.execute(
            "INSERT OR IGNORE INTO users (email, created_at, is_admin, can_format) VALUES (?, ?, 0, 1)",
            (email, now)
        )
        # Ensure can_format stays granted (but don't touch is_admin)
        c.execute(
            "UPDATE users SET can_format=1 WHERE email=? AND is_admin=0",
            (email,)
        )
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
        # INSERT OR IGNORE: if the user already exists, their can_format
        # permission is preserved and NOT overwritten.
        c.execute(
            "INSERT OR IGNORE INTO users (email, created_at, is_admin, can_format) VALUES (?, ?, ?, ?)",
            (email, now, is_admin, is_admin)
        )
        conn.commit()
    except:
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
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)

        msg = f"Subject: OTP\n\nYour OTP is {code}"

        server.sendmail(GMAIL_EMAIL, email, msg)
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
    """Create a persistent session token valid for 30 days."""
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
    """Return user dict if token is valid and not expired/revoked, else None."""
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
    """Revoke all active sessions for a user (admin action)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE sessions SET is_revoked=1 WHERE email=?", (email,))
    conn.commit()
    conn.close()

def revoke_session(token):
    """Revoke a single session token (logout)."""
    if not token:
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE sessions SET is_revoked=1 WHERE token=?", (token,))
    conn.commit()
    conn.close()

def get_user_sessions(email):
    """Get all active sessions for a user."""
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

                # Create a persistent session token
                token = create_session(user["email"])

                st.session_state["authenticated"] = True
                st.session_state["user_email"] = user["email"]
                st.session_state["is_admin"] = user["is_admin"]
                st.session_state["can_format"] = user["can_format"]
                st.session_state["session_token"] = token

                # Store token in URL query params so it survives page refresh
                st.query_params["session"] = token

                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Invalid OTP")

    if not st.session_state.get("authenticated"):
        st.stop()
   
def clean_text(text):
    if not text:
        return ""
    
    text = re.sub(r'\(.*?\d{2}.*?\[.*?\].*?\(.*?\).*?\)', '', text)
    text = re.sub(r'प्रश्न\s+\d+\s*', '', text)
    text = re.sub(r'^\d+\.\s*', '', text)
    text = re.sub(r'^\.+\s*', '', text)
    text = text.replace('\t', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text
    
def format_matching_question(text):
    if not text:
        return text

    text = text.replace('\n', ' ')
    text = re.sub(r'\s+', ' ', text).strip()

    suchi1 = re.findall(
        r'\(([A-D])\)\s*(.*?)(?=\([A-D]\)|सूची-II|$)',
        text,
        re.DOTALL
    )

    suchi2 = re.findall(
        r'\(([IVX]+)\)\s*(.*?)(?=\([IVX]+\)|$)',
        text,
        re.DOTALL
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
        left = ""
        right = ""

        if i < len(suchi1):
            left = f"({suchi1[i][0]}) {suchi1[i][1]}"

        if i < len(suchi2):
            right = f"({suchi2[i][0]}) {suchi2[i][1]}"

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

# Hindi fonts
HINDI_FONTS = {
    "Mangal": "Mangal",
    "Nirmala UI": "Nirmala UI",
    "Kokila": "Kokila",
    "Aparajita": "Aparajita",
    "Utsaah": "Utsaah",
    "Kruti Dev 010": "Kruti Dev 010",
    "Devanagari New": "Devanagari New",
}

# English fonts
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

st.set_page_config(page_title="RBD Formatter", layout="wide")
st.title("📚 RBD Publication – Smart Formatter")
init_db()
seed_trusted_accounts()  # Always ensure hardcoded accounts exist

# ── Auto-restore session from URL query param ──────────────────────────────
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
            # Token invalid/revoked – clear it from URL
            st.query_params.clear()
# ──────────────────────────────────────────────────────────────────────────

if not st.session_state.get("authenticated"):
    login_page()

# 👑 ADMIN PANEL
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
            if st.button("🚫", key=f"revoke_{email}", help=f"Revoke all sessions for {email}"):
                revoke_user_sessions(email)
                st.sidebar.success(f"Sessions revoked for {email}")
                st.rerun()

        if val != bool(can_format):
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE users SET can_format=? WHERE email=?", (val, email))
            conn.commit()
            conn.close()
            st.rerun()

# 🚪 Logout button (shown to all authenticated users)
if st.session_state.get("authenticated"):
    st.sidebar.markdown("---")
    st.sidebar.write(f"👤 {st.session_state.get('user_email', '')}")
    if st.sidebar.button("🚪 Logout"):
        revoke_session(st.session_state.get("session_token"))
        st.session_state.clear()
        st.query_params.clear()
        st.rerun()

# 🔐 AUTH CHECK
if st.session_state.get("authenticated"):

    if not st.session_state.get("can_format"):
        st.error("❌ You are not allowed to use formatter")
        st.stop()

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

    # =============================================================================
    # FONT SELECTION FOR OUTPUT DOCX
    # =============================================================================
    st.header("🔤 Font Settings (Output DOCX)")

    font_language = st.selectbox(
        "Select Font Language",
        ["Hindi (Devanagari)", "English"],
        index=0,
        help="Choose the language/script of your document to apply appropriate fonts"
    )

    if font_language == "Hindi (Devanagari)":
        selected_font_name = st.selectbox(
            "Select Hindi Font",
            list(HINDI_FONTS.keys()),
            index=0,
            help="These fonts support Devanagari script for Hindi content"
        )
        FONT_DOCX = HINDI_FONTS[selected_font_name]
    else:
        selected_font_name = st.selectbox(
            "Select English Font",
            list(ENGLISH_FONTS.keys()),
            index=0,
            help="Standard English fonts for Latin script content"
        )
        FONT_DOCX = ENGLISH_FONTS[selected_font_name]

    st.caption(f"✅ Selected font: **{FONT_DOCX}** — will be applied to all text in output DOCX")

    st.header("✍️ Text Styling")
    q_font = st.slider("Question font size (pt)", 5.0, 12.0, 5.5, 0.5)

    st.markdown("**Indent levels**")
    st.caption("Level-1: question number '1.' and bullet '•' sit here")
    level1_indent = st.number_input("Level-1 indent (inches)", 0.0, 0.5, 0.0, 0.05)
    st.caption("Level-2: all content text starts here (question text, options, explanation)")
    level2_indent = st.number_input("Level-2 indent (inches)", 0.05, 1.0, 0.15, 0.05)

    q_indent = level2_indent

    opt_font = st.slider("Options font size (pt)", 5.0, 11.0, 5.5, 0.5)
    opt_bold = st.checkbox("Bold options", False)
    ans_font = st.slider("Answer font size (pt)", 5.0, 11.0, 5.5, 0.5)
    ans_bold = st.checkbox("Bold answer", False)
    expl_font = st.slider("Explanation font size (pt)", 5.0, 10.0, 5.5, 0.5)

    st.header("📏 Spacing")
    line_spacing = st.slider("Line spacing (pt)", 8.0, 15.0, 9.5, 0.5)
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

    st.header("📋 Metadata")
    include_metadata = st.checkbox("Include PYQ metadata in output", False,
        help="If checked, exam date/shift/year info found in the source file will be shown with each question.")

    if st.checkbox("Extra compact mode", False):
        line_spacing = 5.0
        para_spacing = 0.0
        q_font = 5.0
        opt_font = 5.0
        ans_font = 5.0
        expl_font = 5.0

# =============================================================================
# PARSING
# =============================================================================
def parse_questions(doc):
    import io

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

    def is_heading(text):
        if not text:
            return False

        return bool(
            re.search(r'अध्याय|CHAPTER', text, re.IGNORECASE) or
            re.match(r'^[^\(]*\(\d{4}\)', text)
        )

    def extract_images_from_para(para):
        images = []
        for run in para.runs:
            for blip in run._element.findall(
                './/a:blip',
                namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
            ):
                rId = blip.get(qn('r:embed'))
                image_part = doc.part.related_parts[rId]
                img_bytes = image_part.blob

                width_in = height_in = 1.0

                extent = run._element.find(
                    './/wp:extent',
                    namespaces={'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
                )

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

        if re.match(r'^\s*(अथवा|तथा)\s*$', text):
            if current_block:
                q = process_question_block(current_block)
                if q:
                    q['no'] = str(len(questions) + 1)
                    questions.append(q)

            current_block = []
            inside_question = False
            continue

        if is_question_start(text):
            if current_block:
                q = process_question_block(current_block)
                if q:
                    q['no'] = str(len(questions) + 1)
                    questions.append(q)

            current_block = [(text, images)]
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
            q_no = m.group(1)
            full_text = full_text[m.end():].strip()
            # Remove any stray leading dot left after stripping the question number
            full_text = re.sub(r'^\.+\s*', '', full_text)
            break

    if not q_no:
        return None

    ans_match = re.search(r'(?:सही उत्तर|उत्तर)\s*:\s*\(([a-dA-D])\)', full_text)
    if not ans_match:
        ans_match = re.search(r'\(([a-dA-D])\)\s*$', full_text)

    correct = f"({ans_match.group(1).lower()})" if ans_match else ""

    explanation = ""

    expl_match = re.search(
        r'व्याख्या\s*:\s*(.*?)(?=\n\s*(\d+\.|प्रश्न\s+\d+)|$)',
        full_text,
        re.DOTALL
    )

    if expl_match:
        explanation = clean_text(expl_match.group(1))

    content = full_text

    if ans_match:
        content = content[:ans_match.start()]
    if expl_match:
        content = content[:expl_match.start()]

    content = content.strip()

    suchi_block = ""
    suchi_match = re.search(r'(सूची.*?)(?=कूट|$)', content, re.DOTALL)

    if suchi_match:
        suchi_block = suchi_match.group(1)
        content = content.replace(suchi_block, "")

    koot_block = ""
    koot_match = re.search(r'(कूट\s*:?.*)', full_text, re.DOTALL)

    if koot_match:
        koot_block = koot_match.group(1)

    first_opt = re.search(r'\([a-dA-D]\)', content)

    if first_opt:
        question_text = content[:first_opt.start()].strip()
        opts_raw = content[first_opt.start():]
    else:
        question_text = content
        opts_raw = ""

    question_text = clean_text(question_text)

    options = []

    if opts_raw:
        opts_raw = re.split(
            r'(?=\n\s*\d+\.)|'
            r'(?=\n\s*प्रश्न\s+\d+)|'
            r'कूट|व्याख्या|उत्तर',
            opts_raw
        )[0]

        matches = re.findall(
            r'\(([a-dA-D])\)\s*(.*?)(?=\([a-dA-D]\)|$)',
            opts_raw,
            re.DOTALL
        )

        for key, text in matches:
            text = clean_text(text)

            if re.search(r'\([a-d]\)\s*-\s*\([ivx]+\)', text, re.IGNORECASE):
                continue

            if "सूची" in text:
                continue

            if text:
                options.append({
                    "key": f"({key.lower()})",
                    "text": text.strip()
                })

    options = options[:4]

    if suchi_block:
        suchi_block = format_matching_question(suchi_block)

    final_question = question_text

    if suchi_block:
        final_question += "\n\n" + suchi_block

    if koot_block:
        final_question += "\n\n" + koot_block.strip()

    explanation_images = []
    answer_idx = -1

    for idx, (txt, _) in enumerate(block):
        if re.search(r'(उत्तर|व्याख्या)', txt):
            answer_idx = idx
            break

    src = block[answer_idx+1:] if answer_idx != -1 else block

    for _, imgs in src:
        explanation_images.extend(imgs)

    meta_match = re.search(
        r'\(([^)]*\d{2,4}[^)]*(?:shift|Shift|पाली|[\[\(][^)\]]*[\]\)])[^)]*)\)',
        full_text
    )
    if not meta_match:
        meta_match = re.search(
            r'\(([^)]*\d{4}[^)]*)\)',
            full_text
        )
    metadata_str = meta_match.group(0).strip() if meta_match else ""

    return {
        "no": q_no,
        "question": final_question,
        "options": options,
        "correct": correct,
        "explanation": explanation,
        "explanation_images": explanation_images,
        "metadata": metadata_str
    }

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

    s.set(qn('w:line'), str(int(line_pts * 20)))
    s.set(qn('w:lineRule'), 'atLeast')

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

def apply_font_to_run(run):
    """Apply the selected FONT_DOCX to all font slots of a run."""
    run.font.name = FONT_DOCX
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.insert(0, rFonts)
    rFonts.set(qn('w:ascii'), FONT_DOCX)
    rFonts.set(qn('w:hAnsi'), FONT_DOCX)
    rFonts.set(qn('w:eastAsia'), FONT_DOCX)
    rFonts.set(qn('w:cs'), FONT_DOCX)

def add_run(para, text, bold=False, size_pt=8, italic=False):
    r = para.add_run(text)
    
    r.bold = bold
    r.italic = italic
    r.font.size = Pt(size_pt)

    apply_font_to_run(r)

    if char_spacing > 0:
        set_char_spacing(r, char_spacing)

    return r

# =============================================================================
# ESTIMATE QUESTION HEIGHT
# =============================================================================
def fill_cell(container, q, include_metadata=False):

    p_q = container.add_paragraph()

    p_q.paragraph_format.left_indent = Inches(level2_indent)
    p_q.paragraph_format.first_line_indent = Inches(level1_indent - level2_indent)

    tab_stops = p_q.paragraph_format.tab_stops

    content_width = page_width - left_margin - right_margin
    col_gap = 0.08 if num_columns == 3 else 0.12
    col_width = (content_width - col_gap * (num_columns - 1)) / num_columns

    tab_stops.add_tab_stop(Inches(level2_indent), WD_TAB_ALIGNMENT.LEFT)
    tab_stops.add_tab_stop(Inches(col_width - 0.2), WD_TAB_ALIGNMENT.LEFT)

    is_match = "\t" in q['question']

    add_run(p_q, f"{q['no']}. ", bold=True, size_pt=q_font)

    if is_match:
        lines = q['question'].split("\n")

        for i, line in enumerate(lines):
            if i == 0:
                add_run(p_q, line, bold=True, size_pt=q_font)
            else:
                p_line = container.add_paragraph()
                p_line.paragraph_format.left_indent = Inches(level2_indent)

                tab_stops = p_line.paragraph_format.tab_stops
                tab_stops.add_tab_stop(Inches(level2_indent), WD_TAB_ALIGNMENT.LEFT)
                tab_stops.add_tab_stop(Inches(col_width - 0.2), WD_TAB_ALIGNMENT.LEFT)

                if "\t" in line:
                    left, right = line.split("\t", 1)
                    add_run(p_line, left, size_pt=q_font)
                    p_line.add_run("\t")
                    add_run(p_line, right, size_pt=q_font)
                else:
                    add_run(p_line, line, size_pt=q_font)

                set_spacing(p_line, line_pts=line_spacing, after_pts=para_spacing)
    else:
        add_run(p_q, q['question'], bold=True, size_pt=q_font)

    set_spacing(p_q, line_pts=line_spacing, after_pts=para_spacing)

    if include_metadata and q.get('metadata'):
        p_meta = container.add_paragraph()
        p_meta.paragraph_format.left_indent = Inches(level2_indent)
        p_meta.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_meta = p_meta.add_run(q['metadata'])
        r_meta.italic = True
        r_meta.font.size = Pt(max(q_font - 1.0, 5.0))
        apply_font_to_run(r_meta)
        set_spacing(p_meta, line_pts=line_spacing, after_pts=0)

    option_groups = layout_options(
        q['options'],
        max_per_line=opts_per_line,
        char_limit=opt_char_limit
    )

    right_tab_pos = col_width - 0.2

    for idx, group in enumerate(option_groups):

        text = ("    ".join(f"{o['key']} {o['text']}" for o in group)
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

    if q['explanation']:

        p_expl = container.add_paragraph()

        p_expl.paragraph_format.left_indent = Inches(level2_indent)
        p_expl.paragraph_format.first_line_indent = Inches(level1_indent - level2_indent)

        if expl_bg:
            set_paragraph_background(p_expl, "E6E6E6")

        prefix = "➤ व्याख्या: " if expl_bullet else "व्याख्या: "

        add_run(p_expl, prefix, bold=True, size_pt=expl_font)
        add_run(p_expl, q['explanation'], size_pt=expl_font)

        set_spacing(p_expl, line_pts=line_spacing, after_pts=para_spacing * 2)

    for img_bytes, width_in, height_in in q.get('explanation_images', []):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(img_bytes)
                tmp_path = tmp.name

            max_img_w = col_width - level2_indent - 0.2
            img_w = min(width_in if width_in > 0 else 1.5, max_img_w)

            p_img = container.add_paragraph()
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
    lines = 1

    lines += len(layout_options(q['options'],
                               max_per_line=opts_per_line,
                               char_limit=opt_char_limit))

    if q['explanation']:
        lines += 1

    lines += len(q.get('explanation_images', [])) * 3

    return lines

# =============================================================================
# PAGE GENERATION
# =============================================================================
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.enum.text import WD_BREAK

def create_page_with_questions(questions, page_num, total_pages, chapter_title):
    new_doc = Document()

    sec = new_doc.sections[0]
    sec.page_width = Inches(page_width)
    sec.page_height = Inches(page_height)
    sec.top_margin = Inches(top_margin)
    sec.bottom_margin = Inches(bottom_margin)
    sec.left_margin = Inches(left_margin)
    sec.right_margin = Inches(right_margin)

    sectPr = sec._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), str(num_columns))
    cols.set(qn('w:space'), "300")

    header_text = header_template.format(
        book_name=book_name,
        chapter_title=chapter_title,
        page=page_num
    )

    sec.header_distance = Inches(0.2)
    header = sec.header
    for p in header.paragraphs:
        p._element.getparent().remove(p._element)

    hp = header.add_paragraph()
    hp.alignment = (
        WD_ALIGN_PARAGRAPH.LEFT if header_align == "Left"
        else WD_ALIGN_PARAGRAPH.RIGHT if header_align == "Right"
        else WD_ALIGN_PARAGRAPH.CENTER
    )

    hr = hp.add_run(header_text)
    hr.bold = header_bold
    hr.font.size = Pt(header_font)
    apply_font_to_run(hr)

    if header_bg:
        set_paragraph_background(hp, "E6E6E6")

    set_spacing(hp, line_pts=header_font + 2, after_pts=4)

    if page_num_pos.startswith("Top") and not (hide_on_first and page_num == 1):
        tp = new_doc.add_paragraph()
        tp.alignment = (
            WD_ALIGN_PARAGRAPH.LEFT if "Left" in page_num_pos
            else WD_ALIGN_PARAGRAPH.RIGHT if "Right" in page_num_pos
            else WD_ALIGN_PARAGRAPH.CENTER
        )
        run = tp.add_run(f"पृष्ठ {page_num}")
        run.font.size = Pt(9)
        apply_font_to_run(run)
        set_spacing(tp, line_pts=10, after_pts=3)

    for q in questions:
        fill_cell(new_doc, q, include_metadata=include_metadata)

    if page_num_pos.startswith("Bottom") and not (hide_on_first and page_num == 1):
        bp = new_doc.add_paragraph()
        bp.alignment = (
            WD_ALIGN_PARAGRAPH.LEFT if "Left" in page_num_pos
            else WD_ALIGN_PARAGRAPH.RIGHT if "Right" in page_num_pos
            else WD_ALIGN_PARAGRAPH.CENTER
        )
        run = bp.add_run(f"पृष्ठ {page_num}")
        run.font.size = Pt(9)
        apply_font_to_run(run)
        set_spacing(bp, line_pts=10, before_pts=5)

    if page_num < total_pages:
        new_doc.add_page_break()

    return new_doc
  
    

def generate_multi_page_docx(questions, chapter_title):
    doc = Document()

    sec = doc.sections[0]
    sec.page_width = Inches(page_width)
    sec.page_height = Inches(page_height)
    sec.top_margin = Inches(top_margin)
    sec.bottom_margin = Inches(bottom_margin)
    sec.left_margin = Inches(left_margin)
    sec.right_margin = Inches(right_margin)

    sectPr = sec._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), str(num_columns))
    cols.set(qn('w:space'), "300")

    header_text = header_template.format(
        book_name=book_name,
        chapter_title=chapter_title,
        page=""
    ).rstrip()

    sec.header_distance = Inches(0.2)
    header = sec.header
    for p in header.paragraphs:
        p._element.getparent().remove(p._element)

    hp = header.add_paragraph()
    hp.alignment = (
        WD_ALIGN_PARAGRAPH.LEFT if header_align == "Left"
        else WD_ALIGN_PARAGRAPH.RIGHT if header_align == "Right"
        else WD_ALIGN_PARAGRAPH.CENTER
    )

    hr = hp.add_run(header_text)
    hr.bold = header_bold
    hr.font.size = Pt(header_font)
    apply_font_to_run(hr)

    if header_bg:
        set_paragraph_background(hp, "E6E6E6")

    set_spacing(hp, line_pts=header_font + 2, after_pts=4)

    for q in questions:
        fill_cell(doc, q, include_metadata=include_metadata)

    return doc

# =============================================================================
# HTML PREVIEW
# =============================================================================
def render_q_preview(q):
    l1px = level1_indent * 96
    l2px = level2_indent * 96
    hang_px = l1px - l2px

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
  body{{background:#666;font-family:'Mangal','Arial','Noto Sans Devanagari','Arial',sans-serif;padding:20px;}}
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
        if include_metadata and q.get('metadata'):
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
            with st.spinner(f"Generating DOCX with font: {FONT_DOCX}..."):
                final_doc = generate_multi_page_docx(questions, chapter_title)
                # ✅ Save to BytesIO - NO file saved to disk
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
                pdf_b64 = base64.b64encode(pdf_buffer.getvalue()).decode()
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{pdf_b64}" '
                    f'width="100%" height="800" type="application/pdf"></iframe>',
                    unsafe_allow_html=True)
                st.download_button("📥 Download PDF", pdf_buffer,
                                   file_name="Formatted_Output.pdf", mime="application/pdf")
                st.success("🎉 PDF preview ready!")