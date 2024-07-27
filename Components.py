import streamlit as st
import pandas as pd
import tabula as tb
import os
import time

@st.experimental_fragment
def file_uploader(text, filename, year_text):
    if os.path.exists(f'Inputs/{filename}.xlsx') and os.path.exists(f'{year_text}.txt'):
        st.session_state.years[year_text] = int(open(f'{year_text}.txt', 'r').read())

        st.write(f'**{filename} Already Exists... Delete by Clicking the Button below and Refresh the Page**')
        
        delete = st.button(f'Delete the saved file {filename}.xlsx')

        if delete:
            delete_file(f'Inputs/{filename}.xlsx')
            st.rerun()


    else:
        if not str(st.session_state.years.get(year_text)).isdigit():
            st.session_state.years[year_text] = none = st.text_input(f'Enter **{year_text}** th Year')

            if st.session_state.years.get(year_text):
                st.rerun()

        if str(st.session_state.years[year_text]).isdigit():
            text = text.replace('{}', year_text)
            file = st.file_uploader(f'{text}', type='pdf')

            if file:
                Inputs = tb.read_pdf(file, pages='all', lattice=True)

                full_table = pd.concat(Inputs, ignore_index=True)
                
                if not st.session_state.get('Inputs'):
                    st.session_state.Inputs = {}

                st.session_state.Inputs[filename] = full_table

                commit = st.button(f'Commit {file.name}')

                if commit:
                    save_to_excel(st.session_state.Inputs[filename], filename)
                    with st.spinner('Commiting and Refreshing'):
                        time.sleep(3)
                    st.rerun()

def save_to_excel(df, filename):
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'

    cwd = os.getcwd()
    
    if not os.path.exists('Inputs'):
        os.makedirs('Inputs')
    
    filepath = os.path.join(cwd, 'Inputs', filename)
    
    df.to_excel(filepath, index=False)
    st.success(f"Data saved as {filename}")

def delete_file(filepath):
    try:
        os.remove(filepath)
        print(f"File '{filepath}' deleted successfully.")
    except OSError as e:
        print(f"Error deleting the file '{filepath}': {e}")

def number_input(text):
  return st.number_input(text, step=1, min_value=0)

def button(text):
  return st.button(text)
