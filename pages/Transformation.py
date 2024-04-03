import streamlit as st
import pandas as pd
import numpy as np
from copy import deepcopy
from streamlit_extras.stylable_container import stylable_container 


if 'steps' not in st.session_state:
    st.session_state['steps'] = []

if 'steps_archived' not in st.session_state:
    st.session_state['steps_archived'] = []

st.session_state['tables'] = deepcopy(st.session_state['tables_original'])

class transformation:
    def __init__(self, table_name):
        self.table_name = table_name
        self.action_list = ['Sort','Append','Filter','Join','Derived Column','Data Type Conversion', 'Aggregation', 'Drop Column']
        self.action = ''
        self.script = ''

    def getInput(self,key):
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            action = st.selectbox('Transformation',self.action_list,key='transformation'+str(key), index=None)
        with col2:
            if action is not None:
                self.action = action
                # sort
                if action == 'Sort':
                    transform = self.sortObj(self.table_name)
                    if transform.getSortInput(key):
                        self.script = transform.execSort()
                # drop
                elif action == 'Drop Column':
                    transform = self.dropObj(self.table_name)
                    if transform.getDropInput(key):
                        self.script = transform.execDrop()

                # append
                elif action == 'Append':
                    transform = self.appendObj(self.table_name)
                    if transform.getAppendInput(key):
                        self.script = transform.execAppend()
                
                # join 
                elif action == 'Join':
                    transform = self.joinObj(self.table_name)
                    if transform.getJoinInput(key):
                        self.script = transform.execJoin()

                # data type conversion
                elif action == 'Data Type Conversion':
                    transform = self.dTypeConversionObj(self.table_name)
                    if transform.getDTypeConversionInput(key):
                        self.script = transform.execDTypeConversion()

                # aggregation
                elif action == 'Aggregation':
                    transform = self.aggregationObj(self.table_name)
                    if transform.getAggregationInput(key):
                        self.script = transform.execAggregation()

                # filter
                elif action == 'Filter':
                    transform = self.filterObj(self.table_name)
                    if transform.getFilterInput(key):
                        self.script = transform.execFilter()
                
                # derived column
                else:
                    transform = self.derivedColumnObj(self.table_name)
                    if transform.getDerivedColumnInput(key):
                        self.script = transform.execDerivedColumn()

        with col3:
            st.code(language='python', body=scriptToNLine(self.script,44))

    # sub transformation class
    class sortObj:
        def __init__(self, table_name):
            self.table_name = table_name
            self.columnsAsc = []
            self.columnsDesc = []
        
        def getSortInput(self,key):
            columnsAsc = st.multiselect('Ascending', list(st.session_state['tables'][self.table_name].columns), key='sortasc'+str(key))
            columnsDesc = st.multiselect('Descending', list(set(st.session_state['tables'][self.table_name].columns)-set(columnsAsc)), key='sortdesc'+str(key))
            self.columnsAsc = columnsAsc
            self.columnsDesc = columnsDesc
            if self.columnsAsc != [] and self.columnsDesc != []:
                return True
            else:
                return False
        
        def execSort(self):
            asc = [True]*len(self.columnsAsc)+[False]*len(self.columnsDesc)
            script = """st.session_state['tables']['""" + self.table_name + """'].sort_values(by=""" + str(self.columnsAsc+self.columnsDesc) + """,ascending=""" + str(asc) + """,inplace=True)"""
            exec(script)
            return script.replace("st.session_state['tables']['"+ self.table_name +"']",self.table_name)

    class dropObj:
        def __init__(self, table_name):
            self.table_name = table_name
            self.columnDrop = []
        
        def getDropInput(self,key):
            columnDrop = st.multiselect('Columns to drop', list(st.session_state['tables'][self.table_name].columns), key='drop'+str(key))
            self.columnDrop = columnDrop
            if self.columnDrop != []:
                return True
            else:
                return False
        
        def execDrop(self):
            script = """st.session_state['tables']['""" + self.table_name + """'].drop(""" + str(self.columnDrop) + """,axis=1,inplace=True)"""
            exec(script)
            return script.replace("st.session_state['tables']['"+ self.table_name +"']",self.table_name)

    class appendObj:
        def __init__(self, table_name):
            self.table_name = table_name
            self.tablesAppend = []
        
        def getAppendInput(self,key):
            tablesAppend = st.multiselect('Tables to append', list(st.session_state['tables'].keys()), key='append'+str(key))
            self.tablesAppend = tablesAppend
            if self.tablesAppend != []:
                return True
            else:
                return False
        
        def execAppend(self):
            table_list = [self.table_name]+deepcopy(self.tablesAppend)
            for i in range(len(table_list)):
                table_list[i] = "st.session_state['tables']['" + table_list[i] + "']"
            script = "st.session_state['tables']['" + self.table_name + "']=pd.concat(" + str(table_list).replace('"','') + ").reset_index().drop('index',axis=1)"
            exec(script)
            return script.replace("st.session_state['tables']['"+ self.table_name +"']",self.table_name)
        
    class joinObj:
        def __init__(self, table_name):
            self.table_name = table_name
            self.tableJoin = ''
            self.leftOn = ''
            self.rightOn = ''
            self.how = ''
        
        def getJoinInput(self,key):
            tableJoin = st.selectbox('Tables to join', list(st.session_state['tables'].keys()), key='join'+str(key))
            self.tableJoin = tableJoin
            leftOn = st.selectbox('Column to join in the left table', list(st.session_state['tables'][self.table_name].columns), key='leftjoin'+str(key))
            rightOn = st.selectbox('Column to join in the right table', list(st.session_state['tables'][self.tableJoin].columns), key='rightjoin'+str(key))
            self.leftOn = leftOn
            self.rightOn = rightOn
            how = st.selectbox('How to join',['inner','left','right','outer','cross'])
            self.how = how
            if self.tableJoin != '' and self.tableJoin != '' and self.leftOn != '' and self.rightOn != '' and self.how != '' and st.session_state['tables'][self.table_name][self.leftOn].dtypes == st.session_state['tables'][self.tableJoin][self.rightOn].dtypes:
                return True
            else:
                return False
        
        def execJoin(self):
            script = "st.session_state['tables']['" + self.table_name + "']=st.session_state['tables']['" + self.table_name + "'].merge(st.session_state['tables']['" + self.tableJoin + "'],how='" + self.how + "',left_on='" + self.leftOn + "',right_on='" + self.rightOn + "')"
            exec(script)
            return script.replace("st.session_state['tables']['"+ self.table_name +"']",self.table_name)

    class dTypeConversionObj:
        def __init__(self, table_name):
            self.table_name = table_name
            self.dtypes_list = []
            self.allDtypes = ['Integer (int)','Float (float)','String (string)','Boolean (bool)','Datetime (datetime64[ns])','Object (object)']
            self.columns = []
        
        def getDTypeConversionInput(self,key):
            columns = st.session_state['tables'][self.table_name].columns
            self.columns = columns
            self.dtypes_list = ['']*len(columns)
            for i in range(len(columns)):
                current_dtypes = str(st.session_state['tables'][self.table_name][columns[i]].dtypes)
                current_dtypes = dTypesLookUp(current_dtypes)
                self.dtypes_list[i] = st.selectbox('Data type of '+columns[i], self.allDtypes, index=current_dtypes, key='dtype'+str(key)+columns[i])
            if self.dtypes_list != ['']*len(columns):
                return True
            else:
                return False
        
        def execDTypeConversion(self):
            script = "{"
            for i in range(len(self.columns)):
                if i > 0:
                    script += ','
                script += "'" + self.columns[i] + "':'" + getValueInParam(self.dtypes_list[i]) + "'"
            script = "st.session_state['tables']['" + self.table_name + "']=st.session_state['tables']['" + self.table_name + "'].astype(" + script + "})"
            exec(script)
            return script.replace("st.session_state['tables']['"+ self.table_name +"']",self.table_name)
        
    class aggregationObj:
        def __init__(self, table_name):
            self.table_name = table_name
            self.groupby_column = ''
            self.agg_list = []
            self.allAggTypes = ['Sum (sum)','Max (max)','Min (min)','Median (median)','Mean (mean)','Mode (mode)','Count (count)','Standard Deviation (std)','Variance (var)','Skewness (skew)','Kurtosis (kurt)']
            self.columns = []
        
        def getAggregationInput(self,key):
            columns = list(st.session_state['tables'][self.table_name].columns)
            self.groupby_column = st.selectbox('Group by',columns)
            columns.remove(self.groupby_column)
            self.columns = columns
            self.agg_list = [[]]*len(columns)
            for i in range(len(columns)):
                self.agg_list[i] = st.multiselect('Aggregation on '+columns[i], self.allAggTypes, key='agg'+str(key)+columns[i])
            if self.agg_list != [[]]*len(columns) and self.groupby_column != '':
                return True
            else:
                return False
        
        def execAggregation(self):
            script = ".groupby('" + self.groupby_column + "').agg("
            for i in range(len(self.columns)):
                if len(self.agg_list[i]) > 0:
                    for j in range(len(self.agg_list[i])):
                        if i > 0 or j > 0:
                            script += ','
                        script += self.columns[i] + "_" + getValueInParam(self.agg_list[i][j]) + "=pd.NamedAgg(column='" + self.columns[i] + "',aggfunc='" + getValueInParam(self.agg_list[i][j]) + "')"
            script = "st.session_state['tables']['" + self.table_name + "']=st.session_state['tables']['" + self.table_name + "']" + script + ").reset_index()"
            exec(script)
            return script.replace("st.session_state['tables']['"+ self.table_name +"']",self.table_name)
        
    class filterObj:
        def __init__(self, table_name):
            self.table_name = table_name
            self.columns = []
            self.sign = ['Greater than (>)','Greater than or equal to (>=)','Smaller than (<)','Smaller than or equal to (<=)','Equal to (==)','Not equal to (!=)','In','Not in']
            self.options = ['none','and','or']
            self.option = ''
            self.conditions = []
            self.signs = []
        
        def getFilterInput(self,key):
            columns = list(st.session_state['tables'][self.table_name].columns)
            column1 = st.selectbox('Column to filter',columns,key='filtercolumn1'+str(key))
            sign1 = st.selectbox('Sign',self.sign,key='filtersign1'+str(key))
            condition1 = st.text_input('Condition',key='filtercondition1'+str(key),help='Writing the condition might need to coding background. 1. String should be enclosed by quotation marks. 2. List should be enclosed by square bracket. 3. Check the consistency of the sign and the condition.')
            self.option = st.radio('One or two conditions',self.options,label_visibility='collapsed')
            self.conditions.append(condition1)
            self.signs.append(getValueInParam(sign1))
            self.columns.append(column1)
            if self.option in ['and','or']:
                column2 = st.selectbox('Column to filter',columns,key='filtercolumn2'+str(key))
                sign2 = st.selectbox('Sign',self.sign,key='filtersign2'+str(key))
                condition2 = st.text_input('Condition',key='filtercondition2'+str(key))
                self.conditions.append(condition2)
                self.signs.append(getValueInParam(sign2))
                self.columns.append(column2)
                if self.columns != [] and self.option != '' and self.columns[1] != ''  and self.conditions[1] != '' and self.signs[1] != '':
                    return True
                else:
                    return False
            if self.columns != [] and self.option != '' and self.columns !=  [''] and self.conditions != [''] and self.signs != ['']:
                return True
            else:
                return False
        
        def execFilter(self):
            if self.option == 'none':
                script = "st.session_state['tables']['" + self.table_name + "']=st.session_state['tables']['" + self.table_name + "'][st.session_state['tables']['" + self.table_name + "']." + self.columns[0] + self.signs[0] + self.conditions[0] + "]"
            elif self.option == 'and':
                script = "st.session_state['tables']['" + self.table_name + "']=st.session_state['tables']['" + self.table_name + "'][np.logical_and(st.session_state['tables']['" + self.table_name + "']." + self.columns[0] + self.signs[0] + self.conditions[0] + ",st.session_state['tables']['" + self.table_name + "']." + self.columns[1] + self.signs[1] + self.conditions[1] +")]"
            else:
                script = "st.session_state['tables']['" + self.table_name + "']=st.session_state['tables']['" + self.table_name + "'][np.logical_or(st.session_state['tables']['" + self.table_name + "']." + self.columns[0] + self.signs[0] + self.conditions[0] + ",st.session_state['tables']['" + self.table_name + "']." + self.columns[1] + self.signs[1] + self.conditions[1] +")]"
            exec(script)
            return script.replace("st.session_state['tables']['"+ self.table_name +"']",self.table_name)
        
    class derivedColumnObj:
        def __init__(self, table_name):
            self.table_name = table_name
            self.new_existing = ''
            self.column = ''
            self.derivedOperation = ''
        
        def getDerivedColumnInput(self,key):
            columns = list(st.session_state['tables'][self.table_name].columns)
            self.new_existing = st.radio('Create or modify',['Create new column','Modify existing column'],key='new_existing'+str(key),label_visibility='collapsed')
            if self.new_existing == 'Create new column':
                self.column = st.text_input('New column name')
            else:
                self.column = st.selectbox('Column to derive',columns,key='derivedColumn'+str(key))
            self.derivedOperation = st.text_input('Operation')
            if self.new_existing != '' and self.column != '' and self.derivedOperation != '':
                return True
            else:
                return False 
        
        def execDerivedColumn(self):
            script = "st.session_state['tables']['" + self.table_name + "']['" + self.column + "']="
            for i in st.session_state['tables'][self.table_name].columns:
                if i in self.derivedOperation:
                    self.derivedOperation = self.derivedOperation.replace(i,"st.session_state['tables']['" + self.table_name + "']['" + i + "']")
            script += self.derivedOperation
            exec(script)
            return script.replace("st.session_state['tables']['"+ self.table_name +"']",self.table_name)

def dTypesLookUp(dtype:str):
    input = dtype[:3]
    if input == "int":
        return 0
    elif input == 'flo':
        return 1
    elif input == 'str':
        return 2
    elif input == 'boo':
        return 3
    elif input == "dat":
        return 4
    elif input == 'obj':
        return 5
    else:
        print('--------------------------')
        print('Error on input data type!!!')
        print('--------------------------')

def getValueInParam(input):
    return input[input.index('(')+1:input.index(')')]

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

st.title('Data Transformation')

st.divider()

table_name = st.selectbox(
        "Data to transform",
        list(st.session_state['tables'].keys()),
        index=None,
)
st.divider()

for i in range(len(st.session_state['steps'])):
    st.session_state['steps'][i].getInput(i)
    st.divider()

b1, b2, b3, b4 = st.columns([1,5,6,1])

with b1:
    add = st.button('add')

with b3:
    confirm = st.button('confirm')

with b4:
    if len(st.session_state['steps']) == 0:
        remove = st.button('delete',disabled=True)
    else:
        remove = st.button('delete')

if add:
    st.session_state['steps'].append(transformation(table_name))
    st.rerun()

if confirm:
    st.session_state['tables_original'][table_name] = st.session_state['tables'][table_name]
    st.session_state['steps_archived'].append(st.session_state['steps'])
    st.session_state['steps'] = []
    st.rerun()

if remove:
    st.session_state['steps'].pop()
    st.rerun()

st.write("##")

p1, p2, p3 = st.columns([1,1,5])

with p1:
    preview_from = st.selectbox('top_or_bottom',['Top','Bottom'], label_visibility='collapsed')
with p2:
    preview_size = st.number_input('preview_size',min_value=1,step=1,value=5,label_visibility='collapsed')

if table_name is not None:
    if preview_from == 'Top':
        st.write(st.session_state['tables'][table_name].head(preview_size))
    else:
        st.write(st.session_state['tables'][table_name].tail(preview_size))

st.write("##")

r1,r2,r3 = st.columns([1,4,1])

with r3:
    download_cleaned_data = st.button('Download cleaned data')

if download_cleaned_data:
    st.switch_page('pages/Download.py')