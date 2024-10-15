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
    if response and response.result and response.result.candidates:
        generated_text = response.result.candidates[0].content.parts[0].text
    else:
        generated_text = "No description generated."

    return generated_text

# Function to get prompt based on image type
def get_prompt(image_type):
    """Return the appropriate prompt based on the image type."""
    if image_type == "Product Image":
        return (
            "I am working on a project that involves captioning product images. "
            "You are to provide a short and long caption for this image. Here are the guidelines:\n\n"
            
            "For the Short Description of the product:\n"
            "- Emphasize simplicity.\n"
            "- Focus on key elements like object, shape, function, material, and color.\n"
            "- 5-15 words (20-25 max)\n\n"
            
            "For the Long Description:\n"
            "- Include all specific visual details like color, size, material, brand, etc.\n"
            "- Avoid assumptions or marketing language. Stick to what is visible.\n"
            "- Positioning based on image perspective.\n"
            "- Give account of the background as well."
        )
    elif image_type == "Lifestyle Image":
        return (
            "I am working on a project that involves captioning two images: a product image and a lifestyle image showcasing the product in use. "
            "You are to provide a short and long caption for this image. Follow the guidelines below:\n\n"
            
            "For the Short Description of the lifestyle image:\n"
            "- Emphasize simplicity.\n"
            "- Focus on key elements like object, shape, function, material, and color.\n"
            "- 20-25 words maximum, but better to keep it 5-15 words.\n"
            "- Avoid using too many details for the short description.\n\n"
            
            "For the Long Description:\n"
            "- Describe specific details: color, material, position of objects.\n"
            "- Do not include unnecessary marketing language, just describe what's visible.\n"
            "- Describe background elements and how the product interacts with them.\n"
            "- Avoid describing feelings or emotions tied to the image.\n"
            "- Focus on positions like left, right, centered, etc."
        )
    return ""

# Streamlit app interface
def main():
    st.title("Image Caption Generator")

    # Image type selection
    image_type = st.selectbox("Select Image Type", ["Product Image", "Lifestyle Image"])

    # Upload image
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_image:
        # Display uploaded image
        image = Image.open(uploaded_image)
        st.image(image, caption='Uploaded Image', use_column_width=True)

        # Generate the appropriate prompt for the selected image type
        prompt = get_prompt(image_type)

        # Button to generate captions
        if st.button("Generate Description"):
            generated_text = generate_image_descriptions(image, prompt)
            st.write("**Generated Description:**", generated_text)

if __name__ == "__main__":
    main()
