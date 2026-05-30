import streamlit as st
import httpx
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure Page Layout to scale identically to a clean React canvas
st.set_page_config(
    page_title="Google Photos Slideshow Scraper",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------- shadcn/ui Design System Injection ----------
# This overrides Streamlit's structural layout to inject the exact premium elements from your React dump
st.markdown("""
    <style>
        /* Base Canvas Background Styling */
        .stApp {
            background-color: #09090b !important;
            color: #fafafa !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Main Header Custom Layout */
        .main-header {
            text-align: center;
            padding: 2.5rem 0 1.5rem 0;
        }
        .main-title {
            font-size: 2.5rem;
            font-weight: 700;
            letter-spacing: -0.05em;
            color: #fafafa;
            margin-bottom: 0.5rem;
        }
        .main-subtitle {
            font-size: 1rem;
            color: #a1a1aa;
            font-weight: 400;
        }

        /* Premium shadcn Card Styling Wrapper */
        div[data-testid="stVerticalBlock"] > div:has(div.shadcn-card) {
            background-color: #09090b;
            border: 1px solid #27272a;
            border-radius: 0.75rem;
            padding: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            margin-bottom: 2rem;
        }

        /* Beautiful Input Component Overrides */
        div[data-testid="stTextInput"] > div > div > input {
            background-color: #09090b !important;
            color: #fafafa !important;
            border: 1px solid #27272a !important;
            border-radius: 0.375rem !important;
            padding: 0.5rem 0.75rem !important;
            font-size: 0.875rem !important;
            transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
        }
        div[data-testid="stTextInput"] > div > div > input:focus {
            border-color: #fafafa !important;
            box-shadow: 0 0 0 1px #fafafa !important;
        }
        
        /* Premium Image Canvas Frame */
        .image-container {
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: #18181b;
            border: 1px solid #27272a;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-top: 1.5rem;
            overflow: hidden;
            box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.06);
        }
        .image-container img {
            border-radius: 0.375rem;
            max-height: 70vh;
            object-fit: contain;
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        /* Clean Matrix Grid Framing */
        .grid-item {
            border-radius: 0.5rem;
            overflow: hidden;
            border: 1px solid #27272a;
            background-color: #18181b;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .grid-item:hover {
            transform: translateY(-2px);
            border-color: #3f3f46;
        }

        /* Target Streamlit Default Info Overrides */
        div[data-testid="stMarkdownContainer"] > p {
            color: #a1a1aa;
        }
        
        /* Hide default distracting Streamlit elements */
        #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ---------- Core Googlebot Extraction Engine ----------
GOOGLE_PHOTOS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Accept-Language": "en-US,en;q=0.9",
}

PHOTO_URL_REGEX = re.compile(r'(?:https?:)?//lh3\.googleusercontent\.com/pw/[A-Za-z0-9_\-]+')
TITLE_REGEX = re.compile(r"<title>([^<]+)</title>", re.IGNORECASE)

def scrape_shared_album(url: str):
    url = url.strip()
    if not re.match(r"^https?://", url):
        st.error("Invalid URL format. Please supply a valid HTTP/HTTPS link.")
        return None

    if "photos.app.goo.gl" not in url and "http://googleusercontent.com/photos.google.com/5" not in url:
        st.error("Target address structure must map directly to a shared Google Photos workspace vector.")
        return None

    try:
        with httpx.Client(follow_redirects=True, timeout=30.0, headers=GOOGLE_PHOTOS_HEADERS) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                st.error(f"Upstream link resolution failure: Google server status trace {resp.status_code}")
                return None
            html = resp.text
    except httpx.RequestError as e:
        st.error(f"Parsing runtime crash during HTTP pipeline build execution: {e}")
        return None

    # De-duplicate image targets without order corruption
    seen = set()
    photos = []
    for m in PHOTO_URL_REGEX.finditer(html):
        u = m.group(0)
        if u.startswith("//"):
            u = "https:" + u
        if u in seen:
            continue
        seen.add(u)
        photos.append(u)

    # Inject the maximum resolution canvas configurations
    sized_photos = [f"{u}=w2048-h2048" for u in photos]

    title_match = TITLE_REGEX.search(html)
    title = title_match.group(1).strip() if title_match else "Shared Album Workspace"
    if title.endswith("- Google Photos"):
        title = title[:-len("- Google Photos")].strip()

    if not sized_photos:
        st.error("No image stream vectors detected. Confirm that album sharing visibility permissions match public query standards.")
        return None

    return {"title": title, "photos": sized_photos, "count": len(sized_photos)}

# ---------- App Interface Layer ----------

# Header System Layout
st.markdown("""
    <div class="main-header">
        <div class="main-title">📸 Photo Display Engine</div>
        <div class="main-subtitle">A zero-cost standalone replacement for your cloud-hosted scrapers</div>
    </div>
""", unsafe_allow_html=True)

# Main control canvas wrapper container
st.markdown('<div class="shadcn-card">', unsafe_allow_html=True)
album_url = st.text_input("Shared Album Source Vector URL", placeholder="https://photos.app.goo.gl/...")
st.markdown('</div>', unsafe_allow_html=True)

if album_url:
    with st.spinner("Processing asset arrays..."):
        album_data = scrape_shared_album(album_url)
    
    if album_data:
        # Top Dashboard Control Meta Metrics Bar
        col_meta, col_toggle = st.columns([2, 1])
        with col_meta:
            st.markdown(f"### {album_data['title']}")
            st.markdown(f"Identified **{album_data['count']}** high-res graphic streams.")
        with col_toggle:
            view_mode = st.radio("Display Element View Mode", ["Single Slideshow Mode", "Responsive Matrix Grid"], horizontal=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if view_mode == "Responsive Matrix Grid":
            # 3-Column Modern Grid Array
            cols = st.columns(3)
            for idx, photo_url in enumerate(album_data["photos"]):
                target_col = cols[idx % 3]
                with target_col:
                    st.markdown(f'<div class="grid-item">', unsafe_allow_html=True)
                    st.image(photo_url, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
        
        elif view_mode == "Single Slideshow Mode":
            # Centered Slider Element Config to match index views
            photo_index = st.slider("Step Index Array Progression", 1, album_data["count"], 1)
            
            # Focused single image viewer
            st.markdown('<div class="image-container">', unsafe_allow_html=True)
            st.image(album_data["photos"][photo_index - 1], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
