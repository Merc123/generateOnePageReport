import subprocess
# Install or upgrade plotly
subprocess.run(["pip", "install", "--upgrade", "plotly"])
subprocess.run(["pip", "install", "--upgrade", "numpy"])

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# Set up Streamlit UI
st.title("PDF Report Generator")
st.write("This app processes files and generates a PDF report based on provided content.")

# Upload files to a temporary directory
uploaded_files = st.file_uploader("Upload CSV, PNG, HTML, and TXT files", accept_multiple_files=True)
template_file = st.file_uploader("Upload an HTML template for the report", type=['html'])

output_dir = "uploaded_files"
os.makedirs(output_dir, exist_ok=True)

# Save uploaded files to the output directory
if uploaded_files:
    for uploaded_file in uploaded_files:
        with open(os.path.join(output_dir, uploaded_file.name), "wb") as f:
            f.write(uploaded_file.read())
    st.success("Files uploaded successfully.")

# Function to extract text under a specified tag for Analysis
def extract_text_from_analysis_file(file_path, tag):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            if line.strip() == f"[{tag}]":
                return lines[i + 1].strip() if i + 1 < len(lines) else None
    return None

# Generate PDF report
def generate_pdf_report(group, output_dir, output_filename, template_filename, context):
    env = Environment(loader=FileSystemLoader(output_dir))
    template = env.get_template(template_filename)
    html_content = template.render(context)
    HTML(string=html_content).write_pdf(output_filename)
    st.success(f"PDF report generated: {output_filename}")

# Process files and generate a report
if st.button("Generate Report"):
    if template_file:
        template_path = os.path.join(output_dir, template_file.name)
        with open(template_path, "wb") as f:
            f.write(template_file.read())

        files = os.listdir(output_dir)
        groups = set(f.split('.')[0] for f in files if any(f.endswith(ext) for ext in ['.csv', '.png', '.html', '.txt']))
        for group in groups:
            required_extensions = {'.csv', '.png', '.html', '.txt'}
            group_files = set(f for f in files if f.startswith(group) and f.endswith(tuple(required_extensions)))
            if len(group_files) == len(required_extensions):
                st.write(f"Processing group: {group}")
                df_analysis = pd.read_csv(os.path.join(output_dir, f"{group}.csv"))
                data_table1 = df_analysis.to_html(index=False, classes="data-table")
                kpi_data1 = df_analysis[["x1", "y1", "z1", "x2"]].tail(1).to_html(index=False, classes="kpi-table")

                context = {
                    'title_name': extract_text_from_analysis_file(os.path.join(output_dir, f"{group}.txt"), "Title_Name"),
                    'logo_path': os.path.join(output_dir, "logo.png"),
                    'summary_title_name': extract_text_from_analysis_file(os.path.join(output_dir, f"{group}.txt"), "Summary_Title_Name"),
                    'summary_text': extract_text_from_analysis_file(os.path.join(output_dir, f"{group}.txt"), "Summary_Text"),
                    'kpi_title_name': extract_text_from_analysis_file(os.path.join(output_dir, f"{group}.txt"), "KPI_Title_Name"),
                    'kpi_data': kpi_data1,
                    'chart_title_name': extract_text_from_analysis_file(os.path.join(output_dir, f"{group}.txt"), "Chart_Title_Name"),
                    'chart_path': os.path.join(output_dir, f"{group}.png"),
                    'chart_writeup': extract_text_from_analysis_file(os.path.join(output_dir, f"{group}.txt"), "Chart_Writeup"),
                    'datatable_tile_name': extract_text_from_analysis_file(os.path.join(output_dir, f"{group}.txt"), "DataTable_Tile_Name"),
                    'data_table': data_table1,
                    'footer_text': extract_text_from_analysis_file(os.path.join(output_dir, f"{group}.txt"), "Footer_Text"),
                }
                output_filename = os.path.join(output_dir, f"{group}_Annual_Report.pdf")
                generate_pdf_report(group, output_dir, output_filename, template_file.name, context)
    else:
        st.error("Please upload an HTML template.")
