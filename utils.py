import requests
import base64
import streamlit as st
import re
import streamlit.components.v1 as components

def initialize_app():
    st.set_page_config(
        page_title='WebsiteGPT',
        page_icon='🤖',
        #layout="wide",
        initial_sidebar_state='collapsed',
    )


    st.title("Let’s bring your business to life!")
    st.markdown("""
                WebsiteGPT is your AI-powered assistant to create and deploy stunning websites effortlessly. 🚀
                
                """)
    with st.sidebar:
        st.markdown('<center><h1>WebsiteGPT</h1></center>', unsafe_allow_html=True)
        #components.iframe("https://mprajay999.github.io/")
        st.info("""
                Welcome to WebsiteGPT! This tool helps you create a website by interacting with an AI assistant. 
                Simply type your ideas or requirements in the chat, and let the assistant generate the website for you.
                Ready to create your website? Let's get started! 
                """)

def initialize_session_variables():


    if "form_toggle" not in st.session_state:
        st.session_state["form_toggle"] = False

    if "assistant_last_message" not in st.session_state:
        st.session_state["assistant_last_message"] = False

    if "template_info" not in st.session_state:
        st.session_state["template_info"] = {
                                                "industry": False,
                                                "sub_category" : False,
                                                "template" : False
                                             }
    
    if "html" not in st.session_state:
        st.session_state["html"] = {
                                                "generated": False
                                             }
    if "domain" not in st.session_state:
        st.session_state["domain"] = {
                                                "requested": False,
                                                "available": False,
                                                "selected": False
                                             }
    if "customer" not in st.session_state:
        st.session_state["customer"] = {
                                                "info": False,
                                                "id": False,
                                             }

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hello! let's create a website together, Can you please let me know the industry your business is in?"}
        ]
    if "display_messages" not in st.session_state:
        st.session_state["display_messages"] = [
            {"role": "assistant", "content": "Hello! let's create a website together, Can you please let me know the industry your business is in?"}
        ]

import time

def display_previous_messages():
    # Display all previous messages normally (except the last one)
    #print(st.session_state.display_messages)
    for msg in st.session_state.display_messages[:-1]:  # Exclude the last message for streaming
        if msg["role"] =='assistant':
            st.chat_message(msg["role"],avatar="🤖").write(msg["content"])
        else:
            st.chat_message(msg["role"],avatar="👤").write(msg["content"])

    # Stream the last assistant message with a delay (ensure it's displayed as "assistant")
    def stream_last_assistant_message():
        last_assistant_message = st.session_state.display_messages[-1]  # Directly access the last message
        if last_assistant_message["role"] == "assistant" and st.session_state["assistant_last_message"] !=last_assistant_message :
            # Split the message content into words
            st.session_state["assistant_last_message"] =last_assistant_message
            words = last_assistant_message["content"].split(" ")
            for word in words:
                yield word + " "  # Yield each word with a space
                time.sleep(0.05)  # Add a slight delay to simulate typing

    # Use st.chat_message("assistant") to ensure the role is set as "assistant"
    with st.chat_message("assistant",avatar="🤖"):
        st.write_stream(stream_last_assistant_message)






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