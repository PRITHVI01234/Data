import streamlit as st
import pandas as pd
from background import BackgroundCSSGenerator

# Set up Streamlit page configuration
st.set_page_config(
    page_title="TNEA Comparison",
    page_icon="🔍",
    layout="wide"
)

# Define paths for background images
img1_path = r"Main_bg.jpg"
img2_path = r"Sidebar_bg.jpeg"
background_generator = BackgroundCSSGenerator(img1_path, img2_path)
page_bg_img = background_generator.generate_background_css()
st.markdown(page_bg_img, unsafe_allow_html=True)

# Hardcoded user credentials (in a real application, secure this properly)
user_credentials = {
    "CIT-CDC": "CIT2024@",
}

# Function to check login
def check_login(username, password):
    return user_credentials.get(username) == password

# Authentication status stored in session state
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None

# Sign-in form
if st.session_state.authentication_status != True:
    st.title("Sign In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign In"):
        if check_login(username, password):
            st.session_state.authentication_status = True
            st.session_state.username = username
        else:
            st.error("Invalid username or password")
else:
    st.title("TNEA 2023-2024 Seat Matrix Comparison")
    st.divider()

    # Read CSV files
    form4_df = pd.read_csv('form4.csv')
    form5_df = pd.read_csv('form5.csv')

    # Define functions to filter data
    def filter_form4(data):
        filtered = data.copy()
        bound = st.container(border=True)
        left, check1, right = bound.columns([0.4, 0.135, 0.3])
        
        college_name = left.text_input('Enter College Name', placeholder='Enter College Name')
        check1.write('')
        check1.write('')
        starts_with = check1.checkbox('Starts With', value=False)
        college_code = int()

        try:
            college_code = right.text_input('Enter College Code', placeholder='Enter College Code')
            if college_code != '':
                college_code = int(college_code)
        except:
            st.error('College Code is an Integer.')

        if college_name != '':
            if starts_with:
                filtered = filtered[filtered['College Name'].str.lower().str.startswith(college_name.lower())]
            else:
                filtered = filtered[filtered['College Name'].str.lower().str.contains(college_name.lower())]

        if college_code:
            filtered = filtered[filtered['College Code'].astype(str).str.startswith(str(college_code))]

        return filtered

    def filter_form5(data):
        filtered = data.copy()
        bound = st.container(border=True)
        _college_name, sw_toggle, _college_code = bound.columns([0.92, 0.3, 0.8])

        college_name = _college_name.text_input('Enter College Name', placeholder='Enter College Name')
        sw_toggle.write('')
        sw_toggle.write('')
        c_starts_with = sw_toggle.checkbox('Starts With', value=False)
        college_code = int()

        try:
            college_code = _college_code.text_input('Enter College Code', placeholder='Enter College Code', value=1399)
            if college_code != '':
                college_code = int(college_code)
        except:
            st.error('College Code is an Integer.')

        _branch_name, sw_toggle, _branch_code = bound.columns([0.92, 0.3, 0.8])

        branch_name = _branch_name.text_input('Enter Branch Name', placeholder='Enter Branch Name')
        sw_toggle.write('')
        sw_toggle.write('')
        b_starts_with = sw_toggle.checkbox('Starts With', value=False, key="yes")
        branch_code = _branch_code.text_input('Enter Branch Code', placeholder='Enter Branch Code')

        if college_name != '':
            if c_starts_with:
                filtered = filtered[filtered['College Name'].str.lower().str.startswith(college_name.lower())]
            else:
                filtered = filtered[filtered['College Name'].str.lower().str.contains(college_name.lower())]

        if college_code:
            filtered = filtered[filtered['College Code'].astype(str).str.startswith(str(college_code))]

        if branch_name != '':
            if b_starts_with:
                filtered = filtered[filtered['Branch Name'].str.lower().str.startswith(branch_name.lower())]
            else:
                filtered = filtered[filtered['Branch Name'].str.lower().str.contains(branch_name.lower())]

        if branch_code:
            filtered = filtered[filtered['Branch Code'].astype(str).str.startswith(str(branch_code))]

        return filtered

    with st.sidebar:
        st.session_state.form = st.selectbox(
            label='Select Form',
            options=['Form 4', 'Form 5']
        )

    if st.session_state.get('form'):
        if st.session_state.form == 'Form 4':
            st.session_state.filtered = filter_form4(form4_df)
        elif st.session_state.form == 'Form 5':
            st.session_state.filtered = filter_form5(form5_df)

    if isinstance(st.session_state.get('filtered'), pd.DataFrame):
        # Apply conditional formatting
        def highlight_diff(row):
            difference = row['Difference']
            if difference > 0:
                return ['background-color: lightgreen'] * len(row)
            elif difference < 0:
                return ['background-color: red'] * len(row)
            if row['2023'] == 0:
                row_color = ['background-color: green'] * len(row)
            if row['2024'] == 0:
                row_color = ['background-color: blue'] * len(row)
            else:
                return [''] * len(row)

        styled_df = st.session_state.filtered.style.apply(highlight_diff, axis=1)
        st.dataframe(styled_df, use_container_width=True)
