#########################################
##### SI507 Final Project: Mapping Flickr Photos #####
##### Name: Vanessa Decker          #####
##### Uniqname: vdecker             #####
#########################################

import json
import requests
import flickrapi
from bs4 import BeautifulSoup
import requests
import sqlite3
import pandas as pd
import plotly.graph_objects as go

import final_project_secrets as secrets

flickr_key = secrets.FLICKR_API_KEY
flickr_secret = secrets.FLICKR_API_SECRET
mapbox_token = secrets.MAPBOX_TOKEN

database_filename = 'final_project.db'

CACHE_FILE_NAME = 'final_project.json'
CACHE_DICT = {}

#this is a dictionary that maps how the name is formatted in NPS to how it is appended to the wikipedia URL
wiki_species_input_dict = {
    'Badger': 'American_badger',
    'Black Bear': 'American_black_bear',
    'Bobcat': 'Bobcat',
    'Canada Lynx': 'Canada_lynx',
    'Cougar': 'Cougar',
    'Coyote': 'Coyote',
    'Gray Wolf': 'Wolf',
    'Grizzly Bear': 'Brown_bear',
    'Long-tailed Weasel': 'Long-tailed_weasel',
    'Marten': 'American_marten',
    'Red Fox': 'Red_fox',
    'River Otter': 'North_American_river_otter',
    'Short-tailed Weasel': 'Stoat',
    'Wolverine': 'Wolverine'
}

def load_cache():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache,indent=4)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url):
    ''' Returns desired data from the cache if exists or makes a new request and stores it in the cache"

    Parameters
    ----------
    URL (the key for the desired data in the cache or the URL used to make a new request)

    Returns
    -------
    The desired data from the cache
    '''
    try:
        CACHE_DICT = load_cache()
        output = CACHE_DICT[url]
        return output
    except:
        if "flickr" in url:
            species = url.split('flickr_')[-1].title()
            flickr = flickrapi.FlickrAPI(flickr_key,secret=flickr_secret,format='parsed-json')
            request = flickr.photos.search(text=species, min_taken_date = '2015-01-01', max_taken_date = '2021-01-01', bbox = '-111.211703,44.042039,-109.832919,45.094701', has_geo=1, per_page=50, extras='url_z, geo')
        else:
            request = requests.get(url).text
        CACHE_DICT[url] = request
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]

def make_species_url_dict():
    ''' Makes a dictionary where the key is a predator species name and the value is the species url on the nps.gov Yellowstone-mammals (https://www.nps.gov/yell/learn/nature/mammals.htm) page

    Parameters
    ----------
    None

    Returns
    -------
    A dictionary where the key is the species name and value is the url for the species' NPS page
    '''
    # html1 = requests.get('https://www.nps.gov').text
    html1 = make_url_request_using_cache('https://www.nps.gov/yell/learn/nature/mammals.htm')
    soup1 = BeautifulSoup(html1, 'html.parser')
    search_species = soup1.find('div', id='cs_control_5587046')
    species_urls = {}
    species_names = []
    for name in search_species.find_all('h3', class_='Feature-title carrot-end'):
        species_names.append(name.text)
    for name, url in zip(species_names,search_species.find_all('a', href=True)):
        nps = ('https://www.nps.gov'+url['href'])
        species_urls[name] = nps
    return species_urls

def get_wiki_stats(species):
    ''' Makes a dictionary that maps the species name to the input species and the conservation status to its conservation status scraped from the species' wikipedia page

    Parameters
    ----------
    Species (a species from the list of keys from the make_species_url_dict function)

    Returns
    -------
    A dictionary with two key,value pairs:
    The first key,value pair: the key is the string 'species' and the value is species parameter value
    The second key,value pair: the key is the string 'conservation_status' and the value is the conservation status scraped from the wikipedia page
    '''
    wiki_input = wiki_species_input_dict[species]
    url = f'https://en.wikipedia.org/wiki/{wiki_input}'
    html = make_url_request_using_cache(url)
    soup = BeautifulSoup(html, 'html.parser')
    search_wiki = soup.find('table', class_='infobox biota')
    links = search_wiki.find_all('a', href=True)
    for link in links:
        if 'Conservation status' in link.text:
            status = link.findNext('a').text
    return {'species': species, 'conservation_status': status}

def get_nps_species_stats1(species, species_url):
    ''' Makes a dictionary that maps the species name to the input species and the 'where to see' data from the NPS website to the key 'where to see'
    7 different functions had to be made to scrape this data because many different species' pages had this data under different tags
    For species that use this function, the information was found under the h4 tag (with needed info appearing with a 'p' tag after "Where to See" on the page)

    Parameters
    ----------
    Species (a species from the list of keys from the make_species_url_dict function)
    Species_url (a url from the list of values from the make_species_url_dict function)

    Returns
    -------
    A dictionary with two key,value pairs:
    The first key,value pair: the key is the string 'species' and the value is species parameter value
    The second key,value pair: the key is the string 'Where_to_See' and the value is the information on where to see the species scraped from the NPS website
    '''
    html = make_url_request_using_cache(species_url)
    soup = BeautifulSoup(html, 'html.parser')
    search_species = soup.find('aside', class_='fact-check')
    display_keys = search_species.find_all('h4')
    for display_key in display_keys:
        if 'Where to See' in display_key.text:
            where_val = display_key.findNext('p').text
    stats = {
        'Species':species,
        'Where_to_See':where_val
            }
    return stats

def get_nps_species_stats2(species, species_url):
    ''' Makes a dictionary that maps the species name to the input species and the 'where to see' data from the NPS website to the key 'where to see'
    7 different functions had to be made to scrape this data because many different species' pages had this data under different tags
    For species that use this function, the information was found under the h4 tag (with needed info appearing as a list after "Where to See" on the page)

    Parameters
    ----------
    Species (a species from the list of keys from the make_species_url_dict function)
    Species_url (a url from the list of values from the make_species_url_dict function)

    Returns
    -------
    A dictionary with two key,value pairs:
    The first key,value pair: the key is the string 'species' and the value is species parameter value
    The second key,value pair: the key is the string 'Where_to_See' and the value is the information on where to see the species scraped from the NPS website
    '''
    html = make_url_request_using_cache(species_url)
    soup = BeautifulSoup(html, 'html.parser')
    search_species = soup.find('aside', class_='fact-check')
    display_keys = search_species.find_all('h4')
    where_val = []
    for display_key in display_keys:
        if 'Where to See' in display_key.text:
            where_ul = display_key.findNext('ul')
            where_li = where_ul.find_all('li')
            for w in where_li:
                where_val.append(w.text)
    stats = {
        'Species':species,
        'Where_to_See':where_val
            }
    return stats

def get_nps_species_stats3(species, species_url):
    ''' Makes a dictionary that maps the species name to the input species and the 'where to see' data from the NPS website to the key 'where to see'
    7 different functions had to be made to scrape this data because many different species' pages had this data under different tags
    This function was used only for wolverines, which did not have "where to see" or "habitat" data available

    Parameters
    ----------
    Species (a species from the list of keys from the make_species_url_dict function)
    Species_url (a url from the list of values from the make_species_url_dict function)

    Returns
    -------
    A dictionary with two key,value pairs:
    The first key,value pair: the key is the string 'species' and the value is species parameter value
    The second key,value pair: the key is the string 'Where_to_See' and the value is the information on where to see the species scraped from the NPS website
    '''
    where_key = 'Where_to_See'
    where_val = 'Not available'
    stats = {
        'Species':species,
        where_key:where_val
            }
    return stats

def get_nps_species_stats4(species, species_url):
    ''' Makes a dictionary that maps the species name to the input species and the 'where to see' data from the NPS website to the key 'where to see'
    7 different functions had to be made to scrape this data because many different species' pages had this data under different tags
    For species that use this function, the information was found under the h4 tag (with needed info appearing with no tags after "Where to See" on the page)

    Parameters
    ----------
    Species (a species from the list of keys from the make_species_url_dict function)
    Species_url (a url from the list of values from the make_species_url_dict function)

    Returns
    -------
    A dictionary with two key,value pairs:
    The first key,value pair: the key is the string 'species' and the value is species parameter value
    The second key,value pair: the key is the string 'Where_to_See' and the value is the information on where to see the species scraped from the NPS website
    '''
    html = make_url_request_using_cache(species_url)
    soup = BeautifulSoup(html, 'html.parser')
    search_species = soup.find('aside', class_='fact-check')
    display_keys = search_species.find_all('h4')
    for display_key in display_keys:
        if 'Where to See' in display_key.text:
            where_val = display_key.next_sibling.strip()
    stats = {
        'Species':species,
        'Where_to_See':where_val
            }
    return stats

def get_nps_species_stats5(species, species_url):
    ''' Makes a dictionary that maps the species name to the input species and the 'where to see' data from the NPS website to the key 'where to see'
    7 different functions had to be made to scrape this data because many different species' pages had this data under different tags
    For species that use this function, the information was found under the h3 tag (with needed info appearing with a 'p' tag after "Where to See" on the page)

    Parameters
    ----------
    Species (a species from the list of keys from the make_species_url_dict function)
    Species_url (a url from the list of values from the make_species_url_dict function)

    Returns
    -------
    A dictionary with two key,value pairs:
    The first key,value pair: the key is the string 'species' and the value is species parameter value
    The second key,value pair: the key is the string 'Where_to_See' and the value is the information on where to see the species scraped from the NPS website
    '''
    html = make_url_request_using_cache(species_url)
    soup = BeautifulSoup(html, 'html.parser')
    search_species = soup.find_all('div', class_='Component text-content-size text-content-style ArticleTextGroup clearfix')[1]
    display_keys = search_species.find_all('h3')
    for display_key in display_keys:
        if 'Where to See' in display_key.text:
            where_val = display_key.findNext('p').text
    stats = {
                'Species':species,
                'Where_to_See':where_val
            }
    return stats

def get_nps_species_stats6(species, species_url):
    ''' Makes a dictionary that maps the species name to the input species and the 'where to see' data from the NPS website to the key 'where to see'
    7 different functions had to be made to scrape this data because many different species' pages had this data under different tags
    For species that use this function, the information was found under the h3 tag (with needed info appearing as a list after "Where to See" on the page)

    Parameters
    ----------
    Species (a species from the list of keys from the make_species_url_dict function)
    Species_url (a url from the list of values from the make_species_url_dict function)

    Returns
    -------
    A dictionary with two key,value pairs:
    The first key,value pair: the key is the string 'species' and the value is species parameter value
    The second key,value pair: the key is the string 'Where_to_See' and the value is the information on where to see the species scraped from the NPS website
    '''
    html = make_url_request_using_cache(species_url)
    soup = BeautifulSoup(html, 'html.parser')
    search_species = soup.find_all('div', class_='Component text-content-size text-content-style ArticleTextGroup clearfix')[1]
    display_keys = search_species.find_all('h3')
    where_val = []
    for display_key in display_keys:
        if 'Where to See' in display_key.text:
            where_ul = display_key.findNext('ul')
            where_li = where_ul.find_all('li')
            for w in where_li:
                where_val.append(w.text)
    stats = {
                'Species':species,
                'Where_to_See':where_val
            }
    return stats


def get_nps_species_stats7(species, species_url):
    ''' Makes a dictionary that maps the species name to the input species and the 'where to see' data from the NPS website to the key 'where to see'
    7 different functions had to be made to scrape this data because many different species' pages had this data under different tags
    For species that use this function, the information was found under the h2 tag (with needed info appearing as a list after "Where to See" on the page)

    Parameters
    ----------
    Species (a species from the list of keys from the make_species_url_dict function)
    Species_url (a url from the list of values from the make_species_url_dict function)

    Returns
    -------
    A dictionary with two key,value pairs:
    The first key,value pair: the key is the string 'species' and the value is species parameter value
    The second key,value pair: the key is the string 'Where_to_See' and the value is the information on where to see the species scraped from the NPS website
    '''
    html = make_url_request_using_cache(species_url)
    soup = BeautifulSoup(html, 'html.parser')
    search_species = soup.find('div', class_='Component text-content-size text-content-style ArticleTextGroup clearfix')
    display_keys = search_species.find_all('h2')
    where_val = []
    for display_key in display_keys:
        if 'Habitat' in display_key.text:
            where_ul = display_key.findNext('ul')
            where_li = where_ul.find_all('li')
            for w in where_li:
                where_val.append(w.text)
        if 'Where to See' in display_key.text:
            where_ul = display_key.findNext('ul')
            where_li = where_ul.find_all('li')
            for w in where_li:
                where_val.append(w.text)
    stats = {
                'Species':species,
                'Where_to_See':where_val
            }
    return stats

def pick_species_stats_function(species, url):
    ''' Picks one of the 7 'get_nps_species_stats' functions from above based on how each species' information
    can be accessed (chooses correct function for scraping considering differing tags)

    Parameters
    ----------
    Species (a species from the list of keys from the make_species_url_dict function)
    Species_url (a url from the list of values from the make_species_url_dict function)

    Returns
    -------
    The return value of whichever 'get_nps_species_stats' function is chosen for the given input species
    '''
    if species == 'Black Bear' or species == 'Grizzly Bear':
        stats = get_nps_species_stats1(species, url)
    if species == 'Canada Lynx' or species == 'Gray Wolf':
        stats = get_nps_species_stats2(species, url)
    if species == 'Wolverine':
        stats = get_nps_species_stats3(species, url)
    if species == 'Cougar':
        stats = get_nps_species_stats4(species, url)
    if species == 'Coyote':
        stats = get_nps_species_stats5(species, url)
    if species == 'Red Fox':
        stats = get_nps_species_stats6(species, url)
    if species == 'Badger' or species == 'River Otter' or species == 'Short-tailed Weasel' or species == 'Long-tailed Weasel' or species == 'Marten' or species == 'Bobcat':
        stats = get_nps_species_stats7(species, url)
    return stats

def get_flickr_photos(species):
    ''' Uses the 'make_request_using_cache' function from above to return a dictionary of information from photos of a given species. 

    Parameters
    ----------
     Species (a species from the list of keys from the make_species_url_dict function that is used in the 'text' parameter of the Flickr API call to return
     all photos that mention the species in the title, tags or description)

    Returns
    -------
    A list of dictionaries containing the species name, latitude and longitude (used to create the map output) and 
    url (so that the user can view the image) of each image (50 image limit)
    '''
    unique_key = f"flickr_{species}"
    species_photos = make_url_request_using_cache(unique_key)
    photos_s = species_photos['photos']['photo']

    coord_list = []
    for photo in photos_s:
        coord_lat = photo['latitude']
        coord_long = photo['longitude']
        url = photo['url_z']
        coordinate = {
            'species': species,
            'latitude':coord_lat,
            'longitude': coord_long,
            'url': url
        }
        coord_list.append(coordinate)
    return coord_list

def populate_table(table_name, table_contents):
    ''' Puts all of the data retrieved from the API calls and scraping for each species into the tables created below. There is one table for each data
    source (Flickr API, Wikipedia, and NPS)

    Parameters
    ----------
    Table name (the name of the table created below for each data source)
    Table contents (the list of data to be put into the table)

    Returns
    -------
    None
    '''
    for row in table_contents:
        values = []
        columns = ', '.join(row.keys())
        placeholders = ', '.join('?' * len(row))
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        for val in row.values():
            if type(val) == list:
                val = str(val)
            else:
                val = val
            values.append(val)
        cur.execute(sql, values)
        conn.commit()
    return None



if __name__ == "__main__":
    #Connect to sqlite db
    conn = sqlite3.connect(database_filename)
    species_dict = make_species_url_dict()
    species = None
    try:
        pd.read_sql_query("""SELECT * FROM flickr""", conn)
        pd.read_sql_query("""SELECT * FROM wiki""", conn)
        pd.read_sql_query("""SELECT * FROM nps""", conn)
    except:
        cur = conn.cursor()
        #Create flickr table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS flickr(
        'species' string Not NULL,
        'latitude' float Not NULL,
        'longitude' float NOT NULL,
        'url' string NOT NULL)
        """)
        #Create wiki table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS wiki(
        'species' string PRIMARY KEY,
        'conservation_status' string Not NULL)
        """)
        #Create nps table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS nps(
        'species' string PRIMARY KEY,
        'Where_to_See' string NOT NULL)
        """)
        species_dict = make_species_url_dict()
        wiki_list = []
        nps_list = []
        flickr_list = []
        for key,val in species_dict.items():
            nps_list.append(pick_species_stats_function(key,val))
            wiki_list.append(get_wiki_stats(key))
            flickr_list.extend(get_flickr_photos(key))
        # Populate all the SQL tables
        populate_table("flickr",flickr_list)
        populate_table("nps",nps_list)
        populate_table("wiki",wiki_list)
    while True:
        species_choices = list(species_dict.keys())
        for s in species_choices:
            print(s)
        species = input('Please select a species from the list above to learn more about the species (example: Black Bear or Cougar) or "exit" to quit: ')
        if species == 'exit':
            conn.close()
            break
        df = pd.read_sql_query("""SELECT t.*, wiki.Conservation_Status
                          from (SELECT flickr.*,nps.Where_to_See
                          FROM flickr
                          JOIN nps on nps.species=flickr.species) as t
                          JOIN wiki on wiki.species=t.species""", conn)
        df = df[df.species == species].reset_index()
        print('-------------------------------------')
        print(f'Conservation Status of {species}s: ')
        print(df.conservation_status[0])
        print('-------------------------------------')
        print(f'Where to see {species}s: ')
        print(df.Where_to_See[0])
        print('-------------------------------------')
        print(f'Browse {species} photos below: ')
        count = 0
        for photo in get_flickr_photos(species):
            count += 1
            print(f'Photo {count}:')
            print(f'Latitude: {photo["latitude"]}, Longitude: {photo["longitude"]}, URL: {photo["url"]}')
            sp_lat = df.latitude
            sp_lon = df.longitude
            species_name = df.species
            status = df.conservation_status
            # plotly code based on example number 5 from: https://plotly.com/python/scattermapbox/
            fig = go.Figure() #instantiates map figure object
            fig.add_trace(go.Scattermapbox( #adds points to map from the coordinates in the data frame and specifies marker properties and hover text
                    lat=sp_lat,
                    lon=sp_lon,
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        size=15,
                        color='rgb(0, 125, 125)',
                        opacity=0.7
                    ),
                    text = species_name,
                    hoverinfo='all'
                ))
        fig.update_layout( #creates layout properties like title, map location and style
        title='Predator Sightings in Yellowstone National Park',
        autosize=True,
        hovermode='closest',
        showlegend=False,
        mapbox=dict(
            accesstoken=mapbox_token,
            bearing=0,
            center=dict(
                lat=44,
                lon=-110
            ),
            pitch=0,
            zoom=3,
            style='light'
        ),
    )
        fig.show() #opens the figure in the browser





