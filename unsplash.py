import requests
import re

ACCESS_KEY = "SYKUTgHGFtWXIhWrac31F1hcNQPUEX1TebpznT9tW2Q"

def replace_images_in_html(html_content, api_key):
    # Regex to find all <img> tags with an alt attribute
    img_tag_pattern = r'<img\s+[^>]*alt="([^"]+)"[^>]*>'
    
    # Regex to find background URLs in CSS styles
    css_bg_pattern = r'background\s*:\s*[^;]*url\(([^)]+)\)'  # Capture only the URL part of background

    # Function to get a photo from Unsplash based on the alt text
    def get_unsplash_photo(query):
        url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1"
        headers = {"Authorization": f"Client-ID {api_key}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data['results']:
                return data['results'][0]['urls']['regular']
            else:
                print(f"No photos found for '{query}'")
                return "error-placeholder.png"
        else:
            print(f"Error fetching photo for '{query}': {response.status_code}")
            return "error-placeholder.png"

    # Function to replace the src attribute in <img> tags
    def replace_img_tag(match):
        alt_text = match.group(1)  # Extract the alt text
        new_image_url = get_unsplash_photo(alt_text)  # Fetch a new image URL
        return re.sub(r'src="[^"]*"', f'src="{new_image_url}"', match.group(0))  # Replace src

    # Function to replace CSS background URLs
    def replace_css_bg(match):
        original_bg = match.group(0)  # Entire background property
        original_url = match.group(1)  # Extract the URL part
        new_image_url = get_unsplash_photo(original_url)  # Get new URL from Unsplash API
        # Replace the URL in the background CSS with the new one
        updated_bg = original_bg.replace(original_url, new_image_url)
        return updated_bg

    # Apply the replacements for <img> tags
    updated_html = re.sub(img_tag_pattern, replace_img_tag, html_content)

    # Apply the replacements for CSS background URLs
    updated_html = re.sub(css_bg_pattern, replace_css_bg, updated_html)

    return updated_html

