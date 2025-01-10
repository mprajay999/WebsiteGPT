import psycopg2
import config
import streamlit as st

def fetch_templates():
    try:
        conn = psycopg2.connect(
            dbname=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=config.DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM templates")
        templates = cursor.fetchall()
        cursor.close()
        conn.close()
        return {template[0]: template[1] for template in templates}
    except Exception as e:
        st.error("Error fetching templates from the database.")
        return {}
print(fetch_templates)