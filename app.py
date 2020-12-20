from flask import Flask

import folium
import pandas as pd
import geopandas as gpd
import requests

app = Flask(__name__)

@app.route("/")
def index():
    # Accessing API data using the python "requests" module
    response = requests.get("https://ng-covid-19-api.herokuapp.com/")
    data_json = response.json()

    # Loading the Nigeria geojson file as a pandas Dataframe using "geopandas" python package
    df = gpd.read_file("The_Naija_Poly.geojson")

    # Helper function to help integrate the API based data with the geojson based dataframe together
    def get_stats(df, data):
        if df == "Federal Capital Territory":
                
            if data == "confirmed":
                case = data_json["states"]["FCT"][0]["confirmed"]
                return int(case.replace(",", ""))
            elif data == "discharged":
                discharge = data_json["states"]["FCT"][0]["discharged"]
                return int(discharge.replace(",", ""))
            elif data == "death":
                death = data_json["states"]["FCT"][0]["deaths"]
                return int(death.replace(",", ""))
        else:
            if data == "confirmed":
                case = data_json["states"][df][0]["confirmed"]
                return int(case.replace(",", ""))
            elif data == "discharged":
                discharge = data_json["states"][df][0]["discharged"]
                return int(discharge.replace(",", ""))
            elif data == "death":
                death = data_json["states"][df][0]["deaths"]
                return int(death.replace(",", ""))

    # Helper function implementation
    df["Confirmed Cases"] = df["Name"].apply(get_stats, data = "confirmed")
    df["Discharged"] = df["Name"].apply(get_stats, data = "discharged")
    df["Death"] = df["Name"].apply(get_stats, data = "death")

    # Implementation of Folium Chloropeth Map using the "folium" python package
    total = df["Confirmed Cases"].max()

    folium_map = folium.Map(location = [9.0820, 8.6753],tiles = "Mapbox Control Room", zoom_start = 6, min_zoom = 6, max_zoom = 7,
                    max_lat =16 , max_lon =15 , min_lat = 2 , min_lon =1, max_bounds = True )

    chloro = folium.Choropleth(
        geo_data= df,
        name='choropleth',
        data=df,
        columns=['Name', 'Confirmed Cases'],
        key_on='properties.Name',
        fill_color= "YlOrRd",
        #bins = [0, 100, 400, 700, 900, 1000, 1200, 1500, total+1],
        bins = [0, 0.015*total, 0.15*total, 0.3*total, 0.7*total,total+1],
        fill_opacity=1,
        line_opacity=1,
        legend_name='Confirmed Cases',
        highlight = True,

    ).add_to(folium_map)

    for i in range(0, len(df["Name"])):
        
        temp = df.iloc[i]["Name"]
        if temp == "Federal Capital Territory":
            temp = "FCT"
            
        folium.Marker([df.iloc[i]["lon"], df.iloc[i]["lat"]], icon = folium.DivIcon(html = f"""<div style = "font-family: fantasy
                        ; color: black; font-size: smaller; font-weight: boldest"> 
                        {"{}".format(temp) }</div>  """)).add_to(folium_map) 

    chloro.geojson.add_child(folium.features.GeoJsonTooltip(["Name", "Confirmed Cases", "Discharged", "Death"]))

    folium.LayerControl().add_to(folium_map) 

    return folium_map._repr_html_()

if __name__ == "__main__":
    app.run()