import streamlit as st
from snowflake.cortex import Complete
from snowflake.snowpark import Session

conn = st.connection("snowflake")
df = conn.query("SELECT * FROM mytable;", ttl="10m")
df2 = conn.query("SELECT * FROM mytable;", ttl="10m")

for row in df.itertuples():
    st.write(f"{row.NAME} has a :{row.PET}:")


# ####################################################
session = Session.builder.config("connection_name", "myconnection").create()


st.header("Snowflake AI")


st.write("Question: how do snowflakes get their unique patterns?")

with st.spinner("Searching for an answer..."):
    answer = Complete("mistral-large2", "how do snowflakes get their unique patterns?")
    st.write(answer)

session.close()

