import streamlit as st
import re
from prompt import generate_system_prompt
from utils import *
from openprovider import *
from openai import OpenAI



OPENAI_KEY = st.secrets["OPENAI_API_KEY"]
GITHUB_KEY = st.secrets["GITHUB_KEY"]
OPEN_PROVIDER_KEY = st.secrets["OPEN_PROVIDER_KEY"]

client = OpenAI(api_key=OPENAI_KEY)

with open("Templates/1.html", "r") as file:
    template = file.read()
with open("Templates/2.html", "r") as file:
    template2 = file.read()



def websitegpt_app():

    initialize_app()

    initialize_session_variables()

    display_previous_messages()

    if st.session_state["form_toggle"]:
        get_customer_details()

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




    if user_input:



        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.display_messages.append({"role": "user", "content": user_input})




        if 'deploy' in user_input.lower() and st.session_state["html_generated"]:
            with st.spinner("Finalising..."):
                st.session_state["html_finalised"] = True
                st.session_state["domain_requested"] = True
                st.session_state.display_messages.append(
                    {"role": "assistant", "content": "Great! Let's deploy your website. Please provide your desired domain name."}
                )




        elif st.session_state["domain_requested"] and not st.session_state["domain_available"]:
            with st.spinner("Checking Availability..."):
                domain_availability = check_domain_availability(OPEN_PROVIDER_KEY, user_input)
                if domain_availability:
                    available_domains = [domain for domain in domain_availability if domain[1] == 'free']

                    if available_domains:
                        # Handle single domain scenario
                        if len(available_domains) == 1:
                            domain_name, status, price = available_domains[0]
                            st.session_state.display_messages.append({
                                "role": "assistant",
                                "content": f"The price of **{domain_name}** is {price}. Shall we proceed?"
                            })
                            st.session_state["domain_available"] = True
                        else:
                            # Handle multiple domains scenario
                            message = "The following domain names are available:\n\n"
                            for domain in available_domains:
                                domain_name, status, price = domain
                                message += f"🔹 **{domain_name}** - Price: {price}$ \n\n"

                            message += "\nWhich domain would you like to proceed with?"

                            st.session_state.display_messages.append({
                                "role": "assistant",
                                "content": message
                            })

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




        elif st.session_state['customer_data_collected']:
            customer_id = create_customer(OPEN_PROVIDER_KEY,st.session_state['customer_data'])
            st.session_state["customer_id"]  = customer_id

            st.session_state.display_messages.append({"role": "assistant", "content": f"your customer id is {customer_id} "})



        elif  st.session_state["domain_available"] :
            with st.spinner("Registering the domain..."):
                if 'yes' in user_input.lower():
                    st.session_state["form_toggle"] = True
                    st.session_state.display_messages.append({"role": "assistant", "content": "enter any text to continue"})

                else:
                    st.session_state.display_messages.append({"role": "assistant", "content": "thanks for using websitegpt, hope to see you soon"})





        elif not st.session_state["html_finalised"]:
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
                    html_content = replace_images_in_html(html_content,client)
                    st.session_state["html_generated"] = True
                    github_push(GITHUB_KEY, html_content)

                    github_url = "https://mprajay999.github.io/"
                    st.session_state.display_messages.append(
                        {"role": "assistant", "content": f"Your website is ready! Check it out [here]({github_url}). Let me know if you need any changes or ask me to deploy it"}
                    )
                else:
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                    st.session_state.display_messages.append({"role": "assistant", "content": assistant_response})



        st.rerun()

websitegpt_app()

