import streamlit as st

# setting page config. for centered mode
st.set_page_config(layout="centered")

from utils.footer import cust_footer

# Load CSS file
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# Load CSS file
load_css('styles.css')

def main():
    # Title of the app and description.
    title = """
        <div>
        <p class="title">Olive Scrapper</p>
        </div>
    """
    st.markdown(title, unsafe_allow_html=True)
    st.write("#")
    st.write("#")
    
    introduction = """
        <div>
        <p class="text">Olive Scraper is a web scraping tool developed by OdiaGenAI for web scraping Odia contents from different sources (e.g., websites, PDF, DOC, etc.)</p>
        </div>
    """
    st.markdown(introduction, unsafe_allow_html=True)

    st.write("#")
    st.write("###")
    contributors = """
        <div>
        <p class="text">Contributors: Dr. Shantipriya Parida, Sambit, A.R. Kamaldeen, Prosper</p>
        </div>
    """
    st.markdown(contributors, unsafe_allow_html=True)

    # Add a success message to the sidebar
    st.sidebar.success("Select a page above.")

    # importing the custom footer from utils
    cust_footer()

if __name__ == "__main__":
    main()
