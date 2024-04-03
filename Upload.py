import streamlit as st
import pandas as pd

def transformUploadedData(files, tables:dict):
    for f in files:
        if f.name[f.name.index('.')+1:] == 'csv':
            data = pd.read_csv(f)
        elif f.name[f.name.index('.')+1:] == 'excel':
            data = pd.read_excel(f)
        elif f.name[f.name.index('.')+1:] == 'txt':
            data = pd.read_csv(f, delimiter='\t')
        elif f.name[f.name.index('.')+1:] == 'json':
            data = pd.read_json(f)
        file_name = f.name[0:f.name.index('.')]
        tables[file_name] = data
    return tables

if 'tables_original' not in st.session_state:
    st.session_state['tables_original'] = {}

st.set_page_config(
    page_title="Data Transformation Playground",
    layout="wide",
    initial_sidebar_state='collapsed'
)

st.title('Data Transformation')

st.divider()

col1, col2, col3 = st.columns([2,1,1])

with col1:
    st.session_state['tables_original'] = transformUploadedData(st.file_uploader("Choose a CSV file", accept_multiple_files=True, label_visibility='collapsed'),st.session_state['tables_original'])

with col3:
    table_name = st.radio(
        "Uploaded data files",
        list(st.session_state['tables_original'].keys()),
        index=None,
    )

st.divider()

p1, p2, p3, p4 = st.columns([1,1,5,1])

with p1:
    preview_from = st.selectbox('top_or_bottom',['Top','Bottom'], label_visibility='collapsed')
with p2:
    preview_size = st.number_input('preview_size',min_value=1,step=1,value=5,label_visibility='collapsed')
with p4:
    if table_name is None:
        delete = st.button('Delete', disabled=True)
    else:
        delete = st.button('Delete')

if delete:
    del st.session_state['tables_original'][table_name]
    st.rerun()

if table_name is not None:
    if preview_from == 'Top':
        st.write(st.session_state['tables_original'][table_name].head(preview_size))
    else:
        st.write(st.session_state['tables_original'][table_name].tail(preview_size))

st.write("##")

b1, b2, b3 = st.columns([3,2,3])

with b2:
    transform = st.button('Start transformation')

if transform:
    st.switch_page('pages/Transformation.py')
