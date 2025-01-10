import streamlit as st
from exa_py import Exa

st.title("Web Article Search")

try:
    EXA_API_KEY = st.secrets["EXA_AI_API_KEY"]
    exa = Exa(api_key=EXA_API_KEY)
except KeyError:
    st.error("Please configure your Exa AI API key in Streamlit Secrets.")
    st.stop()


def perform_search():
    with st.spinner("Searching the web..."):
        try:
            results = exa.search(st.session_state.search_query, type="auto", num_results=5)
            print("#############")
            print(results)
            st.session_state.search_results = results.results  # Store the list of results
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.search_results = None

st.text_input("Enter your search query:", key="search_query", on_change=perform_search, label_visibility="visible")

if "search_results" in st.session_state and st.session_state.search_results:
    st.subheader("Search Results:")
    for result in st.session_state.search_results:
        title = result.title
        url = result.url
        if url:
            st.markdown(f"- [{title}]({url})")
        else:
            st.write(f"- {title} (URL not available)")
elif "search_results" in st.session_state and st.session_state.search_results is None and st.session_state.search_query:
    st.warning("No results found.")
elif "search_results" in st.session_state and st.session_state.search_query:
    pass # Do nothing, waiting for the first search