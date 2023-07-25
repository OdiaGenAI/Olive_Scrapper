import streamlit as st

# setting page config. for centered mode
st.set_page_config(layout="centered")

from utils.footer import cust_footer

from lxml import etree
import justext
import concurrent.futures
import datetime
import requests
from bs4 import BeautifulSoup
import json

# ----- FUNCTIONS -----
# function to check whether the url is a sitemap or not
def check_sitemap(url):
    # Check the URL's ending
    if url.lower().endswith(('sitemap.xml', 'sitemap_index.xml', 'sitemap')):
        try:
            # Parse the content as XML
            response = requests.get(url)
            xml_content = etree.fromstring(response.content)
            # Check for sitemap-specific elements
            if xml_content.tag == 'urlset' or xml_content.tag == 'sitemapindex':
                return True
        except etree.XMLSyntaxError:
            pass

    # Additional conditions for identifying sitemaps
    if 'sitemap' in url.lower():
        # Perform additional checks specific to the website's structure or naming conventions
        return True

    return False



def extract_urls_from_sitemaps(xml_url):
    # Make a GET request to the URL and extract the xml content
    response = requests.get(xml_url)

    soup = BeautifulSoup(response.text, 'xml')
    extracted_urls = []

    # check if the sitemap contains nested sitemaps
    sitemap_tags = soup.find_all('sitemap')
    if sitemap_tags:
        # Process nested sitemaps
        for sitemap_tag in sitemap_tags:
            print("sitemap_tags:" + str(sitemap_tag))
            nested_url = sitemap_tag.find('loc').text
            print('nested_url:', nested_url)
            nested_urls = extract_urls_from_sitemaps(nested_url)
            extracted_urls.extend(nested_urls)
    else:
        # Extract URLs from the current sitemap
        loc_tags = soup.find_all('loc')
        for loc_tag in loc_tags:
            # if loc_tag.parent.name != 'image':
            url = loc_tag.text
            if url.endswith('.pdf') or url.endswith('.jpg') or url.endswith('.jpeg'):
                print(f"url skipped because it is a {url.split('.')[-1]}")
            else:
                print('url:', url)
                extracted_urls.append(url)

    return extracted_urls



# function to check whether the entered url is valid
def valid_url(url):
    try:
        # Make a GET request to the URL and extract the text content
        response = requests.get(url)
        if response.status_code == 200:
            return True

    except requests.exceptions.RequestException as e:
        return False
    


# function to create a custom stoplist for justext
def custom_stoplist():
    odia_stopwords = [
        "ଏହି", "ଏକ", "ଏକାଉଣଟ", "ମୁଁ", "ମୋର", "ମୁଁ ନିଜେ", "ଆମେ", "ଆମର", "ଆମର", "ଆମେ ନିଜେ", "ତୁମେ", "ତୁମର", "ତୁମର",
        "ନିଜେ", "ନିଜେ", "ସେ", "ତାଙ୍କୁ", "ତାଙ୍କର",
        "ନିଜେ", "ସେ", "ତାଙ୍କୁ", "ତାଙ୍କର", "ନିଜେ", "ଏହା", "ଏହାର", "ନିଜେ |", "ସେମାନେ", "ସେଗୁଡିକ", "ସେମାନଙ୍କର",
        "ସେମାନଙ୍କର", "ନିଜେ |", "କଣ", "ଯାହା", "କିଏ", "କାହାକୁ",
        "ଏହା", "ତାହା", "ଏଗୁଡ଼ିକ", "ସେଗୁଡ଼ିକ", "ମୁଁ", "ହେଉଛି", "ହେଉଛି |", "ଥିଲା", "ଥିଲା |", "ହୁଅ", "ହୋଇସାରିଛି |", "ହେବା",
        "ଅଛି", "ଅଛି", "ଥିଲା", "ଅଛି", "କର", "କରେ |",
        "କରିଛନ୍ତି", "କରିବା", "ଏବଂ", "କିନ୍ତୁ", "ଯଦି", "କିମ୍ବା", "କାରଣ", "ଯେପରି", "ପର୍ଯ୍ୟନ୍ତ", "ଯେତେବେଳେ", "ର", "ପାଇଁ",
        "ସହିତ", "ବିଷୟରେ", "ବିପକ୍ଷରେ", "ମଧ୍ୟରେ", "ଭିତରକୁ", "ମାଧ୍ୟମରେ",
        "ସମୟରେ", "ପୂର୍ବରୁ", "ପରେ", "ଉପରେ", "ନିମ୍ନରେ |", "କୁ", "ଠାରୁ", "ଅପ୍", "ତଳକୁ", "ଭିତରେ", "ବାହାରେ", "ଉପରେ", "ବନ୍ଦ",
        "ସମାପ୍ତ", "ତଳେ |", "ପୁନର୍ବାର", "ଆଗକୁ",
        "ତାପରେ", "ଥରେ |", "ଏଠାରେ", "ସେଠାରେ", "କେବେ", "କେଉଁଠାରେ", "କିପରି", "ସମସ୍ତ", "ଉଭୟ", "ପ୍ରତ୍ୟେକ", "ଅଳ୍ପ", "ଅଧିକ",
        "ଅଧିକାଂଶ", "ଅନ୍ୟ", "କେତେକ", "ଏହିପରି",
        "ନୁହେଁ |", "କେବଳ", "ନିଜର", "ସମାନ", "ତେଣୁ", "ଅପେକ୍ଷା", "ମଧ୍ୟ", "ବହୁତ", "କରିପାରିବେ |", "ଇଚ୍ଛା", "କେବଳ",
        "କରିବା ଉଚିତ", "ବର୍ତ୍ତମାନ"
    ]
    return frozenset(odia_stopwords)



# function to extract data from url using justext
def extract_data_from_url_(url):
    response = requests.get(url)
    response.raise_for_status()
    page = response.content

    para = ""
    paragraphs = justext.justext(page, custom_stoplist(), 70, 140, 0.0, 0.02, 0.5, 150, False)
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            para = para + '\n' + paragraph.text

    return para


sitemap_data = ""



# function to process a batch of URLS in sitemaps
def process_urls(sitemap_urls , category):

    extracted_txt = ""
    extracted_jsonl_list= []
    for url in sitemap_urls:
        if valid_url(url):
            print(url)
            # using justext to extract data
            temp_para = extract_data_from_url_(url)
            temp_txt_data = ('\n\nFrom url:' + url + '\n' + temp_para + '\n')
            temp_jsonl_data = {"text": temp_para, "url": url, "category": category, "timestamp": str(datetime.datetime.now())}
            extracted_txt += temp_txt_data
            extracted_jsonl_list.append(temp_jsonl_data)
        else:
            st.error("Couldnt extract data from " + url)

    # Convert data_list to JSONL string
    extracted_jsonl_list_encoded = [json.dumps(data, ensure_ascii=False) for data in extracted_jsonl_list]
    extracted_jsonl = '\n'.join(extracted_jsonl_list_encoded)
    
    return extracted_txt, extracted_jsonl



# function to process for a single URL
def run_function(url , category):
    extracted_txt = ""
    # Check if the user has provided a URL
    if url:
        if valid_url(url):
            temp_para = extract_data_from_url_(url)
            temp_txt_data = ('\n\nFrom url:' + url + '\n' + temp_para + '\n')
            extracted_txt = temp_txt_data
            extracted_jsonl = {"text": str(temp_para), "url":str(url) , "category": category , "timestamp": str(datetime.datetime.now())}

            # displaying extracted txt for single URL
            st.text_area("Extracted Text", value=extracted_txt, height=200)
            
            
            extracted_jsonl = json.dumps(extracted_jsonl, ensure_ascii=False)

            # return extract status, and the data extracted
            return True, extracted_txt, extracted_jsonl
        else:
            return False, None, None
    else:
        st.error("Error: An error occurred while fetching content.")
        # return extract status, and the data extracted
        return False, None, None
    


def main():
    st.subheader("Extract Data from URLs")

    category = st.selectbox(
        'Select a Category',
       ('News Articles','Poems','Magazines', 'Other') )
    
    # dividing the body section into 2 columns for url and enter button
    col1, col2 = st.columns([0.7,0.3])

    with col1:
        url_or_xml = st.text_input(label='', placeholder="Enter URL")
        is_a_sitemap = check_sitemap(url_or_xml)

    with col2:
        st.write('##')
        if "button_enter_url" not in st.session_state:
            st.session_state.button_enter_url = False

        if st.button("Enter"):
            st.session_state.button_enter_url = True

    if "extracted_url" not in st.session_state:
        st.session_state.extracted_url = False
    data = ""

    

    # the enter button
    if st.session_state.button_enter_url:
        # check if it is a sitemap or not
        if is_a_sitemap:
            if "Initial" not in st.session_state:
                st.session_state.Initial = True
            # check whether its the initial state
            if st.session_state.Initial == True:
                
                xml = url_or_xml
                st.write("It is a sitemap")
                stored_sitemap_urls = extract_urls_from_sitemaps(xml)
                print('\nno. of urls: ', len(stored_sitemap_urls))
                st.write('no. of urls {}', format(len(stored_sitemap_urls)))

                if stored_sitemap_urls:
                    print(stored_sitemap_urls)
                    current_time = datetime.datetime.now()
                    print(current_time)
                    st.write(current_time)
                    # for sitemap_url in stored_sitemap_urls:

                    #     if valid_url(sitemap_url):
                    #         print(sitemap_url)
                    #         # using justext to extract data
                    #         data = data + extract_data_from_url_(sitemap_url)
                    #     else:
                    #         st.error("Couldnt extract data from " + sitemap_url)

                    num_threads = 16  # Number of threads to use

                    # Calculate the split size for each thread
                    split_size = len(stored_sitemap_urls) // num_threads

                    # Create a ThreadPoolExecutor with maximum `num_threads` threads
                    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                        futures = []
                        for i in range(num_threads):
                            start_index = i * split_size
                            end_index = start_index + split_size if i != num_threads - 1 else None
                            temp_urls = stored_sitemap_urls[start_index:end_index]
                            future = executor.submit(process_urls, temp_urls, category)
                            futures.append(future)

                        # Retrieve the extracted data from each thread
                        text_data = []
                        jsonl_data = []
                        for future in futures:
                            text_result, jsonl_result = future.result()
                            text_data.append(text_result)
                            jsonl_data.append(jsonl_result)

                    # Combine the extracted data from all threads
                    combined_text_data = ''.join(text_data)
                    combined_jsonl_data = '\n'.join(jsonl_data)

                    # Use the combined data as needed
                    # print("Combined Text Data:")
                    # print(combined_text_data)
                    # print("Combined JSONL Data:")
                    # print(combined_jsonl_data)

                         

                    if "sitemap_data_jsonl" not in st.session_state:
                        st.session_state.sitemap_data_jsonl = combined_jsonl_data
                    if "sitemap_data_text" not in st.session_state:
                        st.session_state.sitemap_data_text = combined_text_data

                    

                    
                    current_time = datetime.datetime.now()
                    print(current_time)
                    st.write(current_time)
                    st.session_state.Initial = False
                    print("\n\n\n\n2)Initial State", st.session_state.Initial, "\n\n\n\n\n")
                    st.session_state.extracted_url = True

                else:
                    st.error("Error: Invalid sitemap.")


        else:
            url = url_or_xml
            st.session_state.extracted_url, data_txt, data_jsonl = run_function(url , category)

        
        if st.session_state.extracted_url:
            # displaying extracted txt for sitemaps
            if is_a_sitemap:
                st.text_area("Extracted Text", value=st.session_state.sitemap_data_text, height=300)

            save_as,checkbox_c1, checkbox_c2 = st.columns([0.33 , 0.33 , 0.33])

            # initializing the checbox bool
            save_as_txt =False
            save_as_json = False
            saved_successfully = False
            
            with save_as:
                st.write("Save as ")
            with checkbox_c1:
                save_as_txt = st.checkbox("text", value=False)
                
            with checkbox_c2:
                save_as_json = st.checkbox("jsonl", value=False)
                
            if not save_as_txt and not save_as_json:
                if st.button("Clear"):
                    st.session_state.button_enter_url = False
                    st.session_state.Initial = True
                    st.session_state.extracted_url = False
                    if 'sitemap_data_text' in st.session_state:
                        del st.session_state['sitemap_data_text']
                    if 'sitemap_data_jsonl' in st.session_state:
                        del st.session_state['sitemap_data_jsonl']
                    st.session_state.button_enter_url = False
                    st.experimental_rerun()
            else:
                col1, col2 = st.columns([0.5, 0.5])
                # save column
                with col1:
                    
                    if is_a_sitemap:
                        
                        if save_as_txt:
                            if st.download_button(label="Save as txt",data=st.session_state.sitemap_data_text ):
                                saved_successfully = True
                        if save_as_json:
                            if st.download_button(label="Save as jsonl", data=st.session_state.sitemap_data_jsonl, mime="application/json"):
                                saved_successfully = True
                    else:
                        if save_as_txt:
                            if st.download_button(label="Save as txt",data=data_txt ):
                                saved_successfully = True
                        if save_as_json:
                            if st.download_button(label="Save as jsonl", data=data_jsonl, mime="application/json"):
                                saved_successfully = True

                # clear column                        
                with col2:
                    if st.button("Clear"):
                        st.session_state.button_enter_url = False
                        st.session_state.Initial = True
                        st.session_state.extracted_url = False
                        if 'sitemap_data_text' in st.session_state:
                            del st.session_state['sitemap_data_text']
                        if 'sitemap_data_jsonl' in st.session_state:
                            del st.session_state['sitemap_data_jsonl']
                        st.session_state.button_enter_url = False
                        st.experimental_rerun()

            if saved_successfully:
                # Confirmation message
                st.success(f"File saved successfully.")
            st.write("#")
            st.write("#")
        else:
            st.warning("Data not extracted")
            if st.button("clear"):
                st.session_state.button_enter_url = False
                st.session_state.extracted_url = False
                st.experimental_rerun()
            st.write("#")
            st.write("#")


    # Add a success message to the sidebar
    st.sidebar.success("Select a page above.")

    # importing the custom footer from utils
    cust_footer()
    

if __name__ == "__main__":
    main()
