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
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

# Function to generate image descriptions using LLM
def generate_image_descriptions(image, prompt):
    """Send image and prompt to LLM to get descriptions."""
    
    # Convert the image to a byte array (Blob)
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format=image.format)
    img_byte_arr.seek(0)  # Go back to the start of the buffer

    # Prepare the input as content
    contents = [
        prompt,  # Pass the prompt as a simple string
        Image.open(img_byte_arr)  # Pass the image correctly as a PIL image
    ]

    # Generate response using the model
    response = model.generate_content(contents)

    # Extract the generated content text from the response
    
    generated_text = response.candidates[0].content.parts[0].text
    return generated_text

# Function to get prompt based on image type
def get_prompt(image_type):
    """Return the appropriate prompt based on the image type."""
    if image_type == "Product Image":
        return (           
           """**For the Short Description**:

            - Emphasize simplicity.
            - Focus only on the key elements. What this object is, if something that comes in different shapes (i.e. perfume bottle), function, material, color
            - Keep the short description to be 5 words maximum, but better to keep it 15 words
            - Avoid using too many details for the short description and focus only on the key attributes.
            - Example: A cordless vacuum with a light blue base and silver and gold handle

            **For the Long Description**:

            - Include all the specific details: the color of the products, material of the product,
              brand/manufacturer and any additional features.
            - Ensure it is includes details of the background, if the background include design descrice as well.
            - take note of the the text on the and the product itself, include it in the description.
            - Make this description detailed 
            - Do not describe it in a way to sell it, describe it in a way to help a machine learning model to understand what it looks like. Only include details that can be gathered from looking at the image, do not include details that would only be learned from the product description.
            - Any positioning should be based on your perspective looking at the image e.g. left, right"""
        )
    elif image_type == "Lifestyle Image":
        return ("""
            "I am working on a project that involves captioning two images: a product image and a lifestyle image showcasing the product in use. "
            "You are to provide a short and long caption for this image. Follow the guidelines below:\n\n"
            
            "For the Short Description of the lifestyle image:\n"
            "- Emphasize simplicity.\n"
            "- Focus on key elements like object, shape, function, material, and color.\n"
            "- 20-25 words maximum, but better to keep it 5-15 words.\n"
            "- Avoid using too many details for the short description.\n\n"
            
            "For the Long Description:"
            - Include all the specific details: the color of the products, material of the product,
              brand/manufacturer and any additional features.
            - Ensure it is includes details of the background, if the background include design descrice as well.
            - take note of the the text on the and the product itself, include it in the description.
            - Make this description detailed 
            - Do not describe it in a way to sell it, describe it in a way to help a machine learning model to understand what it looks like. Only include details that can be gathered from looking at the image, do not include details that would only be learned from the product description.
            - Any positioning should be based on your perspective looking at the image e.g. left, right
            "- Avoid describing feelings or emotions tied to the image.\n"
            "- Focus on positions like left, right, centered, etc.
            - note that you are to give full details of the product lifestyle image."""
        )
    return ""

# Streamlit app interface
def main():
    st.title("Image Caption Generator")

    # Image type selection
    image_type = st.selectbox("Select Image Type", ["Product Image", "Lifestyle Image"])

    # Upload image
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png", "webp"])
    
    if uploaded_image:
        # Display uploaded image
        image = Image.open(uploaded_image)
        st.image(image, caption='Uploaded Image', width=300)

        # Generate the appropriate prompt for the selected image type
        prompt = get_prompt(image_type)

        # Button to generate captions
        if st.button("Generate Description"):
            generated_text = generate_image_descriptions(image, prompt)
            st.write("**Generated Description:**", generated_text)

if __name__ == "__main__":
    main()
