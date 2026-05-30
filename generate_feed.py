import datetime
from zoneinfo import ZoneInfo
import urllib.request
import xml.etree.ElementTree as ET
from xml.dom import minidom

# --- CONFIGURATION ---
BASE_URL = "https://archive.rthk.hk/mp3/radio/archive/radio1/hktoday/m4a/"  # Replace with the actual base URL
STATION_NAME = "晨早新聞天地"
FEED_DESCRIPTION = "Archived episodes of the programme."
AUTHOR = "Radio Station"
FEED_URL = "https://projdir.github.io/podcast2/podcast.xml" # Update later
IMAGE_URL = "https://podcast.rthk.hk/podcast/upload_photo/item_photo/1400x1400_916.jpg"

def check_url_exists(url):
    """Checks if the audio file actually exists on the server."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req) as response:
            return response.status == 200
    except Exception:
        return False

def create_rss():
    # 1. Initialize RSS structure
    rss = ET.Element("rss", version="2.0", xmlns_itunes="http://www.itunes.com/dtds/podcast-1.0.dtd")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = STATION_NAME
    ET.SubElement(channel, "link").text = FEED_URL
    ET.SubElement(channel, "description").text = f"Custom archive feed for {STATION_NAME}"
    ET.SubElement(channel, "language").text = "zh-CN"

    # iTunes Specific Fields for AntennaPod compatibility
    # ET.SubElement(channel, "itunes:author").text = AUTHOR
    # ET.SubElement(channel, "itunes:summary").text = FEED_DESCRIPTION
    # ET.SubElement(channel, "itunes:explicit").text = "no"
    
    # Podcast Artwork Image
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = IMAGE_URL
    ET.SubElement(image, "title").text = STATION_NAME
    ET.SubElement(image, "link").text = FEED_URL
    
    # itunes_image = ET.SubElement(channel, "itunes:image", href=IMAGE_URL)    

    # 2. Generate dates to check (e.g., the last 3 days)
    tz = ZoneInfo("Asia/Hong_Kong")
    today = datetime.datetime.now(tz).date()
    # today = datetime.date.today()
    for i in range(3):
        current_date = today - datetime.timedelta(days=i)
        date_str = current_date.strftime("%Y%m%d")
        episode_url = f"{BASE_URL}{date_str}.m4a"

        # Check if the episode exists before adding it
        if check_url_exists(episode_url):
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = f"晨早新聞天地 {current_date.strftime('%Y-%m-%d')}"
            ET.SubElement(item, "link").text = episode_url
            ET.SubElement(item, "guid", isPermaLink="true").text = episode_url
            
            # Convert date to RFC 822 format for RSS
            pub_date = datetime.datetime.combine(current_date, datetime.time(12, 0)).strftime("%a, %d %b %Y %H:%M:%S +0000")
            ET.SubElement(item, "pubDate").text = pub_date
            
            # Enclosure tag tells AntennaPod it's an audio file
            ET.SubElement(item, "enclosure", url=episode_url, length="0", type="audio/mp4")

    # 3. Format and save XML
    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
    with open("podcast.xml", "w", encoding="utf-8") as f:
        f.write(xml_str)

if __name__ == "__main__":
    create_rss()
