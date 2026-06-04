import streamlit as st
import os
import time
import json
from groq import Groq

# ================== Page Config ==================
st.set_page_config(
    page_title="Gesner Deslandes AI Agent Builder",
    page_icon="🤖",
    layout="wide"
)

# ================== Custom CSS (Branded Light Purple Theme) ==================
st.markdown("""
<style>
    /* Light lavender background throughout the app and sidebar */
    .stApp, [data-testid="stSidebar"] {
        background-color: #E6E6FA !important;
    }
    
    /* Sidebar border adjustment */
    [data-testid="stSidebar"] {
        border-right: 3px solid #8A2BE2;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label, [data-testid="stSidebar"] h2 {
        color: #333333 !important;
    }
    
    /* Elegant Dark Violet Typography */
    h1, h2, h3, h4 { color: #4B0082 !important; font-weight: bold; }
    p, li, span, .stMarkdown { color: #111111 !important; }
    
    /* White-Glass Cards for Content Blocks */
    .metric-card, .debugger-card, .agent-card {
        background: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #8A2BE2;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    
    /* Custom CSS alignment wrapper for Title & Avatar */
    .title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin-bottom: 5px;
    }
    .title-avatar {
        border-radius: 50%;
        width: 75px;
        height: 75px;
        border: 3px solid #8A2BE2;
        object-fit: cover;
    }
    
    /* Code box styling */
    pre {
        background-color: #f4f4f9 !important;
        border: 1px solid #ddd !important;
        border-radius: 8px !important;
    }
    
    /* Primary buttons */
    .stButton>button {
        background-color: #8A2BE2 !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background-color: #4B0082 !important;
        border-color: #4B0082 !important;
    }
    
    /* Main footer design */
    .main-footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1.5rem;
        border-top: 2px solid #8A2BE2;
        color: #4B0082 !important;
        font-weight: bold;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ================== Asset Configurations ==================
GITHUB_AVATAR_URL = "https://github.com/Deslandes1.png"
has_groq = "GROQ_API_KEY" in st.secrets

# ================== Tool Definitions for Simulator ==================
# Simple deterministic helper python tools representing the Agent's environment
def tool_translation_haiti(text, target_lang):
    """Translates Haitian Creole text into English, Spanish, or French."""
    translations = {
        "english": {
            "enjenyè": "engineer",
            "pwofesè": "teacher",
            "lojisyèl": "software",
            "kòd": "code",
            "kreyòl": "Creole"
        },
        "french": {
            "enjenyè": "ingénieur",
            "pwofesè": "professeur",
            "lojisyèl": "logiciel",
            "kòd": "code",
            "kreyòl": "créole"
        },
        "spanish": {
            "enjenyè": "ingeniero",
            "pwofesè": "profesor",
            "lojisyèl": "software",
            "kòd": "código",
            "kreyòl": "criollo"
        }
    }
    target = target_lang.lower().strip()
    words = text.lower().replace(".", "").replace(",", "").split()
    translated_words = []
    
    if target in translations:
        for word in words:
            translated_words.append(translations[target].get(word, f"[{word}]"))
        return " ".join(translated_words)
    return f"Translation target '{target_lang}' not supported by tool."

def tool_accent_detector(text):
    """Analyzes text and catches common missing grave accents (È/Ò) in Creole words."""
    corrections = []
    text_lower = text.lower()
    if "enjenye" in text_lower and "enjenyè" not in text_lower:
        corrections.append("Correction: Changed 'enjenye' to 'enjenyè' (Missing È grave accent).")
    if "pwofese" in text_lower and "pwofesè" not in text_lower:
        corrections.append("Correction: Changed 'pwofese' to 'pwofesè' (Missing È grave accent).")
    if "lojisyel" in text_lower and "lojisyèl" not in text_lower:
        corrections.append("Correction: Changed 'lojisyel' to 'lojisyèl' (Missing È grave accent).")
    if "kod" in text_lower and "kòd" not in text_lower:
        corrections.append("Correction: Changed 'kod' to 'kòd' (Missing Ò grave accent).")
    
    if corrections:
        return "\n".join(corrections)
    return "No missing grave accents detected in Creole keywords."

# ================== Sidebar Brand Panel ==================
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 15px;">
        <img src="{GITHUB_AVATAR_URL}" style="border-radius: 50%; width: 110px; border: 3px solid #8A2BE2;">
        <h2 style="margin-top: 10px; font-size: 1.4rem; font-weight: bold;">GlobalInternet.py</h2>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    if has_groq:
        st.success("⚡ Groq API Connected!")
    else:
        st.warning("⚠️ Groq Key missing in Secrets. Running Simulation Mode.")
        
    st.header("⚙️ Agent Settings")
    temperature = st.slider("Agent Temperature (Creativity vs Determinism)", 0.0, 1.0, 0.1, step=0.05)
    model_name = st.selectbox("LLM Core Engine:", ["llama3-8b-8192", "mixtral-8x7b-32768"])
    
    st.markdown("---")
    st.markdown("### 👨‍💻 Creator profile")
    st.markdown("**Enjenyè-an-Chèf:** GESNER DESLANDES")
    st.markdown("📱 (509) 4738 5663")
    st.markdown("[Visit Website](https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/)")

# ================== Main Window Rendering ==================
st.markdown(f"""
<div class="title-container">
    <h1>Gesner Deslandes AI Agent Builder</h1>
    <img class="title-avatar" src="{GITHUB_AVATAR_URL}">
</div>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; font-size: 1.2rem; font-style: italic; color: #333333;'>Design, Validate, and Deploy AI Agents Using the Core Principles of Simple Agent Architecture</p>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #8A2BE2 !important; letter-spacing: 1px; font-weight: bold;'>BUILT BY GESNER DESLANDES FOR GLOBALINTERNET.PY</h4>", unsafe_allow_html=True)
st.markdown("---")

# ================== Rule 1: Task Evaluation Panel ==================
st.markdown("## 1️⃣ Rule 1: Don't Build Agents for Everything")
st.markdown("Before writing complex loops, verify if your task actually requires an agent, or if it can be mapped via standard Python workflows.")

col_input, col_eval = st.columns(2)

with col_input:
    st.markdown("#### Evaluate Your Next Task")
    task_desc = st.text_area("What is the goal of your automation/agent?", value="Correct spelling and accents in Creole video transcripts, translate them, and format them directly as an SRT file.", height=100)
    
    # Simple interactive scorecard mapping to Rule 1 variables
    q1 = st.checkbox("Is the execution flow too ambiguous to map with standard if/else statements?", value=True)
    q2 = st.checkbox("Does the output format require natural language reasoning or contextual decisions?", value=True)
    q3 = st.checkbox("Does the task require choosing between multiple external interfaces/tools dynamically?", value=False)
    q4 = st.checkbox("Can this task be solved with 100% deterministic code? (If yes, map the workflow instead)", value=False)

with col_eval:
    st.markdown("#### Automation Recommendation Matrix")
    
    # Scoring algorithm based on check boxes
    score = 0
    if q1: score += 30
    if q2: score += 30
    if q3: score += 40
    if q4: score -= 50
    
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown(f"### Design Recommendation Score: **{score}/100**")
    
    if score >= 60:
        st.success("🎯 **VERDICT: Build an AI Agent.** This task involves high ambiguity, dynamic tool requirements, or variable natural language output. It cannot be easily scripted.")
    elif score >= 20:
        st.info("🔄 **VERDICT: Build a Hybrid Chain.** Use structured prompting or standard APIs sequentially rather than letting an agent run free in tool loops.")
    else:
        st.error("🛑 **VERDICT: Use standard Python scripts.** Save money and compute! This task can be mapped directly. Map the workflow.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ================== Rule 2 & 3: Interactive Sandbox ==================
st.markdown("## 2️⃣ Rules 2 & 3: Simple Loop Design & Context Debugger")
st.markdown("An agent is merely a model inside a loop with access to a specific **Context**, **System Instructions**, and a **Set of Tools**.")

col_sandbox, col_terminal = st.columns([1.1, 1])

# Base Context we inject explicitly to limit hallucinations
system_prompt_template = (
    "You are an AI Agent designed by Engineer Gesner Deslandes for GlobalInternet.py.\n"
    "Your environment has access to exactly two tools:\n"
    "1. translation_tool(text, target_lang) - translates keywords 'enjenyè', 'pwofesè', 'lojisyèl', 'kòd', 'kreyòl'\n"
    "2. accent_corrector(text) - analyzes Creole accents for È and Ò words.\n\n"
    "Respond using JSON format only:\n"
    "{\n"
    "  \"thought\": \"your reasoning process\",\n"
    "  \"tool_to_use\": \"tool_name or None\",\n"
    "  \"tool_input\": \"parameters\",\n"
    "  \"final_answer\": \"the final result\"\n"
    "}"
)

with col_sandbox:
    st.markdown("#### Configure Agent Workspace Environment")
    
    # Custom system instruction input
    system_instructions = st.text_area("Agent System Prompt (Context Boundaries):", value=system_prompt_template, height=180)
    
    # Define current active tools
    st.markdown("**Active Tools in Workspace:**")
    st.code("🔧 translation_tool (target_lang, text)\n🔧 accent_corrector (text)")
    
    # User query
    user_query = st.text_input("Simulate User Query Input:", value="Check accents for 'pwofese' and translate 'lojisyel' to English.")
    
    run_agent = st.button("🚀 Execute Model-Tool Loop")

with col_terminal:
    st.markdown("#### 🔍 What the Agent Sees (Raw Context)")
    
    # Visually represents Rule 3 ("Woud I know what to do if I only saw what the agent sees?")
    st.markdown('<div class="debugger-card">', unsafe_allow_html=True)
    st.markdown("**RAW PROMPT TO LLM ARCHITECTURE:**")
    debug_context = {
        "ROLE": "SYSTEM INSTRUCTIONS",
        "CONTEXT_PROMPT": system_instructions,
        "INPUT_QUERY": user_query,
        "BOUNDARIES": "Respond using JSON matching defined format. No other words outside JSON container."
    }
    st.json(debug_context)
    st.markdown('</div>', unsafe_allow_html=True)

# Loop Execution Logic
if run_agent:
    st.markdown("---")
    st.markdown("## ⚙️ Execution Loop (ReAct Phase Trace)")
    
    if not has_groq:
        # Simulation Mode Trace (Shows step-by-step loop as described in Anthropic design principles)
        with st.status("Running Model-Tool Loop Simulation...", expanded=True) as status:
            st.write("🔄 **Step 1: Ingesting Raw Context & System Prompt...**")
            time.sleep(1.0)
            st.write("💭 **Step 2: LLM Reasoning thought generation...**")
            
            simulated_thought = {
                "thought": "The user wants me to do two things. First, check accents for 'pwofese'. Second, translate 'lojisyel' to English. I should run the accent_corrector tool first.",
                "tool_to_use": "accent_corrector",
                "tool_input": "pwofese",
                "final_answer": ""
            }
            st.json(simulated_thought)
            time.sleep(1.2)
            
            st.write("🛠️ **Step 3: Triggering Active Environment Tool...**")
            tool_output = tool_accent_detector("pwofese")
            st.code(f"Tool Output: {tool_output}")
            time.sleep(1.0)
            
            st.write("💭 **Step 4: Feeding Tool Output back into Context Loop...**")
            simulated_thought_2 = {
                "thought": "The accent correction caught 'pwofesè'. Now I need to translate 'lojisyèl' to English using translation_tool.",
                "tool_to_use": "translation_tool",
                "tool_input": {"text": "lojisyèl", "target_lang": "english"},
                "final_answer": ""
            }
            st.json(simulated_thought_2)
            time.sleep(1.2)
            
            tool_output_2 = tool_translation_haiti("lojisyèl", "english")
            st.code(f"Tool Output: {tool_output_2}")
            time.sleep(0.8)
            
            st.write("🎯 **Step 5: Synthesizing Final Answer...**")
            final_res = {
                "thought": "I have successfully analyzed accents and performed translation with all tools executed.",
                "tool_to_use": "None",
                "tool_input": "None",
                "final_answer": "Accents correction: Changed 'pwofese' to 'pwofesè'. Translation of 'lojisyèl' is 'software'."
            }
            st.json(final_res)
            
            status.update(label="Simulation Loop Finished Successfully!", state="complete")
            
            st.markdown('<div class="agent-card">', unsafe_allow_html=True)
            st.markdown("### 🏆 Simulated Agent Response")
            st.success(final_res["final_answer"])
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        # Live Run Mode utilizing actual Groq Engine
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        with st.spinner("Executing Real-Time Agent reasoning on Groq platform..."):
            try:
                # Step 1: Query LLM for Tool Choice
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_query}
                    ],
                    model=model_name,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                
                raw_json = response.choices[0].message.content
                agent_decisions = json.loads(raw_json)
                
                st.markdown("### 🧠 Live LLM Agent Reasoning Trace")
                st.json(agent_decisions)
                
                # Step 2: Handle Tool Execution Dynamically
                tool_selected = agent_decisions.get("tool_to_use")
                tool_param = agent_decisions.get("tool_input")
                
                if tool_selected == "accent_corrector":
                    tool_result = tool_accent_detector(str(tool_param))
                elif tool_selected == "translation_tool":
                    if isinstance(tool_param, dict):
                        tool_result = tool_translation_haiti(tool_param.get("text", ""), tool_param.get("target_lang", "english"))
                    else:
                        tool_result = tool_translation_haiti(str(tool_param), "english")
                else:
                    tool_result = "No tools triggered by LLM core decision matrix."
                
                st.markdown("### 🛠️ Execution Observation Output")
                st.code(f"Observation Result: {tool_result}")
                
                # Step 3: Synthesis of final result with observation context added
                synthesis_prompt = f"The tool output from execution is: '{tool_result}'. Now compile the final clean response to the user."
                
                final_response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": user_query},
                        {"role": "assistant", "content": raw_json},
                        {"role": "user", "content": synthesis_prompt}
                    ],
                    model=model_name,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                
                final_output_json = json.loads(final_response.choices[0].message.content)
                
                st.markdown('<div class="agent-card">', unsafe_allow_html=True)
                st.markdown("### 🏆 Live Agent Final Answer Output")
                st.success(final_output_json.get("final_answer", "Processing Completed Successfully."))
                st.markdown('</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")

# Bottom Branding Footer
st.markdown('<div class="main-footer">© GlobalInternet.py – Built by GESNER DESLANDES.</div>', unsafe_allow_html=True)
