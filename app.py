import streamlit as st
from PIL import Image, ImageDraw
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.messages import HumanMessage
import pytesseract
from gtts import gTTS
import io
import base64


# Set Tesseract command for local testing (Windows)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure Google Gemini API Key
GOOGLE_API_KEY = "AIzaSyDOTIWJl_mr6JbhO-QxGOWCYMEAxJY9Vus"  ## add your api key 
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GOOGLE_API_KEY)

# Function to convert an image to Base64 format
def image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

# Function to run OCR on an image
def run_ocr(image):
    return pytesseract.image_to_string(image).strip()

# Function to analyze the image using Gemini
def analyze_image(image, prompt):
    try:
        image_base64 = image_to_base64(image)
        message = HumanMessage(
            content=[ 
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": f"data:image/png;base64,{image_base64}"}
            ]
        )
        response = llm.invoke([message])
        return response.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# Function to convert text to speech (using a neutral or female voice)
def text_to_speech(text):
    tts = gTTS(text=text, lang='en', slow=False)
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    return audio_bytes.getvalue()

# Function to detect and highlight objects in the image
def detect_and_highlight_objects(image):
    # You can replace this with a more advanced object detection model (like YOLO or OpenCV)
    # For simplicity, we'll just create random bounding boxes here as placeholders
    draw = ImageDraw.Draw(image)
    # Example: Drawing rectangles as fake objects (Replace with actual detection model)
    objects = [
        {"label": "Obstacle", "bbox": (50, 50, 200, 200)},
        {"label": "Object", "bbox": (300, 100, 500, 300)}
    ]
    
    for obj in objects:
        bbox = obj['bbox']
        draw.rectangle([bbox[0], bbox[1], bbox[2], bbox[3]], outline="red", width=5)
        draw.text((bbox[0], bbox[1] - 10), obj['label'], fill="red")
    
    return image, objects

# Main app function
def main():
    st.set_page_config(page_title="AI Assistive Tool", layout="wide", page_icon="🤖")

    st.title("Ko'zi ojizlar uchun AI yordamchi vositasi 👁️ 🤖")
    st.write("""
       Ushbu sun'iy intellektga asoslangan vosita tasvirni tahlil qilish orqali ko'rish qobiliyati zaif odamlarga yordam beradi. 
        U quyidagi xususiyatlarni taqdim etadi:
        - **Scene Understanding**: Yuklangan tasvirlar mazmunini tavsiflaydi.
        - **Matnni nutqqa aylantirish**: OCR yordamida tasvirlardan matnni chiqarib oladi va ovoz chiqarib o‘qiydi.
        - **Ob'ekt va to'siqlarni aniqlash**: Xavfsiz navigatsiya uchun ob'ektlar yoki to'siqlarni aniqlaydi.
        - **Shaxsiylashtirilgan yordam**: yorliqlarni o‘qish yoki elementlarni tanib olish kabi tasvir mazmuniga asoslangan vazifaga oid ko‘rsatmalarni taklif qiladi.
        
        Boshlash uchun rasmni yuklang va AI sizning atrof-muhitingizni tushunish va o'zaro munosabatda bo'lishga yordam beradi!
    """)

    st.sidebar.header("📂 Rasmni yuklang")
    uploaded_file = st.sidebar.file_uploader("Rasmni yuklang (jpg, jpeg, png)", type=['jpg', 'jpeg', 'png'])

    st.sidebar.header("🔧 Ko'rsatma")
    st.sidebar.write("""
    1. Rasm yuklang.
    2. Quyidagi variantni tanlang:
       - 🖼️ Sahnani tasvirlash: Tasvir tavsifini oling.
       - 📜 Matnni ajratib olish: Rasmdan matnni ajratib oling.
       - 🚧 Ob'ektlar va to'siqlarni aniqlang: to'siqlarni aniqlang va ularni ta'kidlang.
       - 🛠️ Shaxsiylashtirilgan yordam: vazifaga oid yordam oling.
    3. Oson tushunish uchun natijalar ovoz chiqarib o'qiladi.
    """)

    if uploaded_file:
        if 'last_uploaded_file' in st.session_state and st.session_state.last_uploaded_file != uploaded_file:
            st.session_state.extracted_text = None
            st.session_state.summarized_text = None

        st.session_state.last_uploaded_file = uploaded_file
        image = Image.open(uploaded_file)

        st.markdown("""<style>
            .centered-image {
                display: block;
                margin-left: auto;
                margin-right: auto;
                width: 500px;
            }
        </style>""", unsafe_allow_html=True)

        image_base64 = image_to_base64(image)
        st.markdown(f'<img src="data:image/png;base64,{image_base64}" class="centered-image" />', unsafe_allow_html=True)

        def style_button(label, key, active_button_key):
            if 'active_button' not in st.session_state:
                st.session_state.active_button = None

            color = "green" if st.session_state.get('active_button') == active_button_key else "dodgerblue"

            button_html = f"""
            <style>
                div[data-testid="stButton"] > button {{
                    background-color: {color} !important;
                    color: white !important;
                    border: none !important;
                    padding: 20px 40px !important;
                    cursor: pointer !important;
                    border-radius: 10px;
                    font-size: 18px !important;
                    font-weight: bold;
                    transition: all 0.3s ease;
                }}
                div[data-testid="stButton"] > button:hover {{
                    background-color: darkorange !important;
                    transform: scale(1.1);
                }}
            </style>
            """
            st.markdown(button_html, unsafe_allow_html=True)
            return st.button(label, key=key, help=f"Click to activate {label}")

        if style_button("🖼️ Describe Scene", key="scene_description", active_button_key="scene_description"):
            st.session_state.active_button = "scene_description"
            with st.spinner("Generating scene description..."):
                scene_prompt = "Ushbu rasmni qisqacha tasvirlab ber, o'zbek tilida"
                scene_description = analyze_image(image, scene_prompt)
                st.subheader("Scene Description")
                st.success(scene_description)
                st.audio(text_to_speech(scene_description), format='audio/mp3')

        if style_button("📜 Extract Text", key="extract_text", active_button_key="extract_text"):
            st.session_state.active_button = "extract_text"
            with st.spinner("Extracting text..."):
                extracted_text = run_ocr(image)
                if extracted_text:
                    st.session_state.extracted_text = extracted_text
                    st.subheader("Extracted Text")
                    st.info(extracted_text)
                    st.audio(text_to_speech(extracted_text), format='audio/mp3')
                else:
                    no_text_message = "No text detected in the image."
                    st.session_state.extracted_text = no_text_message
                    st.subheader("No Text Detected")
                    st.info(no_text_message)
                    st.audio(text_to_speech(no_text_message), format='audio/mp3')

        if style_button("🚧 Detect Objects & Obstacles", key="detect_objects", active_button_key="detect_objects"):
            st.session_state.active_button = "detect_objects"
            with st.spinner("Identifying objects and obstacles..."):
                obstacle_prompt = "Ushbu rasmdagi ob'ektlar yoki to'siqlarni aniqla va xavfsiz navigatsiya uchun ularning joylashishini uzbek tilida tushuntir."
                obstacle_description = analyze_image(image, obstacle_prompt)
                st.subheader("Objects & Obstacles Detected")
                st.success(obstacle_description)
                st.audio(text_to_speech(obstacle_description), format='audio/mp3')

                # Highlight detected objects
                highlighted_image, objects = detect_and_highlight_objects(image.copy())
                st.image(highlighted_image, caption="Highlighted Image with Detected Objects", use_column_width=True)

        if style_button("🛠️ Personalized Assistance", key="personalized_assistance", active_button_key="personalized_assistance"):
            st.session_state.active_button = "personalized_assistance"
            with st.spinner("Providing personalized guidance..."):
                task_prompt = "Ushbu rasmning qisqacha mazmuniga asoslanib, vazifaga oid ko'rsatmalar ber. Elementni aniqlash, yorliqlarni oʻqish va tegishli kontekstni qoʻsh, o'zbek tilida"
                assistance_description = analyze_image(image, task_prompt)
                st.subheader("Personalized Assistance")
                st.success(assistance_description)
                st.audio(text_to_speech(assistance_description), format='audio/mp3')

if __name__ == "__main__":
    main()
