import streamlit as st
import pandas as pd
import json
import plotly.express as px
from openai import OpenAI
from dotenv import load_dotenv
import os
import re
import base64
import streamlit.components.v1 as components



load_dotenv()  # This loads the .env file into your current environment

# st.set_page_config(layout="centered")

   # Access the environment variables using os.environ
#    database_url = os.environ.get("DATABASE_URL")
api_key = os.environ.get("api_key")

# Set your OpenAI API key
client = OpenAI(api_key=api_key)  # Replace with your key

with open("skewb-logomark 3.png", "rb") as image_file:
    encoded = base64.b64encode(image_file.read()).decode()

st.set_page_config(page_title="SkewbGPT ", layout="centered")


favicon_html = f"""
<link rel="icon" type="image/png" href="data:image/png;base64,{encoded}">
"""
components.html(favicon_html, height=0, width=0)

# st.markdown("<h1 style='text-align: center;'>SkewbGPT </h1>", unsafe_allow_html=True)
html_code = f"""
<h1 style='text-align: center; padding:0 px'>
    <img src='data:image/png;base64,{encoded}' alt='logo' style='height: 40px; vertical-align: middle; margin-right: 10px;'>
    SkewbGPT
</h1>
"""

st.markdown(html_code, unsafe_allow_html=True)

# Sidebar for Excel upload
with st.sidebar:
    st.header("Upload Excel File")

    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    st.markdown("---")

    use_default = st.button("📊 optimizer_equations_with_demo_sigmoids.xlsx")

    # Load the dataframe
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success("Excel file uploaded!")
    elif use_default:
        df = pd.read_excel("optimizer_equations_with_demo_sigmoids.xlsx")
        st.success("Using sample Excel file!")
    else:
        df = pd.read_excel("optimizer_equations_with_demo_sigmoids.xlsx")
        st.success("Using sample Excel file!")
        

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# Custom CSS for chat bubbles
st.markdown("""
    <style>
        .chat-bubble {
            padding: 10px 15px;
            border-radius: 15px;
            margin-bottom: 10px;
            max-width: 80%;
            word-wrap: break-word;
        }
        .user-bubble {
            background-color: #000000;
            margin-left: auto;
            text-align: right;
            color: white;
        }
        .bot-bubble {
            background-color: #d6ff41;
            margin-right: auto;
            text-align: left;
            color: black;
        }
        
        .chat-container {
            height: 10vh;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }
            
        .stVerticalBlock{
            padding: 0px !important;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        .stTextInput>div>div>input {
            border-radius: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Show DataFrame preview
if df is not None:
    # with st.expander("🔍 Preview Excel Data"):
    #     st.dataframe(df)

    def build_context(dataframe):
        preview = dataframe.to_markdown(index=False)
        return f"""
You are a data assistant. Here's a preview of the user's uploaded Excel data:

{preview}

Answer their questions based only on this data and do not give the approach be more result oriented.

GPT PROMPT TRAINING INSTRUCTIONS  
Purpose: Guide GPT to answer marketing mix modeling (MMM) questions using sigmoid response curves from Excel.

FORMULAS

%% Change in Sales from Current Point:
growth = gsf * [(1 - exp(-coef * new_spend / csf)) - (1 - exp(-coef * current_spend / csf))]

Contribution:
contribution = gsf * (1 - exp(-coef * spend / csf))

ROI:
roi = (total_sales * gsf * (1 - exp(-coef * spend / csf))) / spend

RULES FOR GPT

- Always use parameters (coef, csf, gsf, current_spend, new_spend, sales) from the Excel file.
- Do not show code unless asked.
- Explain results simply using business terms.
- Avoid technical jargon or API references.

CORE TASKS

1. Optimal Channel Reallocation  
Prompt: Reallocate total current budget for best sales outcome.  
Output:  
Optimal Spend Allocation Summary:  
- Total Spend Kept Constant: ₹197.08 Cr  
- Expected Incremental Growth: 8.2 percent  
- Incremental Sales: ₹91.1 Cr

Channel Changes:  
YouTube: Increase by 8 Cr → 28.41 Cr  
CRM: Decrease by 5 Cr → 2.11 Cr  

Top ROI Gainers:  
YouTube – ROI: 6.2  
Meta – ROI: 5.1  
TV – ROI: 4.7

Recommendation:  
Divert spends from low ROI channels (CRM) to high ROI ones (YouTube, Meta, TV)

2. Incremental ROI by Channel  
Prompt: What is ROI if I add 10 Cr to YouTube?  
Output:  
Incremental Sales: ₹23 Cr  
Incremental ROI: 6.1  
Growth Percent: 10.5

3. Contribution Analysis  
Prompt: Which channels contribute most today?  
Output: Contribution per channel as percent of total



5. Growth Waterfall
Prompt: Move 10 Cr from CRM to YouTube.
Output:
Loss from CRM
Gain in YouTube
Net change
Growth and ROI impact

6. Target-Based Optimization
Prompt: I want 15 percent growth. What budget and allocation?
Output:
Required total spend, spend per channel, expected ROI

7. Scenario Simulation
Prompt: What if I reduce 5 Cr from all channels?
Output:
Sales loss, ROI impact, suggested adjustments

8. Channel Recommendation
Prompt: Where to invest next 10 Cr?
Output:
Incremental Spend Comparison:

YouTube:
Incremental Sales: ₹23 Cr
ROI: 6.1
Growth: 10.5

Meta:
Incremental Sales: ₹19 Cr
ROI: 5.3
Growth: 8.5

Recommendation:
Prefer YouTube for better returns

3
TV – ROI: 5.0

Channel Allocation for Reduced Budget:
YouTube: ₹24.5 Cr
Meta: ₹26.5 Cr
TV: ₹21.9 Cr
Amazon: ₹18.2 Cr
Influencer: ₹15.8 Cr
Google: ₹12.5 Cr
Flipkart: ₹9.7 Cr
OTT Others: ₹5.4 Cr
Hotstar: ₹4.8 Cr
CRM: ₹2.0 Cr
Remaining Channels: Balance to complete ₹167.51 Cr

RESPONSE CURVE DETAILS
X-axis: Spends in Cr
Y-axis: Percent change in sales

...

EXCLUSIONS  
- Do not show equations or programming code unless asked  
- Use exact values from Excel

If the user asks for a chart, graph, or visualization, respond with valid JSON in the following format: 

this is just format only a example, labels values and all other factors will vary according to asked query
[
  {{
    "type": "line" | "bar" | ...,
    "title": "title",
    "labels": ["label1", "label2",....],
    "values": {{
      "series1": [100, 110,...],
      "series2": [100, 130,...],
      ....
    }},
    "x_title": "x title",
    "y_title": "y title"
  }},
  {{
    "type": "bar",
    "title": "title",
    "labels": ["label1", "label2",...],
    "values": {{
      "series1": [300, 400, 500,...],
      "series2": [30, 45, 60,...],
      ....
    }},
    "x_title": "x title",
    "y_title": "y title"
  }}
]


and do not give formula in any series.
"""




    def submit():
        user_input = st.session_state.input_text.strip()
        if user_input == "":
            return

        context = build_context(df)

        messages = [{"role": "system", "content": context}]
        for pair in st.session_state.chat_history:
            messages.append({"role": "user", "content": pair["question"]})
            messages.append({"role": "assistant", "content": pair["answer"]})
        messages.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages
                )

                print("response:",response)
                answer = response.choices[0].message.content.strip()
                st.session_state.chat_history.append({
                    "question": user_input,
                    "answer": answer
                })
                st.session_state.input_text = ""
                # st.rerun()
            except Exception as e:
                st.error(f"❌ API Error: {str(e)}")

    # Show chat history with custom bubbles and optional plots
    # Show chat history with custom bubbles and optional plots
    st.subheader("💬 Conversation")
    for chat in st.session_state.chat_history:
        st.markdown(f'<div class="chat-bubble user-bubble"><strong>You:</strong><br>{chat["question"]}</div>', unsafe_allow_html=True)

        # Initialize response_text outside the try block
        response_text = chat["answer"]
        json_string = None
        plot_created = False
        
        try:
            # Look for JSON in markdown code blocks
            if '```json' in response_text:
                json_string = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                # Try without explicit json marker
                json_string = response_text.split('```')[1].split('```')[0].strip()
            else:
                # Fallback: try to extract a raw JSON object from the text using regex
                match = re.search(r'{[\s\S]*?}', response_text)
                if match:
                    json_string = match.group(0)


            print("json_string:", json_string)
            
            if json_string:
                # Try to parse the JSON
                json_string = re.sub(r'//.*', '', json_string)

                chart_data = json.loads(json_string)
                
                # After json.loads(json_string)
                charts = chart_data if isinstance(chart_data, list) else [chart_data]

                for chart in charts:
                    if not all(k in chart for k in ("type", "title", "labels", "values")):
                        continue

                    x_vals = chart["labels"]
                    y_vals = chart["values"]
                    title = chart["title"]
                    x_title = chart.get("x_title", "")
                    y_title = chart.get("y_title", "")
                    chart_type = chart["type"]

                    fig = None

                    if isinstance(y_vals, dict):  # Multiple series
                        df = pd.DataFrame({**{"labels": x_vals}, **y_vals})
                        df_long = df.melt(id_vars="labels", var_name="Series", value_name="values")

                        if chart_type == "line":
                            fig = px.line(df_long, x="labels", y="values", color="Series", title=title)
                        elif chart_type == "bar":
                            fig = px.bar(df_long, x="labels", y="values", color="Series", title=title, barmode="group")
                        elif chart_type == "scatter":
                            fig = px.scatter(df_long, x="labels", y="values", color="Series", title=title)
                    else:  # Single series
                        if chart_type == "line":
                            fig = px.line(x=x_vals, y=y_vals, title=title)
                        elif chart_type == "bar":
                            fig = px.bar(x=x_vals, y=y_vals, title=title)
                        elif chart_type == "scatter":
                            fig = px.scatter(x=x_vals, y=y_vals, title=title)
                        elif chart_type == "pie":
                            fig = px.pie(names=x_vals, values=y_vals, title=title)

                    if fig:
                        fig.update_layout(xaxis_title=x_title, yaxis_title=y_title)
                        st.plotly_chart(fig, use_container_width=True)
                        plot_created = True

        except Exception as e:
            st.error(f"Error processing response: {str(e)}")
    
    # If no plot was created, display the full response as text
        if not plot_created:
            st.markdown(f'<div class="chat-bubble bot-bubble"><strong>Skewb-GPT:</strong><br>{response_text}</div>', unsafe_allow_html=True)
    
    
    # Input section
    st.markdown("---")
    st.subheader("💬 Ask Something")
    with st.form(key='my_form'):
        col1, col2 = st.columns([5, 1])
        with col1:
            input_text = st.text_input(
                "Type your question...", 
                key="input_text", 
                label_visibility="collapsed"
            )
        with col2:
            submitted = st.form_submit_button(
                "Send", 
                on_click=submit, 
                use_container_width=True
            )
        
        # This will trigger when either the button is clicked or Enter is pressed
        if submitted:
            submit()  # Call your submit function

else:
    st.info("📁 Please upload an Excel file to begin chatting.")
