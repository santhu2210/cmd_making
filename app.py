## importing required packages
import os
import pandas as pd
import re

from flask import Flask, render_template, request, json

## pattern for escape characters
pattern = re.compile(r"\\n|\\r|\\t|\\r|\\f|\\b")
#pattern = re.compile(r"\s")


##  Global variable declariation
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = 'data'
XL_FILE = 'NEW_GT_PROJECT.xlsx'
GT_NAME_COLUMN = 'GT_Name'
OPERATOR_1_COLUMN = 'Operator1'
OPERATOR_2_COLUMN='Operator2 '

STATUS_COLUMN_NAME = 'Status'
OUTPUT_COLUMNS = ['Carrier_Name','Switch','TG_Name','Direction','Nop ID','Bharti GW IP','Carrier_IP','Capacity (Circuits)','Status']

''''
E164 = MOD SCCPGT:GTI=GT4,NUMPLAN=ISDN,ADDR=K'370663,GTNM1="OMNLIT",GTGNM="ILD GT",RESULTT=STP3,LSDGNM="GT_2-162-6_2-166-6";
E214 = MOD SCCPGT:GTI=GT4,NUMPLAN=ISDNMOV,ADDR=K'370663,GTNM1="OMNLIT",GTGNM="ILD GT",RESULTT=STP3,LSDGNM="GT_2-162-6_2-166-6";
164 = ADD SCCPGT: GTNM="SLOVE1", NI=INT, GTI=GT4, NUMPLAN=ISDN, ADDR=K'38664, RESULTT=STP3, LSDGNM="GT_2-81-2_2-81-1 ", GTGNM="ILD GT";
214 = ADD SCCPGT: GTNM="SLOVE1", NI=INT, GTI=GT4, NUMPLAN=ISDNMOV, ADDR=K'38664, RESULTT=STP3, LSDGNM="GT_2-81-2_2-81-1 ", GTGNM="ILD GT";

'''


## Initialize flask app 
app = Flask(__name__)


## main or index page routing function
@app.route("/")
def main():
    # keyword = request.args.get('inputKeyword')
    # if keyword:
    #     print("query param keyword: -->", keyword)
    return render_template('index.html')



## Search call rounting function
@app.route('/search', methods=['POST'])
def search():
    # read the posted values from the UI
    keyword = request.form['GTName']
    GT_Name = request.form['GTName']
    Operator1 = request.form['Operator1']
    Operator2 = request.form['Operator2']
    cmd_mode = request.form['cmd_mode']
    print("request data-",request.form )

    InfoDF = pd.DataFrame()

    for sht, df in sheet_to_df_dict.items():
       # try:
            # print("sht name :", sht)
            all_df = df[(df[GT_NAME_COLUMN].str.contains(str(GT_Name),na=False, case=False)) & (df[OPERATOR_1_COLUMN] == Operator1) & (df[OPERATOR_2_COLUMN] == Operator2)]
            # tg_df = df[(df[TG_COLUMN_NAME].str.contains(str(keyword),na=False, case=False)) & (df[STATUS_COLUMN_NAME] == 'LIVE')]
            # ip_df = df[(df[CARRIER_IP_COLUMN_NAME].str.contains(str(keyword),na=False, case=False)) & (df[STATUS_COLUMN_NAME] == 'LIVE')]
            all_df = all_df.astype(str)


            cmd_list = []
            
            for index, row in all_df.iterrows():
                if cmd_mode == 'E164':
                    cmd = "MOD SCCPGT:GTI=GT4,NUMPLAN=ISDN,ADDR=K'"+row['GT_Number']+',GTNM1="OMNLIT",GTGNM="ILD GT",RESULTT=STP3,LSDGNM="'+row['Gateway_SPC']+'";'
                elif cmd_mode == 'E214':
                    cmd = "MOD SCCPGT:GTI=GT4,NUMPLAN=ISDNMOV,ADDR=K'"+row['GT_Number']+',GTNM1="OMNLIT",GTGNM="ILD GT",RESULTT=STP3,LSDGNM="'+row['Gateway_SPC']+'";'
                elif cmd_mode == '164':
                    cmd = 'ADD SCCPGT: GTNM="SLOVE1", NI=INT, GTI=GT4, NUMPLAN=ISDN, ADDR=K'+"'"+row['GT_Number']+', RESULTT=STP3, LSDGNM="'+row['Gateway_SPC']+'", GTGNM="ILD GT";'
                elif cmd_mode == '214':
                    cmd = 'ADD SCCPGT: GTNM="SLOVE1", NI=INT, GTI=GT4, NUMPLAN=ISDNMOV, ADDR=K'+"'"+row['GT_Number']+', RESULTT=STP3, LSDGNM="'+row['Gateway_SPC']+'", GTGNM="ILD GT";'
                else:
                    pass
                cmd_list.append(cmd)
            
            print('cmd_list',':',cmd_list)

            tempDF = pd.DataFrame()
            print('all_df :', '\n', all_df)
            tempDF = pd.concat([all_df])

            if len(tempDF) > 0:
                InfoDF= InfoDF.append(tempDF, ignore_index = True) 
                #InfoDF = pd.concat([InfoDF,tempDF])

        # except Exception as e:
        #     print(e)

    # print('InfoDF',InfoDF.OUTPUT_COLUMNS)
    pd.set_option('display.max_colwidth', -1)
    pd.options.display.float_format = '{:,.0f}'.format

    if len(InfoDF) > 0:
        req_df = InfoDF[OUTPUT_COLUMNS]#.iloc[:,0:9]
        # df.a = df.a.astype(float)
    else:
        req_df = pd.DataFrame()

    tables_html=[req_df.to_html(classes="table table-striped table-bordered search-data ", index=False, header="true")]

    # print(json.dumps(req_df.to_dict('records')))

    if len(tables_html[0]) > 450 :
        search_result = remove_escape_characters(tables_html[0])

    else:
        search_result = '<h4> No result found.. </h4>'

    return (search_result)


## helping functions to remove escape characters
def remove_escape_characters(string):
    #processed_string = string.encode('ascii', 'ignore').decode('unicode_escape') if isinstance(string, str) else string
    processed_string = string

    cleaned_string = pattern.sub(", ", str(processed_string))
    return cleaned_string

## helping functions to read excel file read
def read_xls(test_file):
    # df_one = pd.read_excel(test_file, sheet_name=None)
    # print(df_one.head())
    xls = pd.ExcelFile(test_file)
    all_sheet_names = xls.sheet_names

    ## to read all sheets to a map
    sheet_to_df_dict = {}
    for sheet_name in all_sheet_names:
        sheet_to_df_dict[sheet_name] = xls.parse(sheet_name)

    return sheet_to_df_dict


test_file_path = os.path.join(BASE_DIR, DATA_DIR, XL_FILE)
sheet_to_df_dict = read_xls(test_file_path)


## main function
if __name__ == "__main__":
    app.run(debug=True, host= '0.0.0.0', port=5556)

