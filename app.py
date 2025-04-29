import streamlit as st
import pandas as pd
import openai

# Set your OpenAI API Key
openai.api_key = 'YOUR_OPENAI_API_KEY'

st.title("🧠 Autoagent Client File Analyzer")

st.write("Upload a client tax or payment file (.csv or .xlsx) and get AI mapping suggestions!")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

if uploaded_file:
    # Read the file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
except pd.errors.ParserError:
    uploaded_file.seek(0)  # Reset file pointer
    df = pd.read_csv(uploaded_file, delimiter='\t')  # Try tab-delimited
    else:
        df = pd.read_excel(uploaded_file)

    st.write("### Preview of Uploaded File", df.head())

    # Button to trigger AI analysis
    if st.button("🔍 Analyze File"):
        # Prepare prompt
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

        # Call OpenAI GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You help Autoagent integrators understand client tax data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )

        # Display results
        result = response['choices'][0]['message']['content']
        st.write("### 📝 AI Mapping Suggestions")
        st.text(result)

        # Option to download result
        st.download_button("📥 Download Mapping Suggestions", result, file_name="mapping_suggestions.txt")

