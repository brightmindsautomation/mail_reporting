# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 15:51:37 2025


"""

# data_processing.py
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
#import os
#from boolean_parser import parse
from email_sender import send_email
from config import RECIPIENT_EMAILS, FILE_PATH

from input_handler import get_user_input


def filter_excel_rows(start_value, end_value, item_name_list, report_item_name_list, threshold_tags, threshold_logic, grouped_columns, normal_state, excluded, config, percentage_auto, percentage_manual, report_config, emails):
    #threshold_percentage = 80
    df = pd.read_excel(FILE_PATH, header=0, parse_dates=[0]) #read excel file
    df.insert(0, "Datetime", df.pop(df.columns[0])) #insert datetime
    
    validation_tags = config.loc[config["Item_Type"] == "Validation"]["Item_Name"].values #the tags involved in the logic
    val_dict = {}
    val_dict_rename = {}
    for i in range(len(validation_tags)):
        val_dict.update({validation_tags[i]: "val" + str(i)})
        val_dict_rename.update({"val" + str(i): validation_tags[i]}) #create dictionaries to rename columns since .query() func does not accept col names with periods
        threshold_logic = threshold_logic.replace(validation_tags[i], "val" + str(i)) #replace column names in logic
    threshold_logic = threshold_logic.strip()
    threshold_logic = threshold_logic.replace("AND", "&")
    df.rename(columns = val_dict, inplace = True)
    

    filtered_df = df[(df["Datetime"] >= start_value) & (df["Datetime"] <= end_value)] #select based on dates
    selected_df = filtered_df.query(threshold_logic) #filter df according to logic supplied in Validation items
    selected_df.rename(columns = val_dict_rename, inplace=True) #rename columns
    filtered_df.rename(columns = val_dict_rename, inplace=True)
    df.rename(columns = val_dict_rename, inplace=True)

    #total_points = len(filtered_df)
    up_time_row = {col: 0 for col in selected_df.columns} #initialize UpTime row
    up_time_row["Datetime"] = "Up Time" 

    validation_cols = config.loc[config["Item_Type"] != "Report"]["Item_Name"].values.tolist() #columns to remove based on Item Type

    excluded_columns = set(df.columns) - set(item_name_list)
    excluded_columns = excluded_columns.union(set(excluded["Item_Name"].values.tolist())).union(set(validation_cols))
    percentage_row = {col: 0 for col in selected_df.columns}
    percentage_row["Datetime"] = "Percentage"
    
    percentage_values = []
    grouped_cols = {}
    for i in range(len(grouped_columns)):
        if len(grouped_columns.iloc[i])>1:
            grouped_cols.update({grouped_columns.index[i]: grouped_columns.iloc[i]})
    grouped_columns = grouped_cols
    min_percentage_per_group = {}

    for col in selected_df.columns[1:]:
        if col in excluded_columns:
            continue
        if selected_df[col].dtype == object:
            valid_count = selected_df[col].count()
            total_count = filtered_df[col].count()
            up_time = round((valid_count / total_count) * 100, 2) if total_count > 0 else 0
            up_time_row[col] = up_time
            
            normal = normal_state.loc[normal_state["Item_Name"]==col]["Normal State"].values[0]
            percent_count = (selected_df[col]== normal).sum()

            percentage = round((percent_count * 100) / valid_count, 2) if valid_count > 0 else 0
            percentage_row[col] = percentage
            percentage_values.append(percentage)

            for group, columns in grouped_columns.items():
                if col in columns:
                    if group not in min_percentage_per_group or percentage < min_percentage_per_group[group]:
                        min_percentage_per_group[group] = percentage

    table_data = []
    for col, percentage in percentage_row.items():
        if col not in excluded_columns:
            report_col = report_item_name_list.loc[report_item_name_list["Item_Name"]==col]["Report_Item_Name"].values            
            description = config.loc[config["Item_Name"]==col]["Description"].values
            if len(report_col)>0:
                report_col = report_col[0]
            if len(description)>0:
                description = description[0]
            if col != "Datetime":    
                if report_config == 3:
                    try:
                        filtered_series = report_item_name_list.loc[report_item_name_list["Item_Name"] == col, "Report_Item_Name"].fillna("")
                        if filtered_series.size > 0 and filtered_series.iloc[0].upper().endswith(".SP"):                            
                            # table_data.append([filtered_series.iloc[0], "0"])
                            sp_cols = [col for col in selected_df.columns if col.upper().endswith(".SP")]
                            selected_df = selected_df[sp_cols]
                    except:
                        print('3. error in appending table data3.')                    
                else:                                                
                    if report_config == 1 and percentage >= percentage_auto:
                        try:
                            table_data.append([report_col, description, percentage])
                        except:
                            print('1. error in appending table data.')
                    if report_config == 2 and percentage >= percentage_manual:
                        try:
                            table_data.append([report_col, description, percentage])
                        except:
                            print('2. error in appending table data.')                

    avg_percentage = round(sum(percentage_values) / len(percentage_values), 2) if percentage_values else 0
    if report_config == 3:
        SPchanges = 0
        for col in selected_df.columns:
            SPchanges = (selected_df[col] != selected_df[col].shift(1)).sum() - 1
            table_data.append([col, SPchanges])
        changes_df = pd.DataFrame([SPchanges]).reindex(columns=selected_df.columns)      
        selected_df = pd.concat([selected_df, pd.DataFrame([SPchanges])], ignore_index=True) 
    else:
        selected_df = pd.concat([selected_df, pd.DataFrame([up_time_row]), pd.DataFrame([percentage_row])], ignore_index=True)
    for oldCol, newCol in zip(report_item_name_list["Item_Name"], report_item_name_list["Report_Item_Name"]):
        if oldCol in selected_df.columns:
            selected_df.rename(columns = {oldCol: newCol}, inplace=True)
    
    report_file = "Generated_Report.xlsx"
    report_df = selected_df if report_config == 3 else selected_df.tail(2)
    report_df_t = report_df.transpose()
    report_df_t.to_excel(report_file, index=True, header=False)

    if report_config == 1:
        table_df = pd.DataFrame(table_data, columns=["Item Name", "Description", "Percentage in Auto State"])
    elif report_config == 2:
        table_df = pd.DataFrame(table_data, columns=["Item Name", "Description", "Percentage in Manual State"])
    elif report_config == 3:
        table_df = pd.DataFrame(table_data, columns=["Item Name", "Number of Changes occured"])
        
    if type(emails) == list:
        emails = emails[0]
    send_email(table_df, avg_percentage, emails, report_file)
    
    return selected_df

#start_value, end_value, item_name_list, report_item_name_list, threshold_tags, threshold_logic, grouped_columns, normal_state, excluded, config, percentage_auto, percentage_manual, report_config, emails = get_user_input()
#filter_excel_rows(start_value, end_value, item_name_list,  report_item_name_list,threshold_tags, threshold_logic, grouped_columns, normal_state, excluded, config, percentage_auto, percentage_manual, report_config, emails)