import requests
standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
data = requests.get(standings_url)
from bs4 import BeautifulSoup
soup = BeautifulSoup(data.text, features="html.parser")

standings_table = soup.select('table.stats_table')[0]

links = standings_table.find_all('a') #find a tag with links to teams 

links = [l.get("href") for l in links]
links = [l for l in links if '/squads/' in l] #filters for href links the squad links - links now hold all indiviual links for squads 

teams_urls = [f"https://fbref.com{l}" for l in links] #adds first part to links 

teams_url = teams_urls[0]
data = requests.get(teams_url)

import pandas as pd
matches = pd.read_html(data.text, match ="Scores & Fixtures") ##looks into tables for string , pd.read.html reads all ables on the page 

soup = BeautifulSoup(data.text)

links = soup.find_all('a')
links = [l.get("href") for l in links] #list comp to get url of link

links = [l for l in links if l and 'all_comps/shooting/' in l]

data = requests.get(f"https://fbref.com{links[0]}") #shooting stats page

shooting = pd.read_html(data.text, match="Shooting")[0] #shooting data

shooting.columns = shooting.columns.droplevel()

team_data = matches[0].merge(shooting[["date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
##-------------------------------------------------------------------------------------- data scraping portion
## now we use a loop to scrap data from multiple years 

years = (list(range(2022,2020), -1))

all_matches = []
standings_url = "https://fbref.com/en/comps/9/Premier-League-Stats"
import time

for year in years:
    data = requests.get(standings_url)
    soup = BeautifulSoup(data.text, features="html.parser")
    standings_table = soup.select('table.stats_table')[0]
    links = [l.get("href") for l in standings_table.find_all('a')]
    links = [l for l in links if '/squads/' in l]
    team_urls = [f"https://fbref.com{l}" for l in links]

    previous_season = soup.select("a.prev")[0].get("href")
    standings_url = f"https://fbref.com{previous_season}"

    for team_url in team_urls:
        team_name = team_url.split("/")[-1].replace("-Stats", "").replace("-", " ")
        data = requests.get(team_url)
        matches = pd.read_html(data.text, match="Scores & Fixtures")[0]
        soup = BeautifulSoup(data.text)
        links = [l.get("href") for l in soup.find_all('a')]
        links = [l for l in links if l and 'all_comps/shooting/' in l]
        data = requests.get(f"https://fbref.com{links[0]}")
        shooting = pd.read_html(data.text, match="Shooting")[0]
        shooting.columns = shooting.columns.droplevel()

        try:
            team_data = matches.merge(shooting[["Date", "Sh", "SoT", "Dist", "FK", "PK", "PKatt"]], on="Date")
        except ValueError:
            continue
        team_data = team_data[team_data["Comp"] == "Premier League"]
        
        team_data["Season"] = year
        team_data["Team"] = team_name
        all_matches.append(team_data)
        time.sleep(1)

        




        match_df = pd.concat(all_matches)
        match_df.columns = [c.lower() for c in match_df.columns]
        match_df
        match_df.to_csv("matches.csv")









 
