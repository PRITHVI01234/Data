import streamlit as st 
import pandas as pd
import os
from Components import file_uploader
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

if not st.session_state.get('years'):
  st.session_state.years = {}

st.set_page_config(page_title='TNEA Compare',layout="wide")

st.title('Seat Matrix Comparison PDF Uploads')

col1, col2 = st.columns(2)

with col1:
  file_uploader('Upload SeatMatrix **{}** th Year', 'a', 'N-1')
with col2:
  file_uploader('Upload SeatMatrix **{}** th Year', 'b', 'N')

def rename_first_four_columns(df):

    new_column_names = ['College Code', 'College Name', 'Branch Code', 'Branch Name']
    current_columns = df.columns.tolist()
    rename_mapping = {current_columns[i]: new_column_names[i] for i in range(min(len(current_columns), 4))}
    df = df.rename(columns=rename_mapping)
    
    return df

def execute_script():

    df1 = pd.read_excel(r"Inputs/a.xlsx")
    df2 = pd.read_excel(r"Inputs/b.xlsx")
    df1 = rename_first_four_columns(df1)
    df2 = rename_first_four_columns(df2)
    df1.to_excel("Inputs/a.xlsx", index=False)
    df2.to_excel("Inputs/b.xlsx", index=False)

    st.success("Changes have been made and files have been updated!")


st.sidebar.subheader(":rainbow-background[Note:]")
st.sidebar.success("**Upload both files, enter commit, and press 'Make Changes' to process.**")
if st.sidebar.button('Make Changes'):
    execute_script()
