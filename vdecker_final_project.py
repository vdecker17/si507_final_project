#########################################
##### SI507 Final Project           #####
##### Name: Vanessa Decker          #####
##### Uniqname: vdecker             #####
#########################################

import json
import requests
import flickrapi
from bs4 import BeautifulSoup
import requests
from pprint import pprint
import sqlite3

import final_project_secrets as secrets

flickr_key = secrets.FLICKR_API_KEY
flickr_secret = secrets.FLICKR_API_SECRET

database_filename = 'final_project.db'

CACHE_FILE_NAME = 'final_project.json'
CACHE_DICT = {}

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
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache


def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache,indent=4)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url):
    try:
        CACHE_DICT = load_cache()
        output = CACHE_DICT[url]
        return output
    except:
        if "flickr" in url:
            species = url.split('flickr_')[0]
            flickr = flickrapi.FlickrAPI(flickr_key,secret=flickr_secret,format='parsed-json')
            request = flickr.photos.search(tags=species, min_taken_date = '2019-01-01', max_taken_date = '2020-01-01', bbox = '-111.211703,44.042039,-109.832919,45.094701', has_geo=1, per_page=50, extras='url_z, geo')
        else:
            request = requests.get(url).text
        CACHE_DICT[url] = request
        save_cache(CACHE_DICT)
        return CACHE_DICT[url]

def make_species_url_dict():
    ''' Make a dictionary where the key is a predator species name and the value is the species url on the nps.gov Yellowstone-mammals (https://www.nps.gov/yell/learn/nature/mammals.htm) page

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is the species name and value is a url
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
    where_key = 'Where_to_See'
    where_val = 'Not available'
    stats = {
        'Species':species,
        where_key:where_val
            }
    return stats

def get_nps_species_stats4(species, species_url):
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
    for row in table_contents:
        # columns = ', '.join(row.keys())
        # vals = ', '.join([':'+i for i in row.keys()])
        # # values = ', '.join([f"'{i}'" for i in row.values()])
        # values = list(row.values())
        # print(f"""
        # INSERT INTO {table_name} ({columns})
        # VALUES ({values})
        # """)
        # conn.execute(f"""
        # INSERT INTO {table_name} ({columns})
        # VALUES ({vals})
        # """,values)
        columns = ', '.join(row.keys())
        placeholders = ', '.join('?' * len(row))
        sql = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
        values = [str(x) if isinstance(x, list) else x for x in row.values()]
        cur.execute(sql, values)
        conn.commit()
    return None

# def map_photos(coordinates):


if __name__ == "__main__":
    #Connect to sqlite db
    conn = sqlite3.connect(database_filename)
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

    # species_dict = make_species_url_dict()
    # selection = None
    # while True:
    #     if selection == 'exit':
    #         break
    #     species = [species_dict.keys()]
    #     print(species)
    #     choice = input('Please select a species from the list above to learn more about the species (example: Black Bear or Cougar): ')
    #     choice = choice.title()
    #     bear = get_flickr_photos('brown bear')
    #     species = make_species_url_dict()
    #     for species, url in species.items():
    #         print(pick_species_stats_function('species', url))
    species_dict = make_species_url_dict()
    wiki_list = []
    nps_list = []
    flickr_list = []
    for key,val in species_dict.items():
        nps_list.append(pick_species_stats_function(key,val))
        wiki_list.append(get_wiki_stats(key))
        flickr_list.extend(get_flickr_photos(key))
    
    # Populate all the SQL tables
    # print(wiki_list)
    populate_table("flickr",flickr_list)
    populate_table("nps",nps_list)
    populate_table("wiki",wiki_list)
    conn.close()



