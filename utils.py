import requests
import base64
import openai
from prompt import generate_system_prompt
import streamlit as st
import re
import config

OPENAI_KEY = config.OPENAI_KEY
openai.api_key = OPENAI_KEY



def initialize_app():
    st.set_page_config(
        page_title='WebsiteGPT',
        page_icon='🤖',
        layout="wide",
        initial_sidebar_state='collapsed',
    )
    st.title("Let’s bring your business to life!")
    st.markdown("""
                WebsiteGPT is your AI-powered assistant to create and deploy stunning websites effortlessly. 🚀
                """)
    with st.sidebar:
        st.markdown('<center><h1>WebsiteGPT</h1></center>', unsafe_allow_html=True)
        st.info("""
                Welcome to WebsiteGPT! This tool helps you create a website by interacting with an AI assistant. 
                Simply type your ideas or requirements in the chat, and let the assistant generate the website for you.
                Ready to create your website? Let's get started! 
                """)

def initialize_session_variables():

    if "html_generated" not in st.session_state:
        st.session_state["html_generated"] = False
    if "html_finalised" not in st.session_state:
        st.session_state["html_finalised"] = False
    if "domain_requested" not in st.session_state:
        st.session_state["domain_requested"] = False
    if "domain_available" not in st.session_state:
        st.session_state["domain_available"] = False
    if "domain_selected" not in st.session_state:
        st.session_state["domain_selected"] = False
    if "customer_data_collected" not in st.session_state:
        st.session_state["customer_data_collected"] = False


    if "form_toggle" not in st.session_state:
        st.session_state["form_toggle"] = False

    if "customer_info" not in st.session_state:
        st.session_state["customer_info"] = False

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hello! let's create a website together."}
        ]
    if "display_messages" not in st.session_state:
        st.session_state["display_messages"] = [
            {"role": "assistant", "content": "Hello! let's create a website together."}
        ]

def display_previous_messages():
        for msg in st.session_state.display_messages:
            st.chat_message(msg["role"]).write(msg["content"])

def define_user_input():

    if not st.session_state["html_generated"]:
        user_input = st.chat_input(max_chars=500, placeholder="Describe your website")
    
    elif st.session_state["html_generated"] and not st.session_state["html_finalised"]:
        user_input = st.chat_input(max_chars=500, placeholder="Let me know if you need any changes to the website or ask me to deploy it...")
    
    elif st.session_state["html_finalised"] and st.session_state["domain_requested"] and not st.session_state["domain_available"]:
        user_input = st.chat_input(max_chars=500, placeholder="Please enter a domain name...")
    
    elif st.session_state["domain_requested"] and not st.session_state["domain_available"]:
        user_input = st.chat_input(max_chars=500, placeholder="Please enter a different a domain name...")

    elif st.session_state["domain_available"]:
        user_input = st.chat_input(max_chars=500, placeholder="Yes or No")
    
    else:
        user_input = st.chat_input(max_chars=500)

























def generate_responses(template):
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=
                    [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages] 
                    + 
                    [{"role": "system", "content": generate_system_prompt(template)}]
            )
            return response




def github_push(GITHUB_KEY,html):
    repo_name = "mprajay999.github.io"
    file_name = "index.html"
    commit_message = "Replaced index.html with new content"

    # Read the new file content and encode it to base64
    content = base64.b64encode(html.encode('utf-8')).decode('utf-8')

    # Correct URL format for the GitHub API
    url = f"https://api.github.com/repos/mprajay999/{repo_name}/contents/{file_name}"

    headers = {
        "Authorization": "Bearer "+ GITHUB_KEY
    }

    # Fetch the current file's details to get the sha for replacement
    response_get = requests.get(url, headers=headers)

    if response_get.status_code == 200:
        # File exists, get the sha value for replacement
        file_info = response_get.json()
        sha = file_info['sha']
        
        # Prepare the data for the file replacement
        data = {
            "message": commit_message,
            "content": content,
            "sha": sha  # Include the sha to replace the file
        }
    elif response_get.status_code == 404:
        # If file doesn't exist, create a new one without sha
        data = {
            "message": commit_message,
            "content": content
        }
    else:
        #print(f"Failed to fetch file details: {response_get.status_code}, {response_get.text}")
        exit()

    # Send the PUT request to replace the file
    response = requests.put(url, headers=headers, json=data)

    # # Check if the file was successfully replaced
    # if response.status_code == 201:
    #     print("File replaced successfully!")
    # else:
    #     print(f"Failed to replace file: {response.status_code}, {response.text}")


def generate_image(alt_text):
    try:
        response = openai.Image.create(
            prompt=alt_text,
            n=1,
            size="1024x1024"
        )
        return response['data'][0]['url']
    except Exception as e:
        print(f"Error generating image for alt text '{alt_text}': {e}")
        return "error-placeholder.png"  # Fallback image URL

def replace_images_in_html(html_content):
    # Regex to find all <img> tags with an alt attribute
    img_tag_pattern = r'<img\s+[^>]*alt="([^"]+)"[^>]*>'
    
    image_count = 0  # Counter for the number of images processed
    max_images = 5   # Maximum number of images to generate
    
    # Function to process each match and replace src
    def replace_img_tag(match):
        nonlocal image_count
        if image_count >= max_images:
            return match.group(0)  # Return the original tag unchanged if limit is reached
        
        alt_text = match.group(1)  # Extract the alt text
        new_image_url = generate_image(alt_text)  # Generate a new image URL
        image_count += 1  # Increment the counter
        
        # Replace the old <img> tag with a new one, including the new src
        return re.sub(r'src="[^"]*"', f'src="{new_image_url}"', match.group(0))
    
    # Iterate through matches and apply replacements
    updated_html = re.sub(img_tag_pattern, replace_img_tag, html_content)
    return updated_html


import streamlit as st

