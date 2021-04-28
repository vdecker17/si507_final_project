# si507_final_project
Map of predacious mammal sightings in Yellowstone National Park

This project scrapes information on different predators in Yellowstone from the National Park Service website and Wikipedia and displays this information in the terminal and also displays Flickr photo location information on a map. The map shows the location of Flickr photos (from 2015 and on) that contain the species’ name in the description, title, or tags, and when you hover over each photo data point, a popup appears that shows the species name and photo coordinates. Print statements in the terminal show the conservation status of the species, information on where you are likely to see them, and the URLs of the photos so that you can view them.
To interact with the program, you run the program and then enter a species name from the list that is printed in the terminal. When you pick a species, a page will open in your browser that shows a map of Flickr photos taken of that species in Yellowstone and the info described above will print in the terminal. Then you can enter another species or exit the program.

Special packages required for this project are:
•	beautifulsoup (used for web scraping)
•	requests
•	flickrapi (used to get info from Flickr)
•	sqlite3 (used to create and manage the SQL database)
•	pandas (used to make a data frame of the SQL database info to make the map and return other info)
•	plotly (used to create the map)

One API key/secret required for this project was the Flickr API key. To get one, you have to make an account then follow the instructions as in this link (https://www.flickr.com/services/api/misc.api_keys.html) 
There was also a token required for mapbox (https://docs.mapbox.com/help/getting-started/access-tokens/) which was used to create the background of the map display. You can make an account then apply for one through the link.

To create the map output, I based my code off of the 5th example in the plotly Scatter Plots on Mapbox in Python page https://plotly.com/python/scattermapbox/ (nuclear waste sites on campuses). Originally, I had hoped to make the map more interactive with clickable links in the hover over popup, but unfortunately that fell outside of my capabilities. The map is still interactive though because you can hover over the point to display the species name. 


