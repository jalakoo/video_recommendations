import streamlit as st
from neo4j_utils import Neo4jConnection
from dotenv import load_dotenv
import pandas as pd
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
def get_keywords():
    keywords_query = f"""
    MATCH (w:Word)-[r:CONTAINS]-(v:Video)
    RETURN w.name AS name
    """
    try:
        words = neo4j_utils.query(keywords_query)
        result = [word.value('name') for word in words]
        return result.sort()
    except Exception as e:
        print(f'visualize.py: get_keywords: ERROR: {e}')
        return None


@st.cache(suppress_st_warning=True, persist=True)
def load_data(url):
    data = pd.read_csv(url, sep=",", keep_default_na=False)
    return data


def fallback_keywords():
    fallback_uri = os.environ["FALLBACK_KEYWORDS_URI"]
    keywords = load_data(fallback_uri)
    return keywords['word'].values.tolist()

# SIDEBAR
#############################################################################
# TODO: Add in some search parameters
# st.sidebar.markdown(
#     "<font color=\"grey\">*Filter Options*</font>", unsafe_allow_html=True)
# lower_threshold = st.sidebar.slider(
#     "Minimum occurance of keyword in a video", 1, 10, 5, 1)


# MAIN
#############################################################################
st.title("AuraDB Video Recommendations")
st.markdown(
    "<font color=\"grey\">*Want to learn more about Neo4j's Free AuraDB? Choose a selection of keywords from transcripts to get a list of the best videos you should watch!*</font>", unsafe_allow_html=True)
st.markdown('<br>', unsafe_allow_html=True)

keywords = get_keywords()
if keywords == None:
    keywords = fallback_keywords()
selection = st.multiselect(
    "Type in or Select keywords you're interested in", keywords)

# TODO: Update query to extract from commonVideos instead
query = f"""
WITH {selection} as keywords
MATCH (v:Video)-[r:CONTAINS]->(w:Word)
WHERE w.name in keywords
WITH w, collect(v) as videosPerWord
WITH collect(videosPerWord) as videos
WITH reduce(commonVideos = head(videos), video in tail(videos) | apoc.coll.intersection(commonVideos, video)) as commonVideos
UNWIND commonVideos as videos
RETURN videos.title as title, videos.url as url
"""


results = neo4j_utils.query(query)
st.markdown('<br>', unsafe_allow_html=True)
st.markdown('Video Recommendations:')

if len(results) == 0:
    st.markdown(
        '* <font color=\"red\">Nothing Yet!</font><font color=\"grey\"> Try a different threshold and keywords combination</font>', unsafe_allow_html=True)
for record in results:
    st.markdown(
        f"* [{record.value('title')}]({record.value('url')})")
neo4j_utils.close()
