import streamlit as st
import pandas as pd
import openai
import csv

# Initialize OpenAI client with secure key
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🧠 Autoagent Client File Analyzer")
st.write("Upload a client tax or payment file (.csv or .xlsx) and get AI mapping suggestions!")

uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # === Handle CSV files ===
        if uploaded_file.name.endswith('.csv'):
            uploaded_file.seek(0)
            sample = uploaded_file.read(2048).decode('utf-8', errors='ignore')
            uploaded_file.seek(0)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)

            df = pd.read_csv(
                uploaded_file,
                delimiter=dialect.delimiter,
                quoting=csv.QUOTE_MINIMAL,
                on_bad_lines='skip'  # Requires pandas >= 1.3.0
            )

        # === Handle Excel files ===
        else:
            df = pd.read_excel(uploaded_file)

        # === Show Preview ===
        st.write("### Preview of Uploaded File")
        st.dataframe(df.head())

        # === GPT Mapping Analysis ===
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

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # ✅ works for all users
                messages=[
                    {"role": "system", "content": "You help Autoagent integrators understand client tax data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )

            result = response.choices[0].message.content
            st.write("### 📝 AI Mapping Suggestions")
            st.text(result)

            st.download_button("📥 Download Mapping Suggestions", result, file_name="mapping_suggestions.txt")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
