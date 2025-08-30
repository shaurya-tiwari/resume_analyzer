
# flow  of code , without stramlit

# 1--------extract_text_from_pdf
# def extract_text_from_pdf(uploaded_file):
#     text = ""
#     with pdfplumber.open(uploaded_file) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text


# Uses pdfplumber to open a PDF file.

# Loops through each page in the PDF.

# Extracts text (page.extract_text()).

# If text exists, appends it to text string.

# Returns the whole PDF’s text as a string.



#2---------------- extract_text_from_docx
# def extract_text_from_docx(uploaded_file):
#     doc = docx.Document(uploaded_file)
#     text = "\n".join([para.text for para in doc.paragraphs])
#     return text


#3--------------- Resume file handlingResume file handling
# resume_text = ""
# if resume_file is not None:
#     if resume_file.type == "application/pdf":
#         resume_text = extract_text_from_pdf(resume_file)
#     elif resume_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
#         resume_text = extract_text_from_docx(resume_file)


#4-------------- Displaying results
# if resume_text and job_description:
#     st.subheader(" Extracted Resume Text:")
#     st.write(resume_text[:1000])  # first 1000 characters
#     st.subheader("Job Description:")
#     st.write(job_description)

# ------------------------------------------------------------------
# without stramlit 
# import pdfplumber
# import docx



# read pf file ----------
# def extract_text_from_pdf(file_path): # fille path is parameter    
#     text = ""
#     with pdfplumber.open(file_path) as pdf:
#         for page in pdf.pages
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text



# read dpcx file ---------
# def extract_text_from_docx(file_path):
#     doc = docx.Document(file_path)
#     text = "\n".join([para.text for para in doc.paragraphs])
#     return text


# # Example usage (without Streamlit)
# resume_pdf = "shauryaResume.pdf"
# resume_docx = "shauryaResume.docx"
# job_description = """We need a Machine Learning Engineer skilled in Python, SQL, Deep Learning, and Cloud Deployment."""

# # Extract text from PDF
# resume_text_pdf = extract_text_from_pdf(resume_pdf)
# print("Resume (PDF) Extracted Text:\n", resume_text_pdf[:500]) # onnly 500 words 

# # Extract text from DOCX
# resume_text_docx = extract_text_from_docx(resume_docx)
# print("\nResume (DOCX) Extracted Text:\n", resume_text_docx[:500])

# # Show Job Description
# print("\nJob Description:\n", job_description)
