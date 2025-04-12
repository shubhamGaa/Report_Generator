import os
import xlsxwriter
import pandas as pd
import streamlit as st
from collections import defaultdict
 
def process_directory(base_dir):
    VALID_CATEGORIES = ['True', 'False']
    BINS = ['Below_50', '50_70', 'Above_70']
 
    merged_counts = defaultdict(lambda: {
        'True_Total': 0, 'True_Below_50': 0, 'True_50_70': 0, 'True_Above_70': 0,
        'False_Total': 0, 'False_Below_50': 0, 'False_50_70': 0, 'False_Above_70': 0
    })
 
    for category in VALID_CATEGORIES:
        category_path = os.path.join(base_dir, category)
        if not os.path.exists(category_path):
            continue
 
        for class_name in os.listdir(category_path):
            class_path = os.path.join(category_path, class_name)
            if not os.path.isdir(class_path):
                continue
 
            for bin_name in BINS:
                bin_path = os.path.join(class_path, bin_name)
                if not os.path.exists(bin_path):
                    continue
 
                file_count = len([
                    f for f in os.listdir(bin_path)
                    if os.path.isfile(os.path.join(bin_path, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))
                ])
 
                prefix = category + "_"
                merged_counts[class_name][prefix + 'Total'] += file_count
                merged_counts[class_name][prefix + bin_name] += file_count
 
    total_row = {
        'True_Total': 0, 'True_Below_50': 0, 'True_50_70': 0, 'True_Above_70': 0,
        'False_Total': 0, 'False_Below_50': 0, 'False_50_70': 0, 'False_Above_70': 0
    }
 
    for counts in merged_counts.values():
        for key in total_row:
            total_row[key] += counts[key]
 
    return merged_counts, total_row
 
def write_to_excel(merged_counts, total_row, output_file):
    workbook = xlsxwriter.Workbook(output_file)
    worksheet = workbook.add_worksheet("Summary")
 
    header_format = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2'})
    true_format = workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'})
    false_format = workbook.add_format({'bg_color': '#F4CCCC', 'font_color': '#9C0006'})
    total_format = workbook.add_format({'bold': True, 'bg_color': '#FFD966'})
 
    headers = [
        'Class',
        'True_Total', 'True_Below_50', 'True_50_70', 'True_Above_70',
        'False_Total', 'False_Below_50', 'False_50_70', 'False_Above_70'
    ]
    worksheet.write_row(0, 0, headers, header_format)
 
    row = 1
    for class_name in sorted(merged_counts.keys()):
        data = merged_counts[class_name]
        worksheet.write(row, 0, class_name)
        worksheet.write_row(row, 1, [
            data['True_Total'], data['True_Below_50'], data['True_50_70'], data['True_Above_70']
        ], true_format)
        worksheet.write_row(row, 5, [
            data['False_Total'], data['False_Below_50'], data['False_50_70'], data['False_Above_70']
        ], false_format)
        row += 1
 
    worksheet.write(row, 0, 'Total', total_format)
    worksheet.write_row(row, 1, [
        total_row['True_Total'], total_row['True_Below_50'], total_row['True_50_70'], total_row['True_Above_70']
    ], total_format)
    worksheet.write_row(row, 5, [
        total_row['False_Total'], total_row['False_Below_50'], total_row['False_50_70'], total_row['False_Above_70']
    ], total_format)
 
    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:I', 15)
    workbook.close()
 
def preview_excel(file_path):
    df = pd.read_excel(file_path, sheet_name="Summary")
    return df
 
 
# ------------------ Streamlit UI ------------------
 
st.title("📊 Class-wise Image Count Report Generator")
 
base_dir = st.text_input("📂 Enter the folder path to process", value=r"C:\Users\admin\Documents\Test_automte\Test_Data_model_106")
 
if st.button("Generate Excel Report"):
    if os.path.exists(base_dir):
        merged_counts, total_row = process_directory(base_dir)
        output_file = os.path.join(base_dir, "merged_class_table.xlsx")
        write_to_excel(merged_counts, total_row, output_file)
        st.success(f"✅ Excel report generated successfully!")
 
        # Download button
        with open(output_file, "rb") as f:
            st.download_button("📥 Download Excel", f, file_name="merged_class_table.xlsx")
 
        # Preview the Excel file
        st.subheader("🔍 Preview of Excel File")
        df_preview = preview_excel(output_file)
        st.dataframe(df_preview, use_container_width=True)
 
    else:
        st.error("❌ The directory does not exist. Please check the path.")
 
 