# input_handler.py
import pandas as pd
import logging

def get_user_input():
    debugging = 0
    try:
        with open("input.txt") as f:
          #print("open.0")
          for x in f:
            #x = x.lower()
            if "Date_From =" in x:
                start_value = x.split("=")[1].split(" ")[1:3]
                start_value = start_value[0] + ' ' + start_value[1]
                start_value = pd.to_datetime(start_value)
                if debugging == 1:
                    print("date_from")
            
            if "Date_To =" in x:
                #print('date to')
                end_value = x.split("=")[1].split(" ")[1:3]
                end_value = end_value[0] + ' ' +  end_value[1]
                end_value = pd.to_datetime(end_value)
                if debugging == 1:
                    print("date_to")
                
            if "Validation items" in x:
                x.replace("AND", "&")
                x.replace("OR", "|")
                x.replace("\n", "")
                threshold_logic = x.split("items")[1]
                if debugging == 1:
                    print("validation_items")
            if "Threshold_percentage_auto" in x:
                percentage_auto = x.split("=")[1].strip()
                percentage_auto = percentage_auto.split("%")[0]
                percentage_auto = percentage_auto.strip()
                try:
                    percentage_auto = float(percentage_auto)
                except:
                    print("Unknown Threshold_percentage_auto. Please update input.txt")
                if debugging == 1:
                    print("threshold_percentage_auto")
            if "Threshold_percentage_manual" in x:
                percentage_manual = x.split("=")[1].strip()
                percentage_manual = percentage_manual.split("%")[0]
                percentage_manual = percentage_manual.strip()
                try:
                    percentage_manual = float(percentage_manual)
                except:
                    print("Unknown Threshold_percentage_auto. Please update input.txt")
                if debugging == 1:
                    print("threshold_percentage_manual")
            if "Report_Configuration" in x:
                report_config = x.split("=")[1].strip()
                report_config = report_config.split(" ")[0]
                report_config = report_config.strip()
                report_config = int(report_config)
                if report_config not in [1,2,3]:
                    print("unknown report configuration. Please update input.txt")
                if debugging == 1:
                    print("report_configuration")
            if "email addresses" in x:
                emails = x.split("=")[1].strip().split(" ")[0]
                emails = emails.split(";")
                if debugging == 1:
                    print("emails")
                    

        f.close()
        
    except:
        print('Error. input file not found')
    try:
            #print('hi!')
            config = pd.read_excel("Config_Data_new.xlsx")
            oldCols = config.columns
            cols = [value.rstrip() for value in oldCols]
            colDict = {}
            for i in range(len(cols)):
                colDict.update({oldCols[i]: cols[i]})
            config.rename(columns = colDict, inplace=True)
            item_name_list = config.loc[config["Item_Type"] == "Report"]["Item_Name"].to_list()
            report_item_name_list = config[["Item_Name", "Report_Item_Name"]]
            grouped_columns = config.groupby("Grouping")["Item_Name"].apply(list)
            threshold_tags = ['6001.P', '6002.P']
            normal_state = config[["Item_Name", "Normal State"]]
            excluded = config.loc[config["Exclude"] == "Y"]
            #print('end')
            return start_value, end_value, item_name_list, report_item_name_list, threshold_tags, threshold_logic, grouped_columns, normal_state, excluded, config, percentage_auto, percentage_manual, report_config, emails
    except:
            print('Error. Config_Data file not found.')
            

get_user_input()