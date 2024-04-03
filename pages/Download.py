import streamlit as st
import pandas as pd
import numpy as np
import io
from copy import deepcopy
from streamlit_extras.stylable_container import stylable_container 

with stylable_container(
                key="restart_button",
                css_styles="""
                    button {
                        background-color: SteelBlue;
                        color: white;
                        border-radius: 30px;
                        height: 40px;
                        width: 200px;
                    }
                    """,
            ):
            restart = st.button('Back to the upload page',key='restart_button')

if restart:
    for key in st.session_state.keys():
        st.switch_page('Upload.py')


def scriptToNLine(input, n):
    quotient = len(input)//n
    output = ''
    for i in range(quotient+1):
        start = i*n
        if i == quotient:
            output += input[start:]
        else:
            output += input[start:(i+1)*n] + '\n'
    print(output)
    return output

st.title('Download Cleaned Data')

for key, value in st.session_state['tables_original'].items():
    st.divider()
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.header(key)
    with col2:
         file_name = st.text_input('File name',value=key,key='file_name'+key)
         file_format = st.selectbox('File format',['csv','txt','json','excel'],key='file_format'+key)
    with col3:
        with stylable_container(
                key="Download "+key,
                css_styles="""
                    button {
                        background-color: SteelBlue;
                        color: white;
                        border-radius: 30px;
                        height: 55px;
                        width: 250px;
                    }
                    """,
            ):
            if file_format == 'csv':
                st.download_button(
                    label="Download "+file_name+' as csv',
                    data=value.to_csv(index=False).encode('utf-8'),
                    file_name=file_name+'.'+file_format
                )
            elif file_format == 'txt':
                st.download_button(
                    label="Download "+file_name+' as txt',
                    data=value.to_csv(index=False).encode('utf-8'),
                    file_name=file_name+'.'+file_format
                )
            elif file_format == 'json':
                st.download_button(
                    label="Download "+file_name+' as json',
                    data=value.to_json().encode('utf-8'),
                    file_name=file_name+'.'+file_format
                )
            elif file_format == 'excel':
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    value.to_excel(writer, sheet_name=key)
                    writer.save()
                    st.download_button(
                        label="Download "+file_name+' as excel',
                        data=buffer,
                        file_name=file_name+'.xlsx'
                    )

st.divider()

st.subheader('All scripts')

scripts = ''
for i in st.session_state['steps_archived']:
    for j in i:
        scripts += j.script + '\n\n'

st.code(scripts,language='python')
