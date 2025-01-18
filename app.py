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
    template1 = file.read()
with open("Templates/2.html", "r") as file:
    template2 = file.read()


def websitegpt_app():

    initialize_app()

    initialize_session_variables()
    
    display_previous_messages()

    if st.session_state["form_toggle"]:
        get_customer_details()


    if not st.session_state["template_info"]["industry"]:
        options = ["Restaurant",'Other Business']
        user_input = st.pills("industry", options, selection_mode="single",label_visibility = 'hidden')
        st.session_state["template_info"]["industry"] = user_input 

        if st.session_state["template_info"]["industry"] =='Restaurant':
            st.session_state["template_info"]["template"] = template1
        else:
            st.session_state["template_info"]["template"] = template2
       


    elif not st.session_state["template_info"]['sub_category']:
        if st.session_state["template_info"]["industry"] == 'Restaurant':
            options = ["Indian","Italian","American","Chinese","Korean","deploy"]
        else:
            options=["IT Consulting"]
        user_input = st.pills("sub category", options, selection_mode="single",label_visibility = 'hidden')
        st.session_state["template_info"]["sub_category"] = user_input  

    elif not st.session_state["html"]["generated"]:
        user_input = st.chat_input(max_chars=500, placeholder="Describe your website")

    elif not st.session_state["html"]["finalised"]:
        user_input = st.chat_input(max_chars=500, placeholder="Let me know if you need any changes or aks me to deploy it...")

    elif not st.session_state["domain"]["available"]:                                                         
        user_input = st.chat_input(max_chars=500, placeholder="Please enter your desired domain name without an extension...")

    elif not st.session_state["customer"]["info"]:
        options = [domain for domain in st.session_state["domain"]["available"]]
        user_input = st.pills("domain", options, selection_mode="single",label_visibility = 'hidden')

    else:
        user_input = st.chat_input(max_chars=500)


    if user_input:   

        st.chat_message("user",avatar="👤").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input}) 
        st.session_state.display_messages.append({"role": "user", "content": user_input})

        if not st.session_state["template_info"]["sub_category"]:  
            st.session_state.display_messages.append({"role": "assistant", "content": "Please select your sub category"})
            st.session_state.messages.append({"role": "assistant", "content": "Please select your sub category"})  


        elif not st.session_state["html"]["generated"]:

            with st.spinner('thinking...'):
                response = client.chat.completions.create(model="o1-preview",
                                                                messages=
                                                                [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages] 
                                                                + 
                                                                [{"role": "user", "content": generate_system_prompt(st.session_state["template_info"]["template"])}]
                                                                )

                assistant_response = response.choices[0].message.content
            
            if "```html" in assistant_response:

                with st.spinner("Creating Preview..."):

                    html_content = re.findall(r"```html(.*?)```", assistant_response, re.DOTALL)[0]
                    html_content = replace_images_in_html(html_content,client,UNSPLASH_API_KEY)

                    github_push(GITHUB_KEY, html_content)

                    github_url = "https://mprajay999.github.io/"

                    time.sleep(40)

                    st.session_state.display_messages.append(
                            {"role": "assistant", "content": f"Your website is ready! Check it out [here]({github_url}). Let me know if you need any changes or ask me to deploy it"}
                        )

                    st.session_state["html"]["generated"] = html_content

                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            else:
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                st.session_state.display_messages.append({"role": "assistant", "content": assistant_response})



        elif not st.session_state["html"]["finalised"]:  

            if 'deploy' in user_input.lower():
                st.session_state["html"]["finalised"] = True
                st.session_state.display_messages.append(
                        {"role": "assistant", "content": "Great! Let's deploy your website. Please provide your desired domain name."}
                        )
            
            else:

                with st.spinner("thinking..."):

                    response = client.chat.completions.create(model="o1-preview",
                                                                messages = [{
                                                                                "role": "user",
                                                                                "content": f"Make changes to the code; {user_input} ; output full html code ; {st.session_state['html']['generated']}"
                                                                            }])

                    assistant_response = response.choices[0].message.content
                    print(assistant_response)

                with st.spinner("Creating Preview..."):

                    html_content = re.findall(r"```html(.*?)```", assistant_response, re.DOTALL)[0]

                    github_push(GITHUB_KEY, html_content)
                    github_url = "https://mprajay999.github.io/"

                    time.sleep(40)

                    st.session_state.display_messages.append(
                                {"role": "assistant", "content": f"Your website is ready again! Check it out [here]({github_url}). Let me know if you need any changes or ask me to deploy it"}
                            )

                    st.session_state["html"]["generated"] = html_content

                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})


        elif not st.session_state["domain"]["available"]:
            response = client.chat.completions.create(
                                                        model="gpt-4o",  # Ensure the model name is correct
                                                        messages=[
                                                            {"role": "system", "content": "You are helping a customer buy a domain."},
                                                            {"role": "user", "content": "Return a string for this domain, focusing on .com, .net, .org, .co and its close alternatives to check for availability. You include variations in name and word additions that do not change the overall meaning. The result should be similar to GoDaddy domain search suggestions. Just return the string in CSV, not the variable." + user_input}
                                                        ]
                                                    )
            
            assistant_response = response.choices[0].message.content.split(',')

            with st.spinner("Checking Availability..."):

                domain_availability = check_domains_availability(OPEN_PROVIDER_KEY, assistant_response)
                if domain_availability:
                    available_domains = [domain for domain in domain_availability]

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

