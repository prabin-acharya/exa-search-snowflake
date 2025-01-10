import streamlit as st
from exa_py import Exa
from snowflake.snowpark.context import get_active_session
from snowflake.cortex import Complete


# from snowflake.cortex import Complete

# Streamlit and Snowflake setup
st.title("Debate Topic Generator")
st.markdown(
    """
    Enter a debate topic, and this app will generate arguments for both sides 
    using web articles and Snowflake's LLM-powered summarization.
    """
)

# Snowflake session
session = get_active_session()
root = Root(session)

# Exa AI setup
try:
    EXA_API_KEY = st.secrets["EXA_AI_API_KEY"]
    exa = Exa(api_key=EXA_API_KEY)
except KeyError:
    st.error("Please configure your Exa AI API key in Streamlit Secrets.")
    st.stop()


def search_articles(query, num_results=5):
    """
    Search for articles using Exa AI API based on a given query.
    Args:
        query (str): The search query.
        num_results (int): Number of results to fetch.
    Returns:
        list: A list of articles with title, summary, and URL.
    """
    try:
        with st.spinner("Searching for articles..."):
            results = exa.search(query, type="auto", num_results=num_results)
        return results.results
    except Exception as e:
        st.error(f"Error during web search: {e}")
        return []


def mistral_complete(prompt):
    """
    Generate completion using Snowflake's Mistral model.
    Args:
        prompt (str): The prompt to generate a completion for.
    Returns:
        str: The generated completion.
    """
    try:
        result = session.sql(
            "SELECT snowflake.cortex.complete('mistral-large', ?)", [prompt]
        ).collect()
        return result[0][0]
    except Exception as e:
        st.error(f"Error during LLM completion: {e}")
        return ""


def summarize_articles(articles, position):
    """
    Use Mistral LLM to summarize the articles and generate arguments for a position.
    Args:
        articles (list): List of articles (title, summary, and URL).
        position (str): Either "pro" or "con".
    Returns:
        str: AI-generated arguments.
    """
    # Combine the articles into a single prompt
    article_context = "\n".join(
        f"- {a['title']} ({a['url']})" for a in articles if 'url' in a
    )
    prompt = f"""
    You are an AI assistant that generates arguments for a debate. Below are some articles and their content related to a topic. Your job is to create a detailed and succinct argument in favor of or against the topic.

    Topic: "{st.session_state.debate_topic}"

    Position: {position.upper()}

    Articles:
    {article_context}

    Provide your arguments below, formatted as concise and impactful points:
    """
    with st.spinner(f"Generating {position.upper()} arguments..."):
        return mistral_complete(prompt)


def generate_debate():
    """
    Main function to handle debate generation workflow.
    """
    articles = search_articles(st.session_state.debate_topic)
    if not articles:
        st.warning("No articles found. Try a different topic.")
        return

    st.session_state.articles = articles

    pro_arguments = summarize_articles(articles, "pro")
    con_arguments = summarize_articles(articles, "con")

    st.session_state.pro_arguments = pro_arguments
    st.session_state.con_arguments = con_arguments


# Input for debate topic
st.text_input(
    "Enter a debate topic:",
    key="debate_topic",
    on_change=generate_debate,
    label_visibility="visible",
)

# Display results
if "articles" in st.session_state:
    st.subheader("Top Articles:")
    for article in st.session_state.articles:
        title = article["title"]
        url = article.get("url", "URL not available")
        st.markdown(f"- [{title}]({url})")

if "pro_arguments" in st.session_state and "con_arguments" in st.session_state:
    st.subheader("Debate Arguments")

    st.markdown("### Arguments in Favor:")
    st.markdown(st.session_state.pro_arguments or "No arguments generated.")

    st.markdown("### Arguments Against:")
    st.markdown(st.session_state.con_arguments or "No arguments generated.")
