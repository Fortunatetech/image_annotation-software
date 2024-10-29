import streamlit as st
from PIL import Image
import io
import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash-002")

# Predefined password
APP_PASSWORD = os.getenv("APP_PASSWORD")  # Load password from environment variables

# Function to download and convert image from URL to a PIL image
def download_image_from_url(image_url):
    """Downloads image from a URL and converts it to a PIL image."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(image_url, headers=headers)
        response.raise_for_status()  # Raise an error for invalid URLs
        img = Image.open(io.BytesIO(response.content))
        return img
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred: {http_err}")
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
    return None


# Function to generate image descriptions using LLM
def generate_image_descriptions(image, prompt):
    """Send image and prompt to LLM to get descriptions."""
    try:
        response = model.generate_content([prompt, image])
        generated_text = response.candidates[0].content.parts[0].text
        return generated_text
    except Exception as e:
        return "Usage limit reached or an error occurred."

# Function to get prompt based on image type
def get_prompt(image_type):
    """Return the appropriate prompt based on the image type."""
    if image_type == "Product Image":
        return (           
           """**For the Short Description:**

            - Emphasize simplicity and conciseness.
            - Focus on the essential elements: the object's identity, shape (if applicable), function, material, and color.
            - Ensure you keep the description between 8 to 15 words but ensure is under 15 words.
            - Avoid excessive detail and focus on the core attributes.
            - Example: "Cordless vacuum, light blue base, silver-gold handle."

            **For the Long Description:**

            - Provide comprehensive details, including color, material, brand or manufacturer, and additional features.
            - Note: Ensure you don not include background of the image including any artistic or design elements.
            - Include any text present on the image or the product itself.
            - Avoid promotional language and focus on objective description for machine learning understanding.
            - Limit details to those observable in the image, excluding information only available from product descriptions.
            - Any positioning should be based on your perspective looking at the image e.g. left, right
            - Ensure you pay attention to the position of the product in the image and include the detail in the decription
            - Finally, ensure you include every details in the image.
            """
        )
    elif image_type == "Lifestyle Image":
        return (""" 
                Note: focus only on long description for lifestyle image!

                    For the Long Description:

                    Provide comprehensive details, including colors, materials, brands, and features.
                    Describe the background if it contains design elements.
                    Include any text present on the image or the product.
                    Avoid promotional language and focus on objective description for machine learning.
                    Limit details to those observable in the image, excluding information from product descriptions.
                    Use a consistent perspective (e.g., left, right) for positioning.
                    Avoid describing feelings or emotions tied to the image.
                    Focus on positions like left, right, centered, etc.
                    Provide detailed descriptions of the person using the product, including color, hairstyle, posture, etc.
                    Ensure the description fully captures the lifestyle context of the image.
                    Any positioning should be based on your perspective looking at the image e.g. left, right
                    - Ensure you pay attention to the position of the product in the image and include the detail in the decription 
                    - if the person in the image is holding any object consider the positioning of the object held interm of wheher rigth or left.
                    - Finally, ensure you include every details in the image.
                 """
        )
    return ""

# Function to verify user login
def login(password_input):
    """Simple function to verify the password."""
    if password_input == APP_PASSWORD:
        st.session_state["logged_in"] = True
        st.success("Login successful! You can now use the app.")
    else:
        st.error("Incorrect password. Please try again.")

# Streamlit app interface
def main():
    st.title("SBX Image Caption Generator")

    # Instructional Dropdown
    with st.expander("ℹ️ How to Use the App", expanded=False):
        st.write("""
        1. Input the **Product Image URL** in the first column and **Lifestyle Image URL** in the second column.
        2. Click the 'Generate Description' button to generate an image description.
        3. Edit the generated description in the text box if necessary and copy it for your use.
                 
        **Note:**
        1. The Image Caption Tool may not support sensitive images.
        2. If the usage limit is reached, an error message will be displayed.
        """)

    # Sidebar for login
    with st.sidebar:
        st.subheader("Login")
        password_input = st.text_input("Enter the application password:", type="password")
        if st.button("Login"):
            login(password_input)

    # Check if the user is logged in
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        # Initialize session state variables for persistence
        if "product_description" not in st.session_state:
            st.session_state["product_description"] = ""
        if "lifestyle_description" not in st.session_state:
            st.session_state["lifestyle_description"] = ""

        # Create two columns for product and lifestyle image URLs
        col1, col2 = st.columns([1, 1], gap="large")

        # Column 1: Product Image Section
        with col1:
            st.subheader("Product Image")
            product_url = st.text_input("Enter Product Image URL")

            if product_url:
                try:
                    product_image = download_image_from_url(product_url)
                    st.image(product_image, caption='Product Image', width=300)

                    if st.button("Generate Product Description"):
                        prompt = get_prompt("Product Image")
                        st.session_state["product_description"] = generate_image_descriptions(product_image, prompt)

                except Exception as e:
                    st.error(f"Error loading product image: {str(e)}")

            # Display product description with persistence
            st.text_area("Product Description", st.session_state["product_description"], height=150)

        # Column 2: Lifestyle Image Section
        with col2:
            st.subheader("Lifestyle Image")
            lifestyle_url = st.text_input("Enter Lifestyle Image URL")

            if lifestyle_url:
                try:
                    lifestyle_image = download_image_from_url(lifestyle_url)
                    st.image(lifestyle_image, caption='Lifestyle Image', width=300)

                    if st.button("Generate Lifestyle Description"):
                        prompt = get_prompt("Lifestyle Image")
                        st.session_state["lifestyle_description"] = generate_image_descriptions(lifestyle_image, prompt)

                except Exception as e:
                    st.error(f"Error loading lifestyle image: {str(e)}")

            # Display lifestyle description with persistence
            st.text_area("Lifestyle Description", st.session_state["lifestyle_description"], height=150)

    else:
        st.warning("Please log in to use the application.")

if __name__ == "__main__":
    main()
