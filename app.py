import streamlit as st
import pandas as pd
import openai
import csv

# Set your OpenAI API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]


st.title("🧠 Autoagent Client File Analyzer")

st.write("Upload a client tax or payment file (.csv or .xlsx) and get AI mapping suggestions!")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # CSV handling
        if uploaded_file.name.endswith('.csv'):
            uploaded_file.seek(0)
            sample = uploaded_file.read(2048).decode('utf-8')
            uploaded_file.seek(0)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            df = pd.read_csv(uploaded_file, delimiter=dialect.delimiter)
        else:
            # Excel handling
            df = pd.read_excel(uploaded_file)

        # Show preview
        st.write("### Preview of Uploaded File")
        st.dataframe(df.head())

        # Button to trigger AI analysis
        if st.button("🔍 Analyze File"):
            columns = df.columns.tolist()
            sample_data = df.head(5).to_dict(orient='records')

            prompt = f"""
You are a data integration specialist at Autoagent, LLC.

Here are the column names:
{columns}

Here are a few sample rows:
{sample_data}

Suggest what each column most likely represents from this list:
- Parcel Number
- Owner Name
- Amount Due
- Tax Year
- Installment Number
- Payment Amount
- Payment Date

Output as a table: [Client Column Name] | [Suggested Autoagent Field] | [Confidence %].
"""

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You help Autoagent integrators understand client tax data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )

            result = response['choices'][0]['message']['content']
            st.write("### 📝 AI Mapping Suggestions")
            st.text(result)

            st.download_button("📥 Download Mapping Suggestions", result, file_name="mapping_suggestions.txt")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
