import openai
import requests
import re
import streamlit as st
ACCESS_KEY = "SYKUTgHGFtWXIhWrac31F1hcNQPUEX1TebpznT9tW2Q"
from openai import OpenAI

OPENAI_KEY = st.secrets["OPENAI_API_KEY"]
GITHUB_KEY = st.secrets["GITHUB_KEY"]
OPEN_PROVIDER_KEY = st.secrets["OPEN_PROVIDER_KEY"]
UNSPLASH_API_KEY = st.secrets["UNSPLASH_API_KEY"]


client = OpenAI(api_key=OPENAI_KEY)

import re
import requests
import openai

def replace_images_in_html(html_content, client, api_key):
    # Regex to find all <img> tags with an alt attribute
    img_tag_pattern = r'<img\s+[^>]*alt="([^"]+)"[^>]*>'
    # Regex to find background URLs in CSS styles
    css_bg_pattern = r'background\s*:\s*[^;]*url\(([^)]+)\)'

    # Counter to track the number of images replaced
    image_counter = {"count": 0}

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

    # Function to generate an image using OpenAI's DALL-E
    def generate_image(prompt, size="1024x1024"):
        try:
            response = client.images.generate(
                prompt=prompt,
                n=1,
                size=size
            )
            image_url = response.data[0].url
            return image_url
        except openai.APIError as e:
            print(f"Error generating image: {e}")
            return None

    # Function to replace CSS background URLs
    def replace_css_bg(match):
        original_bg = match.group(0)  # Entire background property
        original_url = match.group(1)  # Extract the URL part
        image_counter["count"] += 1  # Increment image count

        if image_counter["count"] <= 5:
            new_image_url = generate_image('this image will serve as a background for a website, it should be aesthetic '+ original_url)  # Use OpenAI for first 5 images
        else:
            new_image_url = get_unsplash_photo(original_url)  # Use Unsplash for the rest

        updated_bg = original_bg.replace(original_url, new_image_url)
        return updated_bg

    # Function to replace the src attribute in <img> tags
    def replace_img_tag(match):
        alt_text = match.group(1)  # Extract the alt text
        image_counter["count"] += 1  # Increment image count

        if image_counter["count"] <= 5:
            new_image_url = generate_image(alt_text)  # Use OpenAI for first 5 images
        else:
            new_image_url = get_unsplash_photo(alt_text)  # Use Unsplash for the rest

        return re.sub(r'src="[^"]*"', f'src="{new_image_url}"', match.group(0))  # Replace src

    # ✅ First, apply the replacements for CSS background URLs
    updated_html = re.sub(css_bg_pattern, replace_css_bg, html_content)

    # ✅ Next, apply the replacements for <img> tags
    updated_html = re.sub(img_tag_pattern, replace_img_tag, updated_html)

    return updated_html






# print(generate_image(client,"india"))