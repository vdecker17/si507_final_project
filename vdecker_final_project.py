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

import final_project_secrets as secrets

flickr_key = secrets.FLICKR_API_KEY
flickr_secret = secrets.FLICKR_API_SECRET

CACHE_FILE_NAME = 'final_project.json'
CACHE_DICT = {}

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
    contents_to_write = json.dumps(cache)
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
            request = flickr.photos.search(tags=species, min_taken_date = '2019-01-01', max_taken_date = '2020-01-01', bbox = '-111.211703,44.042039,-109.832919,45.094701', has_geo=1, per_page=5, extras='url_z, geo')
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
    html1 = requests.get('https://www.nps.gov').text
    soup1 = BeautifulSoup(html1, 'html.parser')
    search_species = soup1.find('div', id='cs_control_5587046')
    species_urls = {}
    species_names = []
    for name in search_species.find_all('h3', class_='Feature-title carrot-end'):
        species_names.append(name)
    for name, url in zip(species_names,search_species.find_all('a', href=True)):
        nps = ('https://www.nps.gov'+url['href'])
        species_urls[name] = nps
    return species_urls

def get_wiki_stats(species):
    if len(species.split()) > 2:
        species_format = species.split()
        species = f'{species_format[0]}_{species_format[1].lower()}'
    url = f'https://en.wikipedia.org/wiki/{species}'
    html = make_url_request_using_cache(url)
    soup = BeautifulSoup(html, 'html.parser')
    search_wiki = soup.find('div', style='text-align:center')
    status = search_wiki.find('a', href=True, class_='mw-redirect').text
    return status

def get_nps_species_stats1(species_url):
    html = make_url_request_using_cache(species_url)
    soup = BeautifulSoup(html, 'html.parser')
    search_species = soup.find('aside', class_='fact-check')
    display_keys = search_species.find_all('h4')
    for display_key in display_keys:
        if display_key.text == 'Numbers in Yellowstone':
            numbers_key = display_key.text
            numbers_val = display_key.find('p').text
        if display_key.text == 'Where to See':
            where_key = display_key.text
            where_val = display_key.find('p').text
        if display_key.text == 'Size and Behavior':
            size_key = display_key.text
            size_val = display_key.find('p').text
    return f'{numbers_key}: {numbers_val}\n{where_key}: {where_val}\n{size_key}: {size_val}'

def get_nps_species_stats2(species_url, ):
    html = make_url_request_using_cache(species_url)
    soup = BeautifulSoup(html, 'html.parser')
    search_species = soup.find('div', class_='Component text-content-size text-content-style ArticeTextGroup clearfix')
    display_keys = search_species.find('h3')
    for display_key in display_keys:
        if display_key.text == 'Numbers in Yellowstone':
            numbers_key = display_key.text
            numbers_val = display_key.find('p').text
        if display_key.text == 'Where to See':
            where_key = display_key.text
            where_val = display_key.find('p').text
        if display_key.text == 'Size and Behavior':
            size_key = display_key.text
            size_val = display_key.find('p').text
    return f'{numbers_key}: {numbers_val}\n{where_key}: {where_val}\n{size_key}: {size_val}'

def get_flickr_photos(species):
    # flickr = flickrapi.FlickrAPI(flickr_key,secret=flickr_secret,format='parsed-json')
    # species_photos = flickr.photos.search(tags=species, min_taken_date = '2019-01-01', max_taken_date = '2020-01-01', bbox = '-111.211703,44.042039,-109.832919,45.094701', has_geo=1, per_page=5, extras='url_z, geo')
    unique_key = f"flickr_{species}"
    species_photos = make_url_request_using_cache(unique_key)
    photos_s = species_photos['photos']
    # print(f"View Photo: {photos_s['photo'][0]['url_z']}")
    # coord_list = []
    # for photo in photos_s:
    #     coord_lat = photo['photo'][0]['latitude]
    #     coord_long = photo['photo'][0]['longitude']
    #     coord_list.append(coordinate)
    # return coord_list
    return photos_s

# def map_photos(coordinates):


if __name__ == "__main__":
    # species_dict = make_species_url_dict()
    # selection = None
    # while True:
    #     if selection == 'exit':
    #         break
    #     count = 1
    #     species = [species_dict.keys()]
    #     for s in species:
    #         print(f'[{count}] {s}')
    #         count += 1
    #     species = input('Please select a number from the list above to learn more about the species: ')
   bear = get_flickr_photos('brown bear')
   pprint(bear)