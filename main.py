import streamlit as st
from PIL import Image
import io
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google API Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the Gemini model
model = genai.GenerativeModel("models/gemini-1.5-pro-002")

# Function to generate image descriptions using LLM
def generate_image_descriptions(image, prompt):
    try:
        # Convert the image to a byte array (Blob)
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format)
        img_byte_arr.seek(0)

        # Prepare the input as content
        contents = [
            prompt,
            Image.open(img_byte_arr)
        ]

        # Generate response using the model
        response = model.generate_content(contents)

        # Extract the generated content text from the response
        generated_text = response.candidates[0].content.parts[0].text
        return generated_text
    except Exception as e:
        return "Error: The image you uploaded is sensitive or the usage limit has been reached. Please try again later."

# Function to correct grammar using LLM
def correct_grammar(input_text, prompt):
    try:
        contents = [
            prompt,
            input_text
        ]

        # Generate response using the model
        response = model.generate_content(contents)

        # Extract the corrected text from the response
        corrected_text = response.candidates[0].content.parts[0].text
        return corrected_text
    except Exception as e:
        return "Error: Could not process the text. Please try again later."

# Function to generate the prompt for image descriptions
def get_image_description_prompt(image_type):
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
            - Ensure you pay attention to the position of the product in the image and include the detail in the decription
            - Finally, ensure you include every details in the image.
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
                    - Ensure you pay attention to the position of the product in the image and include the detail in the decription 
                    - if the person in the image is holding any object consider the positioning of the object held interm of wheher rigth or left.
                    - Finally, ensure you include every details in the image.
                 """
        )
    return ""

# Function to generate the prompt for grammar correction
def get_grammar_prompt():
    """Return an advanced prompt for correcting and enhancing image descriptions."""
    return (
        "Correct the grammar, punctuation, and spelling in the following image description. "
        "ensure you changed British English to American English"
        "Ensure that the text is clear, concise, and accurately describes the key details of the image. "
        "Improve the sentence flow, eliminate redundancy, and ensure that the tone is professional. "
        "Where necessary, add specific image-related details to enhance the description's accuracy. "
        "Ensure the description remains simple yet vivid, suitable for machine learning and accessibility purposes. "
        "Avoid any subjective interpretation and focus on factual, observable elements."
    )

# Streamlit app interface
def main():
    st.set_page_config(page_title="🚀 AY AI Powerhouse: Image Descriptions & Grammar Correction", layout="wide")

    st.title("🚀 AY AI Powerhouse: Image Descriptions & Grammar Correction")

    # Instructional Dropdown
    with st.expander("ℹ️ How to Use the App", expanded=False):
        st.write("""
        1. Upload or drag in an image.
        2. Select the appropriate image type (Product or Lifestyle).
        3. Click 'Generate Description' to generate an image description.
        4. Edit the description in the provided text box.
        5. Copy and paste the edited description into the Grammar Correction Tool for necessary corrections.
        6. Finally, click 'Correct Grammar' and copy the corrected text for your use.
        
        **Note:** The Image Caption Tool may not support sensitive images.
        """)

    # Create two columns for Image Description and Grammar Correction tools
    col1, col2 = st.columns(2)

    # Column 1: Image Description Generator
    with col1:
        st.header("🖼️ Image Caption Generator")
        
        # Image type selection
        image_type = st.selectbox("Select Image Type", ["Product Image", "Lifestyle Image"])

        # Upload image
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])

        if uploaded_image:
            # Display uploaded image
            image = Image.open(uploaded_image)
            st.image(image, caption='Uploaded Image', width=300)

            # Generate the appropriate prompt for the selected image type
            prompt = get_image_description_prompt(image_type)

            # Button to generate descriptions
            if st.button("Generate Description"):
                generated_text = generate_image_descriptions(image, prompt)
                st.text_area("Generated Description (Editable)", value=generated_text, height=150)

    # Column 2: Grammar Correction Tool
    with col2:
        st.header("📝 Grammar Correction Tool")

        # Text input
        user_input = st.text_area("Enter the text that you want to correct:")

        # Generate the prompt for grammar correction
        prompt = get_grammar_prompt()

        # Button to generate corrected text
        if st.button("Correct Grammar"):
            if user_input:
                corrected_text = correct_grammar(user_input, prompt)
                st.text_area("Corrected Text (Editable)", value=corrected_text, height=150)
            else:
                st.write("Please enter text to correct.")

if __name__ == "__main__":
    main()
