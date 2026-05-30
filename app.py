import streamlit as st
import httpx
import re
import logging

# Set up clean logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configure the Streamlit Page Layout
st.set_page_config(
    page_title="Google Photos Slideshow Scraper",
    page_icon="📸",
    layout="wide"
)

# ---------- Scraper Core Logic (Ported from Emergent) ----------

GOOGLE_PHOTOS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Accept-Language": "en-US,en;q=0.9",
}

PHOTO_URL_REGEX = re.compile(r'(?:https?:)?//lh3\.googleusercontent\.com/pw/[A-Za-z0-9_\-]+')
TITLE_REGEX = re.compile(r"<title>([^<]+)</title>", re.IGNORECASE)

def scrape_shared_album(url: str):
    """Fetches a shared album and parses raw high-res image streams."""
    url = url.strip()
    if not re.match(r"^https?://", url):
        st.error("Invalid URL: Must start with http:// or https://")
        return None

    if "photos.app.goo.gl" not in url and "googleusercontent.com/photos.google.com" not in url:
        st.error("URL must be a valid Google Photos shared album link (e.g., photos.app.goo.gl/...).")
        return None

    try:
        with httpx.Client(follow_redirects=True, timeout=30.0, headers=GOOGLE_PHOTOS_HEADERS) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                st.error(f"Failed to fetch album page from Google (Status Code: {resp.status_code}).")
                return None
            html = resp.text
    except httpx.RequestError as e:
        st.error(f"Network error fetching album target: {e}")
        return None

    # De-duplicate image URLs while preserving original layout ordering
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

    # Apply the high-quality resolution suffix parameters
    sized_photos = [f"{u}=w2048-h2048" for u in photos]

    # Parse album page title
    title_match = TITLE_REGEX.search(html)
    title = title_match.group(1).strip() if title_match else "Shared Album"
    if title.endswith("- Google Photos"):
        title = title[:-len("- Google Photos")].strip()

    if not sized_photos:
        st.error("No photos discovered. Verify the album visibility is set to 'Anyone with the link'.")
        return None

    return {"title": title, "photos": sized_photos, "count": len(sized_photos)}

# ---------- Streamlit UI Render Layer ----------

st.title("📸 Google Photos Shared Album View")
st.write("Extract high-res image sources directly without setting up GCP credentials or API keys.")

# Input Field
album_url = st.text_input("Paste Google Photos Shared Album URL:", placeholder="https://photos.app.goo.gl/...")

if album_url:
    with st.spinner("Executing Googlebot parsing layer..."):
        album_data = scrape_shared_album(album_url)
    
    if album_data:
        st.success(f"Successfully processed **{album_data['title']}** — Found {album_data['count']} photos.")
        
        # Display layout options
        view_mode = st.radio("Display Mode:", ["Grid View", "Single Slideshow View"], horizontal=True)
        
        st.markdown("---")
        
        if view_mode == "Grid View":
            # Display images in a clean 3-column responsive layout matrix
            cols = st.columns(3)
            for idx, photo_url in enumerate(album_data["photos"]):
                col_target = cols[idx % 3]
                col_target.image(photo_url, use_container_width=True)
        
        elif view_mode == "Single Slideshow View":
            # Slider control to click through the items sequentially
            photo_index = st.slider("Select Image Index", 1, album_data["count"], 1)
            st.image(album_data["photos"][photo_index - 1], use_container_width=True)
