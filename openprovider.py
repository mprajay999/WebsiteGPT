import requests
import streamlit as st

def authenticate_user(username, password, ip="0.0.0.0"):
    url = "https://api.openprovider.eu/v1beta/auth/login"
    payload = {
        "username": username,
        "password": password,
        "ip": ip
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            token = data["data"]["token"]
            return token
        else:
            error_message = f"Error: {response.status_code}, {response.text}"
            print(error_message)
            return error_message
    except Exception as e:
        print(f"An error occurred: {e}")
        return str(e)
    

def check_domains_availability(auth_token, domains, with_price=True, batch_size=10):
    url = "https://api.openprovider.eu/v1beta/domains/check"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }
    # Split domains into batches
    batches = [domains[i:i + batch_size] for i in range(0, len(domains), batch_size)]
    available_domains = []

    for batch in batches:
        domain_objects = [
            {"extension": domain.split('.')[-1], "name": '.'.join(domain.split('.')[:-1])}
            for domain in batch
        ]
        payload = {
            "domains": domain_objects,
            "with_price": with_price
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json().get("data", {}).get("results", [])

            for result in results:
                domain = result.get("domain")
                status = result.get("status")
                price = result.get("price", {}).get("product", {}).get("price", "N/A")
                if status == "free":
                    available_domains.append((domain, status, price))

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - {response.text}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred- {req_err}")

    return available_domains

    

@st.dialog("Get Customer Details")
def get_customer_details():
    with st.form("customer_form"):
        st.write("Please fill in the customer details:")
        
        # Collecting customer name details
        first_name = st.text_input("First Name", "")
        last_name = st.text_input("Last Name", "")
        initials = st.text_input("Initials", "")
        prefix = st.text_input("Prefix", "")
        # Collecting address details
        street = st.text_input("Street", "")
        number = st.text_input("Street Number", "")
        city = st.text_input("City", "")
        zipcode = st.text_input("Zip Code", "")
        state = st.text_input("State", "")
        country = st.text_input("Country", "")
        
        # Collecting phone details
        phone_country_code = st.text_input("Phone Country Code", "")
        phone_area_code = st.text_input("Phone Area Code", "")
        phone_subscriber_number = st.text_input("Phone Subscriber Number", "")
        
        # Collecting email
        email = st.text_input("Email", "")
        
        submitted = st.form_submit_button("Submit")
        if submitted:
            customer_data ={
                            "name": {
                                "first_name": first_name,
                                "last_name": last_name,
                                "full_name": first_name+" "+last_name,
                                "initials": initials,
                                "prefix": prefix
                            },
                            "address": {
                                "street": street,
                                "number": number,
                                "city": city,
                                "zipcode": zipcode,
                                "state": state,
                                "country": country
                            },
                            "phone": {
                                "country_code": phone_country_code,
                                "area_code": phone_area_code,
                                "subscriber_number": phone_subscriber_number
                            },
                            "email": email
                        }
        
            st.session_state["customer"]["info"] = customer_data
            st.session_state["form_toggle"] = False
            st.success(f"Please close this window to proceed")



def create_customer(api_token, customer_data):
    base_url = "https://api.openprovider.eu/v1beta/"
    url = f"{base_url}customers"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Send POST request to create the customer
    response = requests.post(url, headers=headers, json=customer_data)

    if response.status_code == 200:
        # Parse the response to get the customer handle
        customer_data = response.json()
        customer_handle = customer_data['data']['handle']
        return customer_handle
    else:
        # Return the error message if request fails
        return f"Error: {response.status_code} - {response.text}"




def register_domain(api_token, owner_handle, admin_handle, tech_handle, domain_name, extension, period=1, name_servers=None, autorenew="default"):
    """
    Registers a domain in OpenProvider.

    Parameters:
        api_token (str): The API token for authentication.
        owner_handle (str): The handle of the customer who will be the domain owner.
        admin_handle (str): The handle of the customer who will be the domain admin.
        tech_handle (str): The handle of the customer who will be the domain tech contact.
        domain_name (str): The domain name to register.
        extension (str): The domain extension (e.g., 'com', 'info').
        period (int): The period to register the domain (default is 1 year).
        name_servers (list): A list of name servers to assign to the domain (optional).
        autorenew (str): Auto-renew setting ('on', 'off', 'default').

    Returns:
        dict: The API response, including domain registration status and other details.
    """
    base_url = "https://api.openprovider.eu/v1beta/"
    url = f"{base_url}domains"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    # Prepare the domain registration data
    data = {
        "owner_handle": owner_handle,
        "admin_handle": admin_handle,
        "tech_handle": tech_handle,
        "domain": {
            "name": domain_name,
            "extension": extension
        },
        "period": period,
        "autorenew": autorenew
    }

    # Add optional name servers if provided
    if name_servers:
        data["name_servers"] = [{"name": ns} for ns in name_servers]

    # Send POST request to register the domain
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        # Return the response data if successful
        return response.json()
    else:
        # Return the error message if request fails
        return {
            "error": f"Error: {response.status_code} - {response.text}"
        }

