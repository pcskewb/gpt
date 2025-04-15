import streamlit as st
import pandas as pd
import json
import plotly.express as px
from openai import OpenAI


# Set your OpenAI API key
client = OpenAI(api_key="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")  # Replace with your key

st.set_page_config(page_title="📊 Skewb-GPT Excel Chat", page_icon="🤖", layout="wide")

st.markdown("<h1 style='text-align: center;'>📊 Chat with Skewb-GPT About Your Excel File</h1>", unsafe_allow_html=True)

# Sidebar for Excel upload
with st.sidebar:
    st.header("Upload Excel File")
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success("Excel file uploaded!")
    else:
        df = None

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
    with st.expander("🔍 Preview Excel Data"):
        st.dataframe(df)

    def build_context(dataframe):
        preview = dataframe.to_markdown(index=False)
        return f"""
You are a data assistant. Here's a preview of the user's uploaded Excel data:

{preview}

Answer their questions based only on this data and do not give the approach be more result oriented.

If the user asks for a chart, graph, or visualization, respond ONLY with valid JSON in the following format:
{{
  "type": "bar" | "line" | "scatter" | "pie",
  "title": "Plot Title",
  "x": ["x1", "x2", ...],
  "y": ["y1", "y2", ...]
}}

Only provide JSON in that case no other info. Otherwise, answer normally in text.
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
    col1, col2 = st.columns([8, 1])
    with col1:
        st.text_input("Type your question...", key="input_text", label_visibility="collapsed")
    with col2:
        st.button("Send", on_click=submit, use_container_width=True)

else:
    st.info("📁 Please upload an Excel file to begin chatting.")
