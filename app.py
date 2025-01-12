import streamlit as st
import re
from prompt import generate_system_prompt
from utils import *
from openprovider import *
from unsplash import *
from openai import OpenAI

OPENAI_KEY = st.secrets["OPENAI_API_KEY"]
GITHUB_KEY = st.secrets["GITHUB_KEY"]
OPEN_PROVIDER_KEY = st.secrets["OPEN_PROVIDER_KEY"]
UNSPLASH_API_KEY = st.secrets["UNSPLASH_API_KEY"]


client = OpenAI(api_key=OPENAI_KEY)

with open("Templates/1.html", "r") as file:
    template = file.read()


def websitegpt_app():

    initialize_app()

    initialize_session_variables()

    display_previous_messages()

    if st.session_state["form_toggle"]:
        get_customer_details()


    if not st.session_state["template_info"]["industry"]:
        options = ["Restaurant"]
        user_input = st.pills("industry", options, selection_mode="single",label_visibility = 'hidden')
        st.session_state["template_info"]["industry"] = user_input 

    elif not st.session_state["template_info"]['sub_category']:
        options = ["Indian","Italian","American","Chinese","Korean"]
        user_input = st.pills("sub category", options, selection_mode="single",label_visibility = 'hidden')
        st.session_state["template_info"]["sub_category"] = user_input   

    elif not st.session_state["html"]["generated"]:
        user_input = st.chat_input(max_chars=500, placeholder="Describe your website")

    elif not st.session_state["domain"]["requested"]:
        options = ["Deploy"]
        user_input = st.pills("Please select from the following options", options, selection_mode="single",label_visibility = 'hidden')

    elif not st.session_state["domain"]["available"]:                                                         
        user_input = st.chat_input(max_chars=500, placeholder="Please enter your desired domain name without an extension...")

    elif not st.session_state["customer"]["info"]:
        options = [domain for domain in st.session_state["domain"]["available"]]
        user_input = st.pills("domain", options, selection_mode="single",label_visibility = 'hidden')

    else:
        user_input = st.chat_input(max_chars=500)


    if user_input:        

        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input}) 
        st.session_state.display_messages.append({"role": "user", "content": user_input})


        if not st.session_state["template_info"]["sub category"]:  
            st.session_state.display_messages.append({"role": "assistant", "content": "Please select your sub category"})
            st.session_state.messages.append({"role": "assistant", "content": "Please select your sub category"})


        elif not st.session_state["html"]["generated"]:

            with st.spinner("Generating..."):

                response = client.chat.completions.create(model="gpt-4o",
                                                            messages=
                                                            [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages] 
                                                            + 
                                                            [{"role": "system", "content": generate_system_prompt(template)}]
                                                            )

                assistant_response = response.choices[0].message.content

                if "```html" in assistant_response:
                    html_content = re.findall(r"```html(.*?)```", assistant_response, re.DOTALL)[0]
                    html_content = replace_images_in_html(html_content,client,UNSPLASH_API_KEY)
                    
                    github_push(GITHUB_KEY, html_content)

                    github_url = "https://mprajay999.github.io/"
                    st.session_state.display_messages.append(
                        {"role": "assistant", "content": f"Your website is ready! Check it out [here]({github_url}). Let me know if you need any changes or ask me to deploy it"}
                    )

                    st.session_state["html"]["generated"] = html_content
                else:
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    st.session_state.display_messages.append({"role": "assistant", "content": assistant_response})



        elif not st.session_state["domain"]["requested"]:
            with st.spinner("Finalising..."):
                st.session_state["domain"]["requested"] = True
                st.session_state.display_messages.append(
                    {"role": "assistant", "content": "Great! Let's deploy your website. Please provide your desired domain name."}

                )

        elif not st.session_state["domain"]["available"]:
            with st.spinner("Checking Availability..."):
                domain_availability = check_domain_availability(OPEN_PROVIDER_KEY, user_input)
                if domain_availability:
                    available_domains = [domain for domain in domain_availability if domain[1] == 'free']

                    if available_domains:

                        message = "The following domain names are available:\n\n"
                        for domain in available_domains:
                            domain_name, status, price = domain
                            message += f"🔹 **{domain_name}** - Price: {price}$ \n\n"

                        message += "\nWhich domain would you like to proceed with?"

                        st.session_state.display_messages.append({
                                "role": "assistant",
                                "content": message
                            })
                        
                        st.session_state["domain"]["available"] = [domain[0] for domain in available_domains]

                    else:
                        st.session_state.display_messages.append({
                            "role": "assistant",
                            "content": "The domain name is not available. Please try a different domain name."
                        })
                else:
                    st.session_state.display_messages.append({
                        "role": "assistant",
                        "content": "There was an error checking domain availability. Please try again later."
                    })


        elif  not st.session_state["customer"]["info"] :
            with st.spinner("Registering the domain..."):
                    st.session_state["domain"]["selected"]=user_input
                    st.session_state["form_toggle"] = True
                    st.session_state["customer"]["info"] = True
                    st.session_state.display_messages.append({"role": "assistant", "content": "enter any text to continue"})
                    

        elif st.session_state["customer"]["info"]:
            customer_id = create_customer(OPEN_PROVIDER_KEY,st.session_state["customer"]["info"])
            st.session_state["customer"]["id"]  = customer_id

            st.session_state.display_messages.append({"role": "assistant", "content": f"your customer id is {customer_id} "})



        st.rerun()
        
websitegpt_app()

