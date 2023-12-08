import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Put the URLs to fetch here. I recommend sorting them all by TEAM_NAME if you are compiling several.
#Make sure to include "SeasonYear={}" in the url for pulling data from multiple seasons
urls = [
    'https://www.nba.com/stats/teams/isolation?SeasonType=Regular%20Season&SeasonYear={}&TypeGrouping=offensive&dir=A&sort=TEAM_NAME',
]
# Empty DataFrame to store the final result
final_df = pd.DataFrame()

# Create a new Chrome WebDriver instance. Make sure you have this set up!!
driver = webdriver.Chrome()

# Iterate through each season (season start year, season end year)
for year in range(2023, 2024):
    season_year = f"{year}-{str(year + 1)[2:]}"
    
    #df to store the data for the current season
    season_df = pd.DataFrame()

    for url in urls:
        url = url.format(season_year)
        driver.get(url)

        # Wait for the table to load (timeout of 10 seconds). 
        wait = WebDriverWait(driver, 10)
        table_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Crom_table__p1iZz"))) #"Crom_table__p1iZz" is the name of the table as of 12/2023. Use inspect element on the web page to identify the table name if you get errors here.
        table_data = table_element.get_attribute('outerHTML')

        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(table_data, 'html.parser')
        table_body = soup.find('tbody')
        rows = table_body.find_all('tr')

        #Empty list to store the data
        data = []

        # Extract data from each row
        for row in rows:
            # Get table cells (including nested elements)
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            data.append(row_data)

        # Define column headers (using the first row of the table)
        header_row = rows[0]
        headers = [url + " - " + header.get_text(strip=True) for header in header_row.find_all(['td', 'th'])]

        df = pd.DataFrame(data, columns=headers)

        # Merge the DataFrame with the current season DataFrame based on column indices
        season_df = pd.concat([season_df, df], axis=1)

        # Add a delay of 2 seconds before the next request
        time.sleep(2) #This timeout prevents errors; adjust if necessary

    # Reset column indices to numbers for the current season DataFrame
    season_df.columns = range(len(season_df.columns))

    # Append the season year to the end of the string in column 1
    season_df.iloc[:, 0] = season_df.iloc[:, 0] + f" - {season_year}"

    # Append the current season_df to the final_df
    final_df = pd.concat([final_df, season_df])

# Reset the indices of the final_df
final_df.reset_index(drop=True, inplace=True)

driver.quit()

print(final_df)