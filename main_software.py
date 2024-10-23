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
model = genai.GenerativeModel("models/gemini-1.5-pro-002")

# Predefined password (You can store this securely in an environment variable)
APP_PASSWORD = os.getenv("APP_PASSWORD")  # Load password from environment variables

# Function to download and convert image from URL to a PIL image
def download_image_from_url(image_url):
    """Downloads image from a URL and converts it to a PIL image."""
    response = requests.get(image_url)
    img = Image.open(io.BytesIO(response.content))
    return img

# Function to convert PIL image to a byte array (Blob)
def image_to_byte_array(image):
    """Converts a PIL image to a byte array (Blob)."""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr.seek(0)
    return img_byte_arr

# Function to generate image descriptions using LLM
def generate_image_descriptions(image, prompt):
    """Send image and prompt to LLM to get descriptions."""
    try:
        # Convert the image to a byte array (Blob)
        img_byte_arr = image_to_byte_array(image)

        # Prepare the input as content
        contents = [
            prompt,  # Pass the prompt as a simple string
            image  # Pass the image as a PIL image
        ]

        # Generate response using the model
        response = model.generate_content(contents)

        # Extract the generated content text from the response
        generated_text = response.candidates[0].content.parts[0].text
        return generated_text
    except Exception as e:
        return "Usage limit reached"

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
            - Describe the background of the image including any artistic or design elements.
            - Include any text present on the image or the product itself.
            - Avoid promotional language and focus on objective description for machine learning understanding.
            - Limit details to those observable in the image, excluding information only available from product descriptions.
            - Any positioning should be based on your perspective looking at the image e.g. left, right
            - Ensure you pay attention to the position of the product in the image and include the detail in the description
            - Finally, ensure you include every detail in the image.
            """
        )
    elif image_type == "Lifestyle Image":
        return ("""  For the Short Description of the Lifestyle Image:

                    Emphasize simplicity and conciseness.
                    Focus on key elements: object, shape, function, material, and color.
                    Ensure you keep the description between 8 to 15 words but ensure is under 15 words.
                    Avoid excessive detail and focus on core attributes.
                    Example: "Person using a blue laptop at a cafe."
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
                    - Ensure you pay attention to the position of the product in the image and include the detail in the description 
                    - if the person in the image is holding any object consider the positioning of the object held in terms of whether right or left.
                    - Finally, ensure you include every detail in the image.
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
        st.error("Incorrect password. Please check your password and try again.")

# Streamlit app interface
def main():
    st.title("SBX Image Caption Generator")

        # Instructional Dropdown
    with st.expander("ℹ️ How to Use the App", expanded=False):
        st.write("""
        1. Select the appropriate image type (Product or Lifestyle).
        2. Upload Image or Use URL: Either upload an image file or provide an image URL.
        3. Click 'Generate Description' to generate an image description.
        4. Edit the description in the provided text box.
        5. Copy and paste the edited description into the Grammar Correction Tool for necessary corrections.
        6. Finally, click 'Correct Grammar' and copy the corrected text for your use.
        
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

     # Check if the user is already logged in
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    # If logged in, show the main app
    if st.session_state["logged_in"]:
        # Image type selection before upload or URL
        image_type = st.selectbox("Select Image Type", ["Product Image", "Lifestyle Image"])

        # Create two columns for image upload and URL
        col1, col2 = st.columns(2)

        # Initialize image variable
        image = None

        # Column 1: Upload Image
        with col1:
            st.subheader("Upload Image")
            uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])
            if uploaded_image:
                image = Image.open(uploaded_image)
                st.image(image, caption='Uploaded Image', width=300)

        # Column 2: Use Image URL
        with col2:
            st.subheader("Use Image URL")
            image_url = st.text_input("Enter Image URL")
            if image_url:
                try:
                    image = download_image_from_url(image_url)
                    st.image(image, caption='Image from URL', width=250)
                except Exception as e:
                    st.error(f"Error loading image: {str(e)}")

        # Only generate the description if an image is available
        if image:
            # Generate the appropriate prompt for the selected image type
            prompt = get_prompt(image_type)

            # Button to generate captions
            if st.button("Generate Description"):
                generated_text = generate_image_descriptions(image, prompt)
                if generated_text == "Usage limit reached":
                    st.error("Usage limit reached. Please try again later.")
                else:
                    st.write("**Generated Description:**", generated_text)
    else:
        st.warning("Please log in to use the application.")

if __name__ == "__main__":
    main()
