import streamlit as st

# setting page config. for centered mode
st.set_page_config(layout="centered")


from utils.footer import cust_footer
import docx2txt
import requests
import pdfplumber

# Load CSS file
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# function to run the enter button
def run_function(documents):
    data = ""
    if documents is not None:
        for document in documents:
            document_details = {
                "filename": document.name,
                "filetype": document.type,
                "filesize": document.size
            }
            st.write(document_details)

            # Extract content from the txt file
            if document.type == "text/plain":
                # Read as bytes
                data += str(document.read(), "utf-8")

            # Extract content from the pdf file
            elif document.type == "application/pdf":
                # using PyPDF2
                # data += read_pdf(document)

                # using pdfplumber
                try:
                    with pdfplumber.open(document) as pdf:
                        all_text = ""
                        for page in pdf.pages:
                            text = page.extract_text()
                            all_text += text + "\n"
                        data += all_text
                except requests.exceptions.RequestException as e:
                    st.write("None")

            # Extract content from the docx file
            elif document.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                data += docx2txt.process(document)

        # Display the extracted text content from file
        st.text_area("Extracted Text", value=data, height=200)
        # return extract status, and the data extracted
        return True, data
    
        

    else:
        st.error("Error: An error occurred while fetching content.")
        # return extract status, and the data extracted
        return False, data


def main():
    
    st.subheader("Extract Data from Documents")

    documents = st.file_uploader(
        "", type=["pdf", "txt", "docx"], accept_multiple_files=True
    )

    if "button_enter_doc" not in st.session_state:
        st.session_state.button_enter_doc = False

    if "extracted_doc" not in st.session_state:
        st.session_state.extracted_doc = False
    data = ""

    enter_c1, enter_c2 = st.columns([0.5, 0.5])
    with enter_c1:
        if st.button("Enter"):
            st.session_state.button_enter_doc = True
    with enter_c2:
        print()

    # the enter button
    if st.session_state.button_enter_doc:
        # check if it is a sitemap or not
        if not documents:
            documents = None
        else:
            for doc in documents:
                if doc.name.split(".")[-1].lower() not in ["pdf", "txt", "docx"]:
                    # if documents is not the relevant type
                    st.error("Unsupported file: " + doc.name)

        st.session_state.extracted_doc, data = run_function(documents)

        if st.session_state.extracted_doc:
            col1, col2 = st.columns([0.5, 0.5])
            with col1:
                saved_button = False

                if st.download_button(
                    label="Save",
                    data=data
                ):
                    saved_button = True

            with col2:
                if st.button("Clear"):
                    st.session_state.button_enter_doc = False
                    st.session_state.extracted_doc = False
                    st.experimental_rerun()

            if saved_button:
                # Confirmation message
                st.success(f"File saved successfully.")

        else:
            clear_c1, clear_c2 = st.columns([0.5, 0.5])
            st.warning("Data not extracted")
            with clear_c1:
                if st.button("clear"):
                    st.session_state.button_enter_doc = False
                    st.session_state.extracted_doc = False
                    st.experimental_rerun()
            with clear_c2:
                print()
    st.write("#")
    st.write("#")        
            
                


    

    # Add a success message to the sidebar
    st.sidebar.success("Select a page above.")

    # importing the custom footer from utils
    cust_footer()


if __name__ == "__main__":
    main()
