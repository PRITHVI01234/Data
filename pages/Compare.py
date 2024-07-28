import pandas as pd
import streamlit as st
from Processors import SeatMatrix
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

# Check if user is logged in
if not st.session_state.get('logged_in'):
    st.error('Please log in through the Home page to access this content.')
else:
  try:
    communities = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']

    def TotalCollegeWise(sm):
      result = sm.data.groupby(['College Code', 'College Name']).apply(
          lambda group : group.assign(
              Total=sm.filter(college_code=group['College Code'].iloc[0])[communities].sum().sum()
          )
      ).reset_index(level=[2], drop=True).drop(columns=['College Code', 'College Name']+['Branch Code', 'Branch Name']).reset_index().drop_duplicates(
          subset=['College Code']
      ).reset_index(drop=True).drop(columns=communities)

      return result

    def TotalCollegeBranch(sm):
      result = sm.data.groupby(['College Code', 'College Name', 'Branch Code', 'Branch Name']).apply(
          lambda group : group.assign(
              Total=sm.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])[communities].sum(axis=1).iloc[0]
          )
      ).reset_index(level=[4], drop=True).drop(columns=['College Code', 'College Name']+['Branch Code', 'Branch Name']).reset_index().drop_duplicates(
          subset=['College Code', 'Branch Code']
      ).reset_index(drop=True).drop(columns=communities)

      return result

    def form4(a, b):
      
      a = TotalCollegeWise(a)
      b = TotalCollegeWise(b)

      removed = []
      new = []
      common_a = []
      common_b = []

      for ind, row in a.iterrows():
        if row['College Code'] not in list(b['College Code']):
          removed_row = row.copy()
          removed_row['Total'] = 0
          removed_row['n'] = st.session_state.a.filter(college_code=removed_row['College Code'])[communities].sum().sum()
          removed_row['Difference'] = removed_row['Total'] - removed_row['n']
          removed.append(removed_row)
        else:
          common_a.append(row.copy())

      for ind, row in b.iterrows():
        if row['College Code'] not in list(a['College Code']):
          new_row = row.copy()
          new_row['Total'] = st.session_state.b.filter(college_code=new_row['College Code'])[communities].sum().sum()
          new_row['n'] = 0
          new_row['Difference'] = new_row['Total'] - new_row['n']
          new.append(new_row)
        else:
          common_b.append(row.copy())

      common_a = pd.DataFrame(common_a)
      common_b = pd.DataFrame(common_b)
      new = pd.DataFrame(new)
      removed = pd.DataFrame(removed)

      result = common_b.groupby(['College Code', 'College Name']).apply(
        lambda group : group.assign(
            n=common_a[common_a['College Code']==group['College Code'].iloc[0]]['Total'].iloc[0],
                Difference=group['Total'].iloc[0] - common_a[common_a['College Code']==group['College Code'].iloc[0]]['Total'].iloc[0]
            )
        ).reset_index(level=[2], drop=True).drop(columns=['College Code', 'College Name']).reset_index()
      
      result = pd.concat([result, removed, new], ignore_index=True).sort_values(by=['College Code']).reset_index(drop=True)
      
      result = result.rename(
            columns={
                'n' : 'N-1',
                'Total' : 'N'
            }
        )[['College Code', 'College Name', 'N-1', 'N', 'Difference']]

      
      if st.session_state.get('years'):
        if st.session_state.years.get('N-1') and st.session_state.years.get('N'):
          result = result.rename(
            columns={
                'N-1' : st.session_state.years['N-1'],
                'N' : st.session_state.years['N']
            }
          )

      return result


    def form5(a, b):
      
      a = TotalCollegeBranch(a)
      b = TotalCollegeBranch(b)

      removed = []
      new = []
      common_a = []
      common_b = []

      for college_code in a['College Code'].unique():
        for ind, row in a[a['College Code'] == college_code].iterrows():
          if row['Branch Code'] not in list(b[b['College Code'] == college_code]['Branch Code']):
            removed_row = row.copy()
            removed_row['Total'] = 0
            removed_row['n'] = st.session_state.a.filter(college_code=removed_row['College Code'], branch_code=removed_row['Branch Code'])[communities].sum().sum()
            removed_row['Difference'] = removed_row['Total'] - removed_row['n']
            removed.append(removed_row)
          else:
            common_a.append(row.copy())

      for college_code in b['College Code'].unique():
        for ind, row in b[b['College Code'] == college_code].iterrows():
          if row['Branch Code'] not in list(a[a['College Code'] == college_code]['Branch Code']):
            new_row = row.copy()
            new_row['Total'] = st.session_state.b.filter(college_code=new_row['College Code'], branch_code=new_row['Branch Code'])[communities].sum().sum()
            new_row['n'] = 0
            new_row['Difference'] = new_row['Total'] - new_row['n']
            new.append(new_row)
          else:
            common_b.append(row.copy())

      common_a = pd.DataFrame(common_a)
      common_b = pd.DataFrame(common_b)
      new = pd.DataFrame(new)
      removed = pd.DataFrame(removed)

      result = common_b.groupby(['College Code', 'College Name', 'Branch Code', 'Branch Name']).apply(
        lambda group : group.assign(
            n=common_a[(common_a['College Code']==group['College Code'].iloc[0]) & (common_a['Branch Code']==group['Branch Code'].iloc[0])]['Total'].iloc[0],
            Difference=group['Total'].iloc[0] - common_a[(common_a['College Code']==group['College Code'].iloc[0]) & (common_a['Branch Code']==group['Branch Code'].iloc[0])]['Total'].iloc[0]
        )
        ).reset_index(level=[4], drop=True).drop(columns=['College Code', 'College Name', 'Branch Code', 'Branch Name']).reset_index()
      
      result = pd.concat([result, new, removed], ignore_index=True).sort_values(by=['College Code', 'Branch Code']).reset_index(drop=True)
      
      result = result.rename(
            columns={
                'n' : 'N-1',
                'Total' : 'N'
            }
        )[['College Code', 'College Name', 'Branch Code', 'Branch Name', 'N-1', 'N', 'Difference']]
      
      if st.session_state.get('years'):
        if st.session_state.years.get('N-1') and st.session_state.years.get('N'):
          result = result.rename(
            columns={
                'N-1' : st.session_state.years['N-1'],
                'N' : st.session_state.years['N']
            }
          )

      return result
    
    def color_row(row):
      row_color = [''] * len(row)
      if row['Difference'] > 0:
          row_color = ['background-color: lightgreen'] * len(row)
      elif row['Difference'] < 0:
          row_color = ['background-color: red'] * len(row)
      
      if row['2023'] == 0:
          row_color = ['background-color: green'] * len(row)
      if row['2024'] == 0:
          row_color = ['background-color: blue'] * len(row)

      return row_color



    if not st.session_state.get('a') and not st.session_state.get('b'):
      st.session_state.a = SeatMatrix('Inputs/a.xlsx')
      st.session_state.b = SeatMatrix('Inputs/b.xlsx')

      st.session_state.form4 = form4(st.session_state.a, st.session_state.b)
      st.session_state.form5 = form5(st.session_state.a, st.session_state.b)



    with st.sidebar:
      st.session_state.form = st.selectbox(
        label='Select Form',
        options=['Form 4', 'Form 5']
      )

    if st.session_state.get('form'):
      if st.session_state.form == 'Form 4':
        st.session_state.filtered = st.session_state.form4.copy()
        bound = st.container(border=True)
        left, check1, right = bound.columns([0.4, 0.135, 0.3])

        college_name = left.text_input('Enter College Name', placeholder='Enter College Name')
        check1.write('')
        check1.write('')
        starts_with = check1.toggle('Starts With', value=False)
        college_code = int()

        try:
          college_code = right.text_input('Enter College Code', placeholder='Enter College Code')
          if college_code != '':
            college_code = int(college_code)
        except:
          st.error('College Code is an Integer.')


        if college_name != '':
          if starts_with == True:
            st.session_state.filtered = st.session_state.filtered[st.session_state.filtered['College Name'].str.lower().str.startswith(college_name.lower())]
          else:
            st.session_state.filtered = st.session_state.filtered[st.session_state.filtered['College Name'].str.lower().str.contains(college_name.lower())]

        if college_code:
          st.session_state.filtered = st.session_state.filtered[st.session_state.filtered['College Code'].astype(str).str.startswith(str(college_code))]


      elif st.session_state.form == 'Form 5':
        st.session_state.filtered = st.session_state.form5.copy()

        bound = st.container(border=True)
        _college_name, sw_toggle, _college_code = bound.container().columns([0.4, 0.135, 0.3])

        college_name = _college_name.text_input('Enter College Name', placeholder='Enter College Name')
        sw_toggle.write('')
        sw_toggle.write('')
        c_starts_with = sw_toggle.toggle('Starts With', value=False)
        college_code = int()

        try:
          college_code = _college_code.text_input('Enter College Code', placeholder='Enter College Code')
          if college_code != '':
            college_code = int(college_code)
        except:
          st.error('College Code is an Integer.')


        _branch_name, sw_toggle, _branch_code = bound.container().columns([1, 0.3, 0.8])

        branch_name = _branch_name.text_input('Enter Branch Name', placeholder='Enter Branch Name')
        sw_toggle.write('')
        sw_toggle.write('')
        b_starts_with = sw_toggle.toggle('Starts With ', value=False)
        branch_code = _branch_code.text_input('Enter Branch Code', placeholder='Enter Branch Code')



        if college_name != '':
          if c_starts_with == True:
            st.session_state.filtered = st.session_state.filtered[st.session_state.filtered['College Name'].str.lower().str.startswith(college_name.lower())]
          else:
            st.session_state.filtered = st.session_state.filtered[st.session_state.filtered['College Name'].str.lower().str.contains(college_name.lower())]

        if college_code:
          st.session_state.filtered = st.session_state.filtered[st.session_state.filtered['College Code'].astype(str).str.startswith(str(college_code))]

        if branch_name != '':
          if b_starts_with == True:
            st.session_state.filtered = st.session_state.filtered[st.session_state.filtered['Branch Name'].str.lower().str.startswith(branch_name.lower())]
          else:
            st.session_state.filtered = st.session_state.filtered[st.session_state.filtered['Branch Name'].str.lower().str.contains(branch_name.lower())]

        if branch_code:
          st.session_state.filtered = st.session_state.filtered[st.session_state.filtered['Branch Code'].astype(str).str.startswith(str(branch_code))]


    if type(st.session_state.get('filtered')) == pd.DataFrame:
      #st.dataframe(st.session_state.filtered,use_container_width=True)
      styled_df = st.session_state.filtered.style.apply(color_row, axis=1)
      st.dataframe(styled_df, use_container_width=True)
      csv = st.session_state.filtered.to_csv(index=False)
      st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='filtered_data.csv',
                mime='text/csv',
            )
    
  except:
    st.warning("Uploads All Files and Commit properly Before Viewing")
