import streamlit as st
import pandas as pd
import numpy as np
from itertools import product

st.set_page_config(page_title="NBA playoff lineups", page_icon=":material/sports_basketball:", layout="wide")

conf_series = pd.read_csv("data/conferences.csv", index_col=0).squeeze()
abbr_series = pd.read_csv("data/NBA-NameReplacements.csv", index_col=0).squeeze()

def combine_names(df, col_first, col_last, col_new="Name"):
    '''Create a new "Name" column that holds both the first and last names'''
    df = df.copy()
    df[col_new] = df.apply(lambda row: f"{row[col_first]} {row[col_last]}", axis=1)
    return df

st.title("NBA playoff lineups")


st.write("Have Underdog email you your exposure csv file (refresh the exposure page right beforehand) and upload the csv file below.  (As far as I can tell, this is only possible from the Exposure section on Desktop, not Mobile.)")

df_ranks = pd.read_csv("data/playoff_rankings.csv")
df_ranks["teamName"] = df_ranks["teamName"].astype(str)

df_ranks = combine_names(df_ranks, "firstName", "lastName")
df_ranks["adp"] = pd.to_numeric(df_ranks["adp"], errors='coerce')
df_ranks = df_ranks.query("adp < 60")
adp_dct = dict(zip(df_ranks["Name"], df_ranks["adp"]))

# from Chicago Bulls to CHI
df_ranks["Team"] = df_ranks["teamName"].map(lambda s: abbr_series.get(s.split()[-1].upper(), ""))

file = st.file_uploader("Exposure csv", type="csv", accept_multiple_files=False)


names = st.multiselect(
    "Get drafts including all of these players",
    df_ranks.sort_values("adp")["Name"],
)


try:
    df = pd.read_csv(file)
    df["Picked At"] = pd.to_datetime(df["Picked At"])
    df = df.sort_values("Picked At", ascending=True)
    df = combine_names(df, "First Name", "Last Name")
    # We only take the drafts that include all of these players
    for name in names:
        draft_keys = df.query("Name == @name")["Draft"].values
        df = df[df["Draft"].isin(draft_keys)]
    
    for key, df_draft in df.groupby("Draft", sort=False):
        st.write(', '.join(df_draft[["Name", "Team"]].apply(lambda row: f"{row['Name']} ({row['Team']})", axis=1).values))
except ValueError:
    pass
