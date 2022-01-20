import streamlit as st
from neo4j_utils import Neo4jConnection
from dotenv import load_dotenv
import os

# SETUP
#############################################################################
load_dotenv()
uri = os.environ['AURA_URI']
user = os.environ['AURA_USER']
password = os.environ['AURA_PASSWORD']
neo4j_utils = Neo4jConnection(
    uri=uri, user=user, pwd=password)


# @st.cache - Doesn't work for calls against driver
def get_keywords(lower_threshold):
    keywords_query = f"""
    MATCH (w:Word)-[r:CONTAINS]-(v:Video)
    WHERE r.number >= {lower_threshold}
    RETURN w.name AS name
    """
    words = neo4j_utils.query(keywords_query)
    result = [word.value('name') for word in words]
    return result


# SIDEBAR
#############################################################################
st.sidebar.markdown(
    "<font color=\"grey\">*Filter Options*</font>", unsafe_allow_html=True)
lower_threshold = st.sidebar.slider(
    "Minimum occurance of keyword in a video", 1, 10, 5, 1)

# MAIN
#############################################################################
st.title("AuraDB Video Recommendations")
st.markdown(
    "<font color=\"grey\">*Want to learn more about Neo4j's Free AuraDB? Choose a selection of keywords from transcripts to get a list of the best videos you should watch!*</font>", unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)

keywords = get_keywords(lower_threshold)
selection = st.multiselect(
    "Enter or Select keywords you're interested in", keywords)

query = f"""
MATCH (v:Video)-[r:CONTAINS]->(w:Word)
WHERE ANY(word IN w.name WHERE word in {selection}) AND r.number >= {lower_threshold}
RETURN v.title AS title, v.url AS url
"""
results = neo4j_utils.query(query)
st.markdown('<br>', unsafe_allow_html=True)
st.markdown('Video Recommendations:')

if len(results) == 0:
    st.markdown(
        '* <font color=\"red\">Nothing Yet!</font><font color=\"grey\"> Try a different threshold and keywords combination</font>', unsafe_allow_html=True)
for record in results:
    print(f'visualize.py: title: {record.value("title")}')
    st.markdown(
        f"* [{record.value('title')}]({record.value('url')})")
