import streamlit as st
from PIL import Image
import io
import os

# Import the Google Gemini API client and types.
# Ensure you have installed the library (e.g., pip install google-genai) and set up your API key.
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Initialize the Gemini API client.
if not GEMINI_API_KEY:
    st.error("Gemini API key not found in environment variable 'GEMINI_API_KEY'.")
    st.stop()

# Initialize the Gemini API client with the API key.
client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_warrant(file_bytes, mime_type):
    """
    Uses the Gemini API to analyze the warrant image or document.
    The prompt instructs the model to determine if the warrant is administrative or criminal.
    """
    prompt = (
        """Analyze the attached warrant document. Determine whether it is an administrative warrant or a criminal warrant.

        • A valid judicial subpoena requires 1) the name of the issuing court, 2) the signature of a judge or federal court clerk’s signature, 3) the target of the subpoena (e.g. FERPA information), and 4) the address of the target of the subpoena (e.g. the school).
        • An administrative subpoena (an “ICE subpoena” or “immigration subpoena”) is NOT valid. 

        • A valid judicial warrant requires 1) the name of the issuing court, 2) the signature of a judge or magistrate, 3) the target of the warrant (the address AND area to be searched), and 4) a current date.
        •An administrative warrant (“ICE warrant” or “immigration subpoena”) will usually be titled “Warrant of Removal/Deportation,” will not contain the name of a court or the signature of a judge or magistrate, and is NOT valid.

        Your answer should:

        1. Clearly state whether the warrant is administrative or criminal.

        2. Explain what the recipient's obligations are based on the type of warrant. Importantly, explain if
        the recipient is required to allow an agent into their home or business based on the type of warrant.

        3. Provide a brief explanation of why the warrant is administrative or criminal.

        Your answer should be short and clear. Use language that is easy to understand for a non-legal audience
        especially at a 6th grade reading level or below.
        """
    )
    # Create a Part object from the file bytes.
    content_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
    
    # Call the Gemini API. Adjust the model name if needed.
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # or another Gemini model as required
            contents=[content_part, prompt]
        )
        return response.text
    except Exception as e:
        return f"Error during analysis: {e}"

def process_uploaded_file(uploaded_file):
    """
    Processes the uploaded file:
    - For image files, returns a PIL Image object for preview.
    - For PDFs, no preview is generated.
    Returns a tuple (file_bytes, mime_type, preview_image) where preview_image is None for PDFs.
    """
    # Get the raw bytes and MIME type from the uploaded file.
    file_bytes = uploaded_file.getvalue()
    mime_type = uploaded_file.type

    preview_image = None
    if mime_type != "application/pdf":
        # Reset pointer and open with PIL to display the image.
        uploaded_file.seek(0)
        try:
            preview_image = Image.open(uploaded_file)
        except Exception:
            st.warning("Could not open the image for preview.")
    return file_bytes, mime_type, preview_image

def main():
    st.title("ICE Warrant Analyzer")
    st.write("Upload an image (JPEG/PNG) or PDF of the warrant, or capture one using your camera.")

    # Select input method.
    input_method = st.radio("Select input method:", ("Upload File", "Capture Image"))

    uploaded_file = None
    if input_method == "Upload File":
        uploaded_file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png", "pdf"])
    else:
        # Use Streamlit's camera input widget.
        uploaded_file = st.camera_input("Capture an image")

    if uploaded_file is not None:
        # Process the file and extract raw bytes, mime type, and a preview (if available).
        file_bytes, mime_type, preview_image = process_uploaded_file(uploaded_file)
        
        if mime_type != "application/pdf" and preview_image:
            st.image(preview_image, caption="Uploaded/Captured Image", use_column_width=True)
        else:
            st.write("PDF file uploaded.")

        st.write("Analyzing the warrant, please wait...")
        # Call the Gemini API to analyze the warrant.
        analysis_result = analyze_warrant(file_bytes, mime_type)
        st.success("Analysis Complete")
        st.write(analysis_result)

if __name__ == "__main__":
    main()
