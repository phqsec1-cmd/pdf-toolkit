import streamlit as st
import fitz
from PIL import Image
import io
import time

# ---- USER DATABASE ----
users = {
    "Admin": "admin@1234",
    "Ashu": "police@1234"
}

# ---- LOGIN FUNCTION ----
def login():

    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in users and users[username] == password:

            st.session_state["login"] = True
            st.session_state["user"] = username
            st.success("Login Successful")
            st.rerun()

        else:
            st.error("❌ Invalid Username or Password")

# ---- SESSION STATE ----
if "login" not in st.session_state:
    st.session_state["login"] = False

# ---- LOGIN PAGE ----
if not st.session_state["login"]:
    login()
    st.stop()

# ---- APP AFTER LOGIN ----

st.sidebar.success(f"👤 Logged in as: {st.session_state['user']}")

if st.sidebar.button("Logout"):
    st.session_state["login"] = False
    st.rerun()

# ---- MAIN APP ----
st.title("📄 PDF Toolkit Dashboard")

st.write("Welcome to the PDF Toolkit App 🚀")

st.info("अब यहाँ आप अपना पूरा PDF Toolkit Code डाल सकते हैं")
#---------------------------Other----------------------
st.set_page_config(page_title="PDF Toolkit Pro", page_icon="📄", layout="wide")

# ---------- ANIMATED CSS ----------

st.markdown("""
<style>

.stApp{
background: linear-gradient(-45deg,#0f2027,#203a43,#2c5364,#1c92d2);
background-size:400% 400%;
animation:gradient 15s ease infinite;
}

@keyframes gradient{
0%{background-position:0% 50%}
50%{background-position:100% 50%}
100%{background-position:0% 50%}
}

.title{
text-align:center;
font-size:45px;
color:white;
font-weight:bold;
margin-bottom:20px;
}

.card{
background:rgba(255,255,255,0.1);
padding:25px;
border-radius:15px;
backdrop-filter:blur(10px);
margin-bottom:20px;
}

.stButton>button{
background:linear-gradient(45deg,#ff512f,#dd2476);
color:white;
border-radius:10px;
padding:10px 20px;
}

.stFileUploader{
border:2px dashed white;
padding:20px;
border-radius:15px;
background:rgba(255,255,255,0.1);
}

[data-testid="stSidebar"]{
background:linear-gradient(#141e30,#243b55);
}

.progress-circle{
width:130px;
height:130px;
border-radius:50%;
display:flex;
align-items:center;
justify-content:center;
font-size:25px;
color:white;
margin:auto;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📄 Smart PDF Toolkit Pro</div>', unsafe_allow_html=True)

# ---------- CIRCULAR PROGRESS FUNCTION ----------

def circular_progress(percent):

    st.markdown(
        f"""
        <div style="display:flex;justify-content:center">
        <div class="progress-circle"
        style="background:conic-gradient(#00eaff {percent*3.6}deg,#ffffff22 0deg);">
        {percent}%
        </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------- MENU ----------

menu = st.sidebar.selectbox(
"Select Tool",
[
"PDF Compress",
"PDF Merge",
"PDF Split",
"Image to PDF",
"PDF to Image",
"PDF Lock",
"PDF Unlock"
]
)

# ---------- PDF COMPRESS ----------

if menu == "PDF Compress":

    file = st.file_uploader("Upload PDF", type="pdf")

    unit = st.selectbox("Target Size Unit", ["MB","KB"])

    if unit == "MB":
        target = st.slider("Target Size (MB)",1,20,5)
        target_bytes = target * 1024 * 1024
    else:
        target = st.slider("Target Size (KB)",5,300,100)
        target_bytes = target * 1024

    if file:

        data = file.read()

        st.info(f"Original Size: {len(data)/1024:.2f} KB")

        if st.button("Compress PDF"):

            pdf = fitz.open(stream=data,filetype="pdf")

            quality = 80
            compressed = data

            percent = 0
            progress_area = st.empty()

            while len(compressed) > target_bytes and quality > 10:

                percent += 10

                progress_area.empty()

                with progress_area.container():
                    circular_progress(percent)

                output = fitz.open()

                for page in pdf:

                    pix = page.get_pixmap()

                    img = pix.tobytes("jpeg",jpg_quality=quality)

                    rect = page.rect

                    new_page = output.new_page(width=rect.width,height=rect.height)

                    new_page.insert_image(rect,stream=img)

                buffer = io.BytesIO()

                output.save(buffer)

                compressed = buffer.getvalue()

                quality -= 10

                output.close()

                time.sleep(0.3)

            pdf.close()

            circular_progress(100)

            st.success(f"Compressed Size: {len(compressed)/1024:.2f} KB")

            st.download_button(
            "Download Compressed PDF",
            data=compressed,
            file_name="compressed.pdf"
            )

# ---------- PDF MERGE ----------

elif menu == "PDF Merge":

    files = st.file_uploader("Upload PDFs",type="pdf",accept_multiple_files=True)

    if files and st.button("Merge"):

        merged = fitz.open()

        for f in files:

            pdf = fitz.open(stream=f.read(),filetype="pdf")

            merged.insert_pdf(pdf)

        buffer = io.BytesIO()

        merged.save(buffer)

        st.download_button(
        "Download Merged PDF",
        data=buffer.getvalue(),
        file_name="merged.pdf"
        )

# ---------- PDF SPLIT ----------

elif menu == "PDF Split":

    file = st.file_uploader("Upload PDF",type="pdf")

    if file:

        pdf = fitz.open(stream=file.read(),filetype="pdf")

        page = st.number_input("Page Number",1,len(pdf))

        if st.button("Extract Page"):

            new_pdf = fitz.open()

            new_pdf.insert_pdf(pdf,from_page=page-1,to_page=page-1)

            buffer = io.BytesIO()

            new_pdf.save(buffer)

            st.download_button(
            "Download Page",
            data=buffer.getvalue(),
            file_name=f"page_{page}.pdf"
            )

# ---------- IMAGE TO PDF ----------

elif menu == "Image to PDF":

    images = st.file_uploader(
    "Upload Images",
    type=["png","jpg","jpeg"],
    accept_multiple_files=True
    )

    if images and st.button("Convert"):

        pdf = fitz.open()

        for img in images:

            image = Image.open(img)

            img_bytes = io.BytesIO()

            image.save(img_bytes,format="PNG")

            rect = fitz.Rect(0,0,image.width,image.height)

            page = pdf.new_page(width=image.width,height=image.height)

            page.insert_image(rect,stream=img_bytes.getvalue())

        buffer = io.BytesIO()

        pdf.save(buffer)

        st.download_button(
        "Download PDF",
        data=buffer.getvalue(),
        file_name="images.pdf"
        )

# ---------- PDF TO IMAGE ----------

elif menu == "PDF to Image":

    file = st.file_uploader("Upload PDF",type="pdf")

    if file:

        pdf = fitz.open(stream=file.read(),filetype="pdf")

        if st.button("Convert"):

            for i in range(len(pdf)):

                page = pdf.load_page(i)

                pix = page.get_pixmap()

                img = pix.tobytes("png")

                st.download_button(
                f"Download Page {i+1}",
                data=img,
                file_name=f"page{i+1}.png"
                )

# ---------- PDF LOCK ----------

elif menu == "PDF Lock":

    file = st.file_uploader("Upload PDF",type="pdf")

    password = st.text_input("Enter Password",type="password")

    if file and password and st.button("Lock PDF"):

        pdf = fitz.open(stream=file.read(),filetype="pdf")

        buffer = io.BytesIO()

        pdf.save(
        buffer,
        encryption=fitz.PDF_ENCRYPT_AES_256,
        owner_pw=password,
        user_pw=password
        )

        st.download_button(
        "Download Locked PDF",
        data=buffer.getvalue(),
        file_name="locked.pdf"
        )

# ---------- PDF UNLOCK ----------

elif menu == "PDF Unlock":

    file = st.file_uploader("Upload Locked PDF",type="pdf")

    password = st.text_input("Enter Password",type="password")

    if file and password:

        pdf = fitz.open(stream=file.read(),filetype="pdf")

        if pdf.authenticate(password):

            buffer = io.BytesIO()

            pdf.save(buffer)

            st.download_button(
            "Download Unlocked PDF",
            data=buffer.getvalue(),
            file_name="unlocked.pdf"
            )
