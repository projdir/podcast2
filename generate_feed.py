# import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET
from xml.dom import minidom

# --- CONFIGURATION ---
BASE_AUDIO_URL = "https://archive.rthk.hk/mp3/radio/contentIndex/radio1/World_in_a_Nutshell/m4a"
IMAGE_URL = "https://podcast.rthk.hk/podcast/upload_photo/item_photo/1400x1400_293.jpg"
FEED_TITLE = "十萬八千里"
FEED_DESCRIPTION = "九十分鐘走遍世界，每週陪你漫遊《十萬八千里》"
FEED_LINK = "https://projdir.github.io/podcast2/podcast.xml"
# ---------------------

# Define HK Timezone globally
tz = ZoneInfo("Asia/Hong_Kong")

def get_last_saturday_and_pubdate():
    """Calculates the yyyymmdd string and the RFC 822 pubDate for the most recent Saturday in HK."""
    # Fetch the precise time right now in Western Australia
    today = datetime.now(tz)
    
    # datetime.weekday() returns 0 for Monday, 5 for Saturday, 6 for Sunday
    # When running on Sunday morning in WA, this accurately subtracts 1 day to hit Saturday
    days_to_subtract = (today.weekday() - 5) % 7
    last_saturday = today - timedelta(days=days_to_subtract)
    
    # Format the date string for the audio URLs (yyyymmdd)
    date_str = last_saturday.strftime("%Y%m%d")
    
    # Construct a proper RFC 822 pubDate string with the +0800 offset for the RSS feed
    # e.g., "Sat, 30 May 2026 12:00:00 +0800"
    pub_date_rss = last_saturday.replace(hour=12, minute=0, second=0, microsecond=0).strftime("%a, %d %b %Y %H:%M:%S %z")
    
    return date_str, pub_date_rss

def generate_xml():
    date_str, pub_date_rss = get_last_saturday_and_pubdate()
    
    # Create root RSS element with iTunes namespace
    rss = ET.Element("rss", version="2.0", attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"})
    channel = ET.SubElement(rss, "channel")

    # Channel Metadata
    ET.SubElement(channel, "title").text = FEED_TITLE
    ET.SubElement(channel, "description").text = FEED_DESCRIPTION
    ET.SubElement(channel, "link").text = FEED_LINK
    ET.SubElement(channel, "language").text = "zh-CN"
    
    # Podcast Image
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = IMAGE_URL
    ET.SubElement(image, "title").text = FEED_TITLE
    ET.SubElement(image, "link").text = FEED_LINK
    # ET.SubElement(channel, "itunes:image", href=IMAGE_URL)

    # Add the 3 audio fragments as feed items
    for part in ["1", "2", "3"]:
        audio_url = f"{BASE_AUDIO_URL}/{date_str}_{part}.m4a"
        
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = f"Broadcast {date_str} - Part {part}"
        ET.SubElement(item, "description").text = f"Part {part} of the broadcast on {date_str}."
        ET.SubElement(item, "pubDate").text = pub_date_rss
        
        # Unique identifier for AntennaPod to track history
        ET.SubElement(item, "guid", isPermaLink="false").text = f"{date_str}_{part}"
        
        # Enclosure element maps the media file payload
        ET.SubElement(item, "enclosure", url=audio_url, length="0", type="audio/mp4")

    # Pretty print XML
    xml_str = ET.tostring(rss, encoding="utf-8")
    parsed_xml = minidom.parseString(xml_str)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")

    # Save output inside public directory for GitHub Pages
    # os.makedirs("public", exist_ok=True)
    with open("podcast.xml", "w", encoding="utf-8") as f:
        f.write(pretty_xml)

if __name__ == "__main__":
    generate_xml()
