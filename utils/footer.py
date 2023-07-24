import streamlit as st

def cust_footer():
    footer = """
        <style>
        footer {
            visibility: hidden !important;
        }

        .divfooter {
            display: flex;
            justify-content: center; 
            align-items: center; 
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            padding: 10px;
            border-top: 2px solid grey;
            background: white;
            
            
        }
        @media (min-width: 768px) {
            .divfooter {
                justify-content: center;
                padding-left: 10%;
            }

        }

        
        </style>
        <div class="divfooter">
        <p style="margin-bottom: 0px">© 2023 Odia Generative AI</p>
        </div>
        """
    st.markdown(footer, unsafe_allow_html=True)