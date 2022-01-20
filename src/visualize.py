import streamlit as st
from neo4j import GraphDatabase
import pandas as pd
import altair as alt
import datetime
from PIL import Image
import keys
from neo4j_utils import Neo4jConnection


# SETUP
#############################################################################
neo4j_utils = Neo4jConnection(
    uri=keys.aura_uri, user=keys.aura_user, pwd=keys.aura_password)


# def load_data(url):
#     data = pd.read_csv(url)
#     def lowercase(x): return str(x).lower()
#     data.rename(lowercase, axis='columns', inplace=True)
#     return data

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
    "Minimum occurance in a video", 1, 10, 5, 1)

# MAIN
#############################################################################
st.title("AuraDB Video Recommendations")
st.markdown(
    "<font color=\"grey\">*Want to learn more about Neo4j's Free AuraDB? Choose a selection of keywords from transcripts to get a list of the best videos you should watch!*</font>", unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)

# words = get_keywords()
# keywords = [word.value('name') for word in words]
keywords = get_keywords(lower_threshold)

selection = st.multiselect("Enter or Select some keywords", keywords)

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
        '<font color=\"red\">No recommendations for keywords and threshold combination</font>', unsafe_allow_html=True)
for record in results:
    print(f'visualize.py: title: {record.value("title")}')
    st.markdown(
        f"* [{record.value('title')}]({record.value('url')})")
