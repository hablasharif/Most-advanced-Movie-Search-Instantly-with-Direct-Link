
import streamlit as st
import pandas as pd
import requests
import random
from bs4 import BeautifulSoup
from lxml import html
import re
from urllib.parse import urlparse

# Load movie data from a CSV file
@st.cache_data
def load_movie_data():
    data = pd.read_csv(r"C:\Users\style\sample test 2 - Copy.csv")  # Replace with the path to your CSV file
    return data

movie_data = load_movie_data()

# User agents to mimic different browsers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/94.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/94.0.992.50",
]

# Function to extract a link from a URL
def extract_link(url):
    try:
        # Check if the URL contains the specified text
        if "https://expeditesimplicity.com/safe.php?link=" in url:
            # Extract the part after the specified text
            link = url.split("https://expeditesimplicity.com/safe.php?link=")[1]
            return link
        else:
            # Create a custom session with a random user agent
            session = requests.Session()
            session.verify = False
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            session.headers.update(headers)

            # Send an HTTP GET request to the URL with retries
            for _ in range(3):
                response = session.get(url)
                if response.status_code == 200:
                    # Parse the HTML content of the page
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Find the element with the data-drive attribute
                    episode_item = soup.find('li', {'data-drive': True})

                    # Extract the URL from the data-drive attribute
                    if episode_item:
                        link = episode_item['data-drive']
                        return link

            return None
    except Exception as e:
        return None

# Function to extract all iframe sources from a URL
def extract_all_iframe_srcs(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        if urlparse(url).netloc == "www.hindimovies.to" and re.match(r'^/movie/', urlparse(url).path):
            st.write("IFrame Sources are not applicable for this URL.")
            return [find_custom_url(url)]

        iframes = soup.find_all('iframe')
        if not iframes:
            return ["No iframes found on this page."]
        
        iframe_srcs = [iframe.get('src') for iframe in iframes if iframe.get('src')]
        return iframe_srcs
    except Exception as e:
        return [f"Error: {e}"]

# Function to find the custom URL for "www.hindimovies.to" domain and specific URL pattern
def find_custom_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Add code to find the custom URL for "www.hindimovies.to" domain and specific URL pattern
        # Here's a placeholder code to extract the URL from a div with id "iframe-screen":
        div = soup.find('div', id="iframe-screen")
        if div:
            a = div.find('a', href=True)
            if a:
                return a['href']
            else:
                return "No custom URL found on this page."
        else:
            return "No custom URL found on this page."
    except Exception as e:
        return f"Error: {e}"

# Function to extract links 01, 03, and 04 from the provided URL pattern
def extract_links_010304(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        link_pattern = re.compile(r'Link\s+(\d{2})')
        link_elements = soup.find_all(text=link_pattern)

        links = {}
        for link_element in link_elements:
            match = link_pattern.search(link_element)
            if match:
                link_number = match.group(1)
                link_container = link_element.find_next('div', class_='OptionBx on')
                if link_container:
                    link_url = link_container.find('a', href=True)
                    if link_url:
                        links[f"Link {link_number}"] = link_url['href']
        
        return links
    except Exception as e:
        return {}

# Function to fetch and display the source code of a URL using dynamically extracted XPath
def show_source_code(link):
    try:
        # Create a custom session with a random user agent
        session = requests.Session()
        session.verify = False
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        session.headers.update(headers)

        # Send an HTTP GET request to the link with retries
        for _ in range(3):
            response = session.get(link)
            if response.status_code == 200:
                # Parse the HTML content of the page using lxml
                tree = html.fromstring(response.content)

                # Use XPath expression to find all href URLs
                href_urls = tree.xpath('//a/@href')
                if href_urls:
                    st.subheader("Href URLs Extracted Using Dynamically Detected XPath:")
                    for url in href_urls:
                        # Split the URL by "=" and print the part after "="
                        parts = url.split("=")
                        if len(parts) > 1:
                            st.write(parts[1])
                    return

        st.error("Failed to fetch href URLs using dynamically detected XPath after multiple attempts.")
    except Exception as e:
        st.error("An error occurred while fetching the content.")

# Streamlit app
def main():
    st.title("Movie Search and URL Extractor")

    # Sidebar for user input
    st.sidebar.header("Search Criteria")
    movie_name = st.sidebar.text_input("Enter Movie Name:")
    movie_year = st.sidebar.text_input("Enter Movie Year:")

    # Check if movie_year is not empty and is a valid integer
    if movie_year and (movie_year.isdigit() or (movie_year.startswith('-') and movie_year[1:].isdigit())):
        # Convert the input year to an integer
        movie_year = int(movie_year)
    else:
        movie_year = None  # Set it to None if it's not a valid integer

    # Additional options
    search_by_name_only = st.sidebar.checkbox("Search by Name Only")
    search_by_year_only = st.sidebar.checkbox("Search by Year Only")

    # Filter the DataFrame based on user input
    if search_by_name_only and movie_name:
        # Use pd.notna() to handle NaN values
        filtered_movies = movie_data[pd.notna(movie_data["Title"]) & movie_data["Title"].str.contains(movie_name, case=False)]
    elif search_by_year_only and movie_year is not None:  # Check if movie_year is not None
        filtered_movies = movie_data[movie_data["Year"] == movie_year]
    else:
        filtered_movies = movie_data[(pd.notna(movie_data["Title"]) & movie_data["Title"].str.contains(movie_name, case=False)) &
                                     (movie_data["Year"] == movie_year)]

    # Display the filtered movies and their URLs
    if not filtered_movies.empty:
        st.subheader("Matching Movies:")
        for index, row in filtered_movies.iterrows():
            st.write(f"**Title:** {row['Title']}")
            st.write(f"**Year:** {row['Year']}")
            st.write(f"**URL:** {row['URL']}")
            st.write("Extracted Links and Iframe Sources:")
            movie_url = row['URL']
            extracted_link = extract_link(movie_url)
            if extracted_link:
                st.write(f"Link: {extracted_link}")
            else:
                st.write("Link not found on the page.")
            
            iframe_srcs = extract_all_iframe_srcs(movie_url)
            if iframe_srcs:
                for i, src in enumerate(iframe_srcs):
                    st.write(f"IFrame Source {i + 1}: {src}")
            else:
                st.write("No IFrame Sources found.")
            
            links = extract_links_010304(movie_url)
            if links:
                for link, href in links.items():
                    st.write(f"{link}: {href}")
            else:
                st.write("No Links 01, 03, 04 found.")
    elif movie_name or movie_year:
        st.subheader("No matching movies found.")
    else:
        st.subheader("Please enter a movie name or year.")

if __name__ == "__main__":
    main()
