import streamlit as st
import pandas as pd
import json
import plotly.express as px
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # This loads the .env file into your current environment

   # Access the environment variables using os.environ
#    database_url = os.environ.get("DATABASE_URL")
api_key = os.environ.get("api_key")

# Set your OpenAI API key
client = OpenAI(api_key=api_key)  # Replace with your key

st.set_page_config(page_title="📊 Skewb-GPT Excel Chat", page_icon="🤖", layout="wide")

st.markdown("<h1 style='text-align: center;'>📊 Chat with Skewb-GPT About Your Excel File</h1>", unsafe_allow_html=True)

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
            background-color: #DCF0FF;
            margin-left: auto;
            text-align: right;
        }
        .bot-bubble {
            background-color: #F0F0F0;
            margin-right: auto;
            text-align: left;
        }
        .chat-container {
            height: 10vh;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
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
{{  
  "type": "bar" | "line" | "scatter" | "pie",  
  "title": "Plot Title",  
  "x": ["x1", "x2", ...],  
  "y": ["y1", "y2", ...]  
}}


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
            
            if json_string:
                # Try to parse the JSON
                chart_data = json.loads(json_string)
                
                if isinstance(chart_data, dict) and all(k in chart_data for k in ("type", "title", "x", "y")):
                    # Display the text part before the JSON (if any)
                    text_part = response_text.split('```')[0].strip()
                    if text_part:
                        st.markdown(f'<div class="chat-bubble bot-bubble"><strong>Skewb-GPT:</strong><br>{text_part}</div>', unsafe_allow_html=True)
                    
                    # Create and display the plot
                    st.markdown(f'<div class="chat-bubble bot-bubble"><strong>Skewb-GPT:</strong><br>Generated Plot:</div>', unsafe_allow_html=True)

                    fig = None
                    if chart_data["type"] == "bar":
                        fig = px.bar(x=chart_data["x"], y=chart_data["y"], title=chart_data["title"])
                    elif chart_data["type"] == "line":
                        fig = px.line(x=chart_data["x"], y=chart_data["y"], title=chart_data["title"])
                    elif chart_data["type"] == "scatter":
                        fig = px.scatter(x=chart_data["x"], y=chart_data["y"], title=chart_data["title"])
                    elif chart_data["type"] == "pie":
                        fig = px.pie(names=chart_data["x"], values=chart_data["y"], title=chart_data["title"])

                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        plot_created = True
                    
                    # Display any text after the JSON (if any)
                    parts = response_text.split('```')
                    if len(parts) > 2:
                        text_part_after = parts[2].strip()
                        if text_part_after:
                            st.markdown(f'<div class="chat-bubble bot-bubble"><strong>Skewb-GPT:</strong><br>{text_part_after}</div>', unsafe_allow_html=True)
                    
                    continue  # Skip the normal text display if we showed a plot
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
