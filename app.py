import streamlit as st
from pathlib import Path
import sqlite3
from sqlalchemy import create_engine
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from langchain_groq import ChatGroq

st.set_page_config(page_title="LangChain: Chat with SQL DB", page_icon="🦜")
st.title("Chat with SQL DB using LangChain and Groq LLM")

# Options
LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = ["Use SQLite3 Database - student.db", "Connect to your MySQL Database"]

selected_opt = st.sidebar.radio(
    label="Choose the DB which you want to chat",
    options=radio_opt
)

# MySQL Inputs
if radio_opt.index(selected_opt) == 1:
    db_uri = MYSQL
    mysql_host = st.sidebar.text_input("MySQL Host", value="localhost")
    mysql_user = st.sidebar.text_input("MySQL User", value="root")
    mysql_password = st.sidebar.text_input("MySQL Password", type="password")
    mysql_db = st.sidebar.text_input("MySQL Database", value="titanic_db")
else:
    db_uri = LOCALDB

# API Key
api_key = st.sidebar.text_input("Groq API Key", type="password")

if not api_key:
    st.info("Please add the Groq API key")
    st.stop()

# LLM
llm = ChatGroq(
    groq_api_key=api_key,
    model_name="llama-3.1-8b-instant",
    streaming=True
)

# DB Configuration
@st.cache_resource(ttl="2h")
def configure_db():
    if db_uri == LOCALDB:
        dbfilepath = (Path(__file__).parent / "student.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))

    elif db_uri == MYSQL:
        if not (mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("Please provide all MySQL connection details.")
            st.stop()

        return SQLDatabase.from_uri(
            f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:3307/{mysql_db}",
            include_tables=["titanic"]   # 🔥 restrict to correct table
        )

# Initialize DB
db = configure_db()

# Debug (optional - can remove later)
st.sidebar.write("Tables:", db.get_usable_table_names())

# Toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Prompt Prefix
prefix = """
You are an SQL assistant.
Always generate correct SQL queries based on the database schema.
Return only the final answer.
"""

# Agent (ONLY ONE)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    prefix=prefix,
    verbose=True,
    handle_parsing_errors=True
)

# Chat Memory
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"}
    ]

# Display chat
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# User Input
user_query = st.chat_input("Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        callback = StreamlitCallbackHandler(st.container())

        response = agent.invoke(
            {"input": user_query},
            config={"callbacks": [callback]}
        )

        output = response.get("output", str(response))

        st.session_state.messages.append({
            "role": "assistant",
            "content": output
        })

        st.write(output)