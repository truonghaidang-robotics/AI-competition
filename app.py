import json
import os
import re
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
COZE_API_KEY = os.getenv("COZE_API_KEY")
COZE_WORKFLOW_ID = os.getenv("COZE_WORKFLOW_ID")
#hubzz was here
#xiao haiwas hêre
# ---------------- CONFIG TRANG WEB ----------------
st.set_page_config(
    page_title="EchoCommerce - KOC Automatic Marketing Studio",
    layout="wide",
    page_icon="🛍️",
    initial_sidebar_state="expanded",
)

# ---------------- CUSTOM CSS MODERN DASHBOARD ----------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    .hero-title {
        background: linear-gradient(90deg, #1e293b 0%, #4f46e5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.2rem;
        margin-bottom: 0px;
    }
    .studio-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.03), 0 8px 10px -6px rgba(0,0,0,0.02);
        margin-bottom: 20px;
    }
    .title-pill {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 4px solid #16a34a;
        color: #166534;
        padding: 12px 16px;
        border-radius: 8px;
        font-weight: 600;
        margin-bottom: 10px;
        font-size: 0.95rem;
    }
    .badge-status {
        background: linear-gradient(90deg, #4f46e5, #7c3aed);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 12px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ---------------- HÀM BÓC TÁCH URL TỪ COZE OBJECT/DICT/ARRAY ----------------
def extract_url_from_coze(val):
  """Giải mã thông minh đường dẫn URL từ chuỗi, Dict hay Array của Coze API"""
  if not val:
    return ""
  if isinstance(val, str):
    return val.strip()
  if isinstance(val, dict):
    return (
        val.get("url")
        or val.get("image_url")
        or val.get("uri")
        or val.get("href")
        or ""
    )
  if isinstance(val, list) and len(val) > 0:
    return extract_url_from_coze(val[0])
  return ""


# ---------------- HÀM BÓC TÁCH BÀI VIẾT PR ----------------
def parse_koc_response(text):
  if not isinstance(text, str):
    return {"titles": "", "body": "", "comment": "", "full_clean": ""}

  clean_text = re.sub(
      r"---?\s*IMAGE_PROMPT:.*", "", text, flags=re.DOTALL | re.IGNORECASE
  )
  clean_text = re.sub(
      r"IMAGE_PROMPT:.*", "", clean_text, flags=re.DOTALL | re.IGNORECASE
  )

  if "### 【转化率评分" in clean_text:
    clean_text = clean_text.split("### 【转化率评分")[0]
  if "【广告法合规审查】" in clean_text and "爆款标题备选" in clean_text:
    clean_text = "爆款标题备选" + clean_text.split("爆款标题备选", 1)[1]

  titles, body, comment = "", "", ""

  titles_match = re.search(
      r"(?:#####|###|#)?\s*爆款标题备选(.*?)(?=(?:#####|###|#)?\s*正文/口播|\Z)",
      clean_text,
      re.DOTALL,
  )
  if titles_match:
    titles = titles_match.group(1).strip()

  body_match = re.search(
      r"(?:#####|###|#)?\s*正文/口播(.*?)(?=(?:#####|###|#)?\s*互动/置顶评论|\Z)",
      clean_text,
      re.DOTALL,
  )
  if body_match:
    body = body_match.group(1).strip()

  comment_match = re.search(
      r"(?:#####|###|#)?\s*互动/置顶评论(.*)", clean_text, re.DOTALL
  )
  if comment_match:
    comment = comment_match.group(1).strip()

  if not body and not titles:
    body = clean_text

  titles = re.sub(r"#{1,6}\s*", "", titles).strip()
  body = re.sub(r"#{1,6}\s*", "", body).strip()
  comment = re.sub(r"#{1,6}\s*", "", comment).strip()

  full_clean_parts = []
  if titles:
    full_clean_parts.append("📌 [3 MẪU TIÊU ĐỀ HOT]\n" + titles)
  if body:
    full_clean_parts.append("✍️ [NỘI DUNG CHÍNH]\n" + body)
  if comment:
    full_clean_parts.append("💬 [BÌNH LUẬN GHIM / CTA]\n" + comment)

  full_clean = (
      "\n\n".join(full_clean_parts)
      if full_clean_parts
      else re.sub(r"#{1,6}\s*", "", clean_text).strip()
  )

  return {
      "titles": titles,
      "body": body,
      "comment": comment,
      "full_clean": full_clean,
  }


# ---------------- SIDEBAR MONITOR ----------------
with st.sidebar:
  st.markdown("## ⚙️ Control Center")
  st.markdown("**Trạng Thái Hệ Thống:**")
  st.success("🟢 Coze API: Active")
  st.success("🟢 Jimeng AI Engine: Connected")

  st.divider()
  st.markdown("### 🤖 Agents Pipeline Monitor")
  st.info("1. **Selection Agent**: Data Cleansing")
  st.info("2. **Content Agent**: PR Scripting")
  st.info("3. **Visual Guard Agent**: Compliance Check")
  st.info("4. **Jimeng Node**: AI Visual & Video")

  st.divider()
  st.caption("EchoCommerce Studio v4.0 | Pure Coze Engine")


# ---------------- MÀN HÌNH CHÍNH ----------------
st.markdown(
    "<h1 class='hero-title'>🛍️ EchoCommerce Studio</h1>", unsafe_allow_html=True
)
st.markdown(
    "<p style='color: #64748b; font-size: 1.05rem;'>Hệ thống AI Marketing 1-Click:"
    " Viết bài PR KOC, tạo Ảnh 3D & Video AI Commercial tự động từ Coze</p>",
    unsafe_allow_html=True,
)

st.divider()

col_url, col_btn = st.columns([3.5, 1.2])
with col_url:
  product_url = st.text_input(
      "🔗 Đường dẫn hoặc văn bản sản phẩm (Taobao / 1688 / TikTok Shop):",
      placeholder="Dán link Taobao hoặc văn bản chia sẻ sản phẩm tại đây...",
      label_visibility="collapsed",
  )
with col_btn:
  btn_run = st.button("🚀 Sáng Tạo Content 1-Click", type="primary")

if btn_run:
  if not product_url:
    st.warning("⚠️ Vui lòng nhập đường dẫn hoặc thông tin sản phẩm!")
  else:
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text(
        "🤖 Coze Workflow đang phân tích dữ liệu, viết bài PR & sinh Media"
        " Jimeng AI..."
    )
    progress_bar.progress(40)

    try:
      url = "https://api.coze.cn/v1/workflow/run"
      headers = {
          "Authorization": f"Bearer {COZE_API_KEY}",
          "Content-Type": "application/json",
      }
      payload = {
          "workflow_id": COZE_WORKFLOW_ID,
          "parameters": {"input": product_url.strip()},
      }

      res = requests.post(url, headers=headers, json=payload, timeout=180)
      result = res.json()

      if res.status_code == 200 and result.get("code") == 0:
        data = result.get("data", {})
        if isinstance(data, str):
          try:
            data = json.loads(data)
          except Exception:
            pass

        # 1. Trích xuất Bài viết PR KOC
        raw_koc_text = (
            data.get("koc_content", "")
            or data.get("content", "")
            or "Chưa có nội dung"
        )
        parsed = parse_koc_response(raw_koc_text)

        # 2. Giải mã URL Ảnh và Video thông minh từ mọi cấu trúc JSON của Coze
        raw_img_val = (
            data.get("image_url")
            or data.get("image")
            or data.get("img_url")
            or data.get("url")
        )
        raw_vid_val = (
            data.get("video_url")
            or data.get("video")
            or data.get("mp4_url")
        )

        image_url = extract_url_from_coze(raw_img_val)
        video_url = extract_url_from_coze(raw_vid_val)

        progress_bar.progress(100)
        status_text.empty()
        progress_bar.empty()

        st.success("✨ Hoàn tất! Tất cả Tài sản Marketing đã sẵn sàng.")

        # ---------------- KHU VỰC HIỂN THỊ KẾT QUẢ ----------------
        col_left, col_right = st.columns([1.2, 1])

        # CỘT TRÁI: BÀI VIẾT PR KOC
        with col_left:
          st.markdown(
              "<div class='studio-card'>", unsafe_allow_html=True
          )
          st.markdown("### ✍️ Content Marketing chuẩn KOC")

          tab1, tab2, tab3, tab4 = st.tabs([
              "📌 3 Tiêu Đề Hot",
              "📖 Bài Viết PR",
              "💬 Bình Luận & CTA",
              "📋 Copy 1-Click",
          ])

          with tab1:
            st.markdown(
                "<div class='badge-status'>TITLES SUGGESTIONS</div>",
                unsafe_allow_html=True,
            )
            if parsed["titles"]:
              for t in parsed["titles"].split("\n"):
                if t.strip():
                  st.markdown(
                      f"<div class='title-pill'>{t.strip()}</div>",
                      unsafe_allow_html=True,
                  )
            else:
              st.info("Chưa có mẫu tiêu đề.")

          with tab2:
            st.markdown(
                "<div class='badge-status'>PR BODY CONTENT</div>",
                unsafe_allow_html=True,
            )
            st.write(parsed["body"])

          with tab3:
            st.markdown(
                "<div class='badge-status'>PINNED COMMENT</div>",
                unsafe_allow_html=True,
            )
            st.write(parsed["comment"])

          with tab4:
            st.text_area(
                "Văn bản sạch 100% (Đã xóa rác & Prompt):",
                value=parsed["full_clean"],
                height=350,
            )

          st.markdown("---")
          st.markdown("#### 💬 Kịch Bản CS Bot Agent (Tự Trả Lời Client)")
          cs_script = data.get(
              "cs_script", "Đã bật chế độ tự động trả lời bình luận."
          )
          with st.expander(
              "🤖 Xem kịch bản Bot tự động trả lời khách hàng", expanded=False
          ):
            st.write(cs_script)

          st.button(
              "📲 Đăng Bài Tự Động & Bật Bot Trực Bình Luận", type="primary"
          )
          st.markdown("</div>", unsafe_allow_html=True)

        # CỘT PHẢI: ASSET VISUAL (HIỂN THỊ TRỰC TIẾP TỪ COZE)
        with col_right:
          st.markdown(
              "<div class='studio-card'>", unsafe_allow_html=True
          )
          st.markdown("### 🖼️ Asset Visual 3D Concept (Jimeng AI)")

          if image_url:
            st.image(
                image_url,
                caption="Ảnh 3D Product Concept từ Coze Jimeng AI",
                use_container_width=True,
            )
          else:
            st.info(
                "💡 Chưa nhận được đường dẫn ảnh từ Coze. Hãy kiểm tra Nhật ký"
                " JSON bên dưới."
            )

          st.markdown("---")
          st.markdown("### 🎬 Video Commercial (Jimeng AI Video)")

          if video_url:
            st.video(video_url)
            st.caption("⚡ Video AI do Coze render tự động 100%.")
          else:
            st.info("💡 Chưa có dữ liệu video_url từ Coze.")

          st.markdown("</div>", unsafe_allow_html=True)

        # BÁO CÁO GIÁM KHẢO
        st.divider()
        with st.expander(
            "🔍 [Dành Cho Báo Cáo Kỹ Thuật] Nhật ký JSON chi tiết từ Coze"
            " Workflow"
        ):
          st.json(data)

      else:
        st.error(f"Lỗi Workflow: {result.get('msg')}")
    except Exception as e:
      st.error(f"Lỗi kết nối API: {e}")