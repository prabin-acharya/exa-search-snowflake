import streamlit as st
from exa_py import Exa
from datetime import datetime
from typing import List, Optional


# Initialize Snowflake connection
connection = st.connection("snowflake")

# Initialize Exa client
def init_exa_client() -> Optional[Exa]:
    try:
        EXA_API_KEY = st.secrets["EXA_AI_API_KEY"]
        return Exa(api_key=EXA_API_KEY)
    except KeyError:
        st.error("Please configure your Exa AI API key in Streamlit Secrets.")
        return None


def search_with_Exa(exa_client: Exa, query: str) -> List:
    try:
        results = exa_client.search_and_contents(query, type="auto", num_results=5, text=True)

        print("##################################+")
        print(results.results[0])
        
        return results.results
    except Exception as e:
        st.error(f"Search error: {e}")
        return []


def insert_articles_to_snowflake(articles: List) -> None:
    if not articles:
        return

    # Using context manager for the connection
    with connection.cursor() as cursor:
        try:
            insert_query = """
            INSERT INTO articles (title, text, url, published_date) 
            VALUES (?, ?, ?, ?)
            """

            # Prepare batch data
            batch_data = [
                (
                    article.title,
                    article.text,
                    article.url,
                    article.published_date
                    if hasattr(article, 'published_date') else None
                )
                for article in articles
            ]

            # Execute batch insert
            cursor.executemany(insert_query, batch_data)
            
            # Commit using the connection instance
            connection._instance.commit()
            st.success(f"{len(batch_data)} articles successfully inserted into Snowflake.")            
        except Exception as e:
            connection._instance.rollback()
            st.error(f"Error inserting articles: {e}")  



def main():
    st.title("Web Article Search")

    # Initialize Exa client
    exa_client = init_exa_client()
    if not exa_client:
        st.stop()

    # Search input
    search_query = st.text_input("Enter your search query:", key="search_query", 
                                label_visibility="visible")

    # search with Exa when query is entered
    if search_query:
        with st.spinner("Searching the web..."):
            results = search_with_Exa(exa_client, search_query)
            st.session_state.search_results = results

    #  save and display results
    if "search_results" in st.session_state and st.session_state.search_results:
        articles = st.session_state.search_results
        insert_articles_to_snowflake(articles)

        st.subheader("Search Results:")
        for result in articles:
            title = result.title
            url = getattr(result, 'url', None)
            if url:
                st.markdown(f"- [{title}]({url})")
            else:
                st.write(f"- {title} (URL not available)")

    elif "search_results" in st.session_state and st.session_state.search_query:
        st.warning("No results found.")

if __name__ == "__main__":
    main()



# if st.button("Search"):
#     perform_search()

# if st.session_state.search_query:
#     perform_search()