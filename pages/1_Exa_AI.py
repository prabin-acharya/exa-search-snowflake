import streamlit as st
from exa_py import Exa
from datetime import datetime


# Initialize Snowflake connection
connection = st.connection("snowflake")

# Initialize Exa client
try:
    EXA_API_KEY = st.secrets["EXA_AI_API_KEY"]
    exa = Exa(api_key=EXA_API_KEY)
except KeyError:
    st.error("Please configure your Exa AI API key in Streamlit Secrets.")
    st.stop()

st.title("Web Article Search")


def perform_search():
    with st.spinner("Searching the web..."):
        try:
            results = exa.search_and_contents(st.session_state.search_query, type="auto", num_results=5, text=True)
            
            print("##################################+")
            print(results.results[0])
        
            st.session_state.search_results = results.results  # Store the list of results
        except Exception as e:
            st.error(f"An error occurred: {e}")
            st.session_state.search_results = None


# Function to insert data into Snowflake
def insert_articles_to_snowflake(connection, articles):
    cursor = connection.cursor()

    try:
        # Prepare the insert query
        insert_query = """
        INSERT INTO articles (title, text, url, published_date) 
        VALUES (?, ?, ?, ?)
        """

        # Insert articles
        for article in articles:
            # Convert the article to tuple
            data = (
                article.title,
                article.text,
                article.url,
                datetime.strptime(article.published_date, "%Y-%m-%dT%H:%M:%S.%fZ") 
                )
            
            cursor.execute(insert_query, data)
        

        connection._instance.commit()
        st.success("Articles successfully inserted into Snowflake.")
    except Exception as e:
        connection._instance.rollback()
        st.error(f"Error inserting articles: {e}")
    finally:
        cursor.close()    

st.text_input("Enter your search query:", key="search_query", label_visibility="visible")



# if st.button("Search"):
#     perform_search()

if st.session_state.search_query:
    perform_search()


if "search_results" in st.session_state and st.session_state.search_results:
    articles = st.session_state.search_results
    insert_articles_to_snowflake(connection, articles)


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