import streamlit as st
import psycopg2
from io import BytesIO
import io
from PIL import Image
import PyPDF2

# Function to initialize the database connection
@st.cache_resource
def init_connection():
    conn = psycopg2.connect(
        host=st.secrets["postgresql"]["host"],
        port=st.secrets["postgresql"]["port"],
        dbname=st.secrets["postgresql"]["database"],
        user=st.secrets["postgresql"]["username"],
        password=st.secrets["postgresql"]["password"]
    )
    conn.autocommit = True  # Enable autocommit mode
    return conn

conn = init_connection()

def create_table():
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uploaded_files (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                filedata BYTEA NOT NULL,
                filetype TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.close()
    except Exception as e:
        st.error(f"Error creating table: {e}")

# Call the function to create the table
create_table()

# Function to upload file to the database
def upload_file_to_db(file, file_type):
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO uploaded_files (filename, filedata, filetype) VALUES (%s, %s, %s)",
            (file.name, file.read(), file_type)
        )
        cursor.close()
        st.success(f"File '{file.name}' uploaded successfully!")
    except Exception as e:
        st.error(f"Error uploading file: {e}")

# Function to display uploaded file content
def display_file(file, file_type):
    if file_type in ['pdf']:
        # Read PDF file and display the first page
        pdf_reader = PyPDF2.PdfReader(file)
        page = pdf_reader.pages[0]
        st.write("PDF Content:")
        st.write(page.extract_text())
    elif file_type in ['jpg', 'jpeg', 'png']:
        # Read image file and display
        image = Image.open(file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
    else:
        st.error("Unsupported file format")

# Streamlit UI
st.title("Upload Aadhaar and PAN Card")

st.sidebar.title("Welcome to Sidebar")

page = st.sidebar.radio("Go To", ["Home", "About", "Contact"])

if page == 'Home':
    st.subheader("Welcome to Homepage")

    aadhaar_file = st.file_uploader("Upload Aadhaar Card", type=['pdf', 'jpg', 'jpeg', 'png'])
    pan_file = st.file_uploader("Upload PAN Card", type=['pdf', 'jpg', 'jpeg', 'png'])

    if aadhaar_file is not None:
        aadhaar_file_type = aadhaar_file.name.split('.')[-1].lower()
        st.write("Aadhaar Card:")
        display_file(aadhaar_file, aadhaar_file_type)
        upload_file_to_db(aadhaar_file, aadhaar_file_type)  # Call this function to upload the file

    if pan_file is not None:
        pan_file_type = pan_file.name.split('.')[-1].lower()
        st.write("PAN Card:")
        display_file(pan_file, pan_file_type)
        upload_file_to_db(pan_file, pan_file_type)  # Call this function to upload the file

elif page == 'About':
    st.subheader("It is mandatory work")
elif page == 'Contact':
    st.subheader("Contact - Catnip Infotech")
