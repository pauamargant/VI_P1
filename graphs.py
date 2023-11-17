import altair as alt
import pandas as pd
import os

#!pip install geopandas
import geopandas as gpd

#!pip install geoplot
import geoplot as gplt

#!pip install geodatasets
import geodatasets

#!pip install h3pandas
import h3pandas
import streamlit as st

import numpy as np

# we disable max_rows in altair
alt.data_transformers.disable_max_rows()

colors = {"bg": "#eff0f3", "col1": "#4f8c9d", "col2": "#6ceac0"}
seq = [
    "#4f8c9d",
    "#5f9aa9",
    "#6fa8b4",
    "#7fb6c0",
    "#8fc4cc",
    "#9fd3d9",
    "#b0e1e5",
    "#c1f0f2",
    "#d2ffff",
]


@st.cache_data
def get_accident_data(fname, sample=False):
    if not sample:
        df = pd.read_csv(fname)
    else:
        df = pd.read_csv(fname).sample(1000)
    # DESCOMENTAR EL SAMPLE

    # We parse the date column as a date
    df["date"] = pd.to_datetime(df["CRASH DATE"], format="%Y-%m-%d")
    print(df.shape)

    # create coolumn weekday/weekend
    df["weekday"] = df["date"].dt.dayofweek
    # We create a column that says wether before or after covid
    df["covid"] = df["date"].dt.year
    # give name
    df["covid"] = df["covid"].replace([2018, 2020], ["before", "after"])
    df["weekday"] = df["weekday"].replace(
        [0, 1, 2, 3, 4, 5, 6],
        ["weekday", "weekday", "weekday", "weekday", "weekday", "weekend", "weekend"],
    )

    return df


@st.cache_data
def get_chart_1(df, w=300):
    return (
        alt.Chart(df)
        .mark_boxplot(size=100)
        .transform_aggregate(accidents="count()", groupby=["weekday", "date", "covid"])
        .encode(
            x=alt.X("weekday:N", title=None),
            y="average(accidents):Q",
            color=alt.Color(
                "weekday:N",
                legend=None,
                scale=alt.Scale(range=[colors["col1"], colors["col2"]]),
            ),
            column="covid:N",
        )
        .properties(width=w)
        # .configure_view(fill=colors["bg"])
    )


def get_map():
    path = geodatasets.get_path("nybb")
    ny = gpd.read_file(path).to_crs("EPSG:4326")
    resolution = 8
    hex_map = ny.h3.polyfill_resample(resolution)
    hex_map = hex_map.to_crs("ESRI:102003")
    return hex_map


def get_buroughs(hex_map):
    hex_buroughs = hex_map.dissolve(by="BoroName")

    ny_df = pd.DataFrame()
    # get dataframe centroid x,y, burough name
    ny_df["x"] = hex_buroughs.centroid.x
    ny_df["y"] = hex_buroughs.centroid.y
    ny_df["BoroName"] = hex_buroughs.index
    return ny_df, hex_buroughs


def calculate_spatial_data(df, hex_map):
    df_coord = df.dropna(subset=["LATITUDE", "LONGITUDE"])
    gdf = gpd.GeoDataFrame(
        df_coord, geometry=gpd.points_from_xy(df_coord.LONGITUDE, df_coord.LATITUDE)
    )[["geometry"]]
    gdf = gdf.set_crs(epsg=4326, inplace=True).to_crs("ESRI:102003")
    # give id to each row in gdf from 1 to n
    gdf = gpd.sjoin(gdf, hex_map, how="right", op="intersects")
    print(gdf.columns)
    gdf_count = (
        gdf.groupby(["geometry", "h3_polyfill"]).size().reset_index(name="counts")
    )
    # set index id
    gdf_count["counts"] = gdf_count.apply(lambda row: row["counts"], axis=1)
    df_geo = pd.DataFrame(gdf_count[["h3_polyfill", "counts"]])

    hex = hex_map.merge(
        df_geo, left_on="h3_polyfill", right_on="h3_polyfill", how="left"
    )
    # to 0 counts sum 1
    hex["counts"] = hex["counts"].apply(lambda x: 1 if x == 0 else x)
    return hex


def plot_map(hex, ny_df, hex_buroughs):
    hexagons = (
        alt.Chart(hex)
        .mark_geoshape()
        .encode(color="counts:Q", tooltip=["h3_polyfill:N", "counts:Q"])
        .project(type="identity", reflectY=True)
        .properties(width=500, height=300)
    )
    labels = (
        alt.Chart(ny_df)
        .mark_text()
        .encode(longitude="x:Q", latitude="y:Q", text="BoroName:N")
    )
    borders = (
        alt.Chart(hex_buroughs)
        .mark_geoshape(stroke="darkgray", strokeWidth=1.25, opacity=1, fillOpacity=0)
        .project(type="identity", reflectY=True)
        .properties(width=500, height=300)
    )
    return hexagons + labels + borders


def save_chart(chart, name):
    folder_path = "/temp"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    chart.save(f"temp/{name}.png", format="png")


def q2_preprocessing(df):
    count_df = df["VEHICLE TYPE CODE 1"].value_counts().reset_index()
    count_df.columns = ["VEHICLE TYPE CODE 1", "count"]
    top_10 = count_df.nlargest(9, "count")

    count_df["VEHICLE TYPE CODE 1"] = np.where(
        count_df["VEHICLE TYPE CODE 1"].isin(top_10["VEHICLE TYPE CODE 1"]),
        count_df["VEHICLE TYPE CODE 1"],
        "Others",
    )
    count_df = count_df.groupby("VEHICLE TYPE CODE 1").sum().reset_index()

    sorted_df = count_df.sort_values(by="count", ascending=False)

    df_part1 = sorted_df[sorted_df["VEHICLE TYPE CODE 1"] != "Others"]
    df_part2 = sorted_df[sorted_df["VEHICLE TYPE CODE 1"] == "Others"]

    sorted_df = pd.concat([df_part1, df_part2])

    sorted_df["percentage"] = (sorted_df["count"] / sorted_df["count"].sum()) * 100

    return sorted_df


def create_chart2(df):
    bar_chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            y=alt.Y(
                "VEHICLE TYPE CODE 1:N",
                title=None,
                sort=df["VEHICLE TYPE CODE 1"].tolist(),
            ),
            x=alt.X(
                "percentage:Q", title="Percentage", scale=alt.Scale(domain=(0, 50))
            ),
            color=alt.Color(
                "VEHICLE TYPE CODE 1:N",
                scale=alt.Scale(
                    domain=df["VEHICLE TYPE CODE 1"].tolist() + ["Others"],
                    range=[colors["col1"]] * (len(df["VEHICLE TYPE CODE 1"]) - 1)
                    + ["gray"],
                ),
                legend=None,
            ),
            tooltip=["VEHICLE TYPE CODE 1", "percentage"],
        )
    )

    text_labels = bar_chart.mark_text(
        fontWeight="bold",
        align="left",
        baseline="middle",
        dx=3,  # Adjust the horizontal position of the labels
    ).encode(
        text=alt.Text(
            "percentage:Q", format=".1f"
        ),  # Format the percentage with one decimal place
        color=alt.condition(
            alt.datum["VEHICLE TYPE CODE 1"] == "Others",
            alt.value("gray"),  # Set the text color to gray for the 'Others' category
            alt.value("black"),  # Set the text color to black for other categories
        ),
    )

    layered_chart = alt.layer(bar_chart, text_labels).configure_axisX(grid=True)
    return layered_chart


def get_weather_data(
    df,
    fnames=[
        "new york city 2018-06-01 to 2018-08-31.csv",
        "new york city 2020-06-01 to 2020-08-31",
    ],
):
    df_weather_1 = pd.read_csv("new york city 2018-06-01 to 2018-08-31.csv")
    df_weather_2 = pd.read_csv("new york city 2020-06-01 to 2020-08-31.csv")
    df_weather = pd.concat([df_weather_1, df_weather_2], axis=0)

    weather_cond = df_weather[["datetime", "conditions"]].copy()
    weather_cond["datetime"] = pd.to_datetime(
        weather_cond["datetime"], format="%Y-%m-%d"
    )

    # Convert 'date' column in df to the same timezone as 'datetime' column in weather_cond
    df["date"] = pd.to_datetime(pd.to_datetime(df["CRASH DATE"]).dt.date)

    # Merge weather conditions with accidents using pd.concat
    data = df.merge(weather_cond, left_on="date", right_on="datetime", how="inner")
    return data


def weather_chart(
    data,
):  # calculate the mean of accidents per day and the mean for each conditions
    per_day = (
        data[["date", "conditions", "CRASH TIME"]]
        .groupby(["date"])
        .count()
        .reset_index()
    )
    mean = per_day["CRASH TIME"].mean()

    # mean per conditions
    per_day_cond = (
        data[["date", "conditions", "CRASH TIME"]]
        .groupby(["date", "conditions"])
        .count()
        .reset_index()
    )
    mean_cond = (
        per_day_cond[["conditions", "CRASH TIME"]]
        .groupby(["conditions"])
        .mean()
        .reset_index()
    )
    mean_cond.columns = ["conditions", "mean_cond"]
    # calcualte difference

    mean_cond["diff"] = mean_cond["mean_cond"].apply(lambda x: x - mean)
    bars = (
        alt.Chart(mean_cond)
        .mark_bar(height=3, orient="horizontal")
        .encode(
            y=alt.Y("conditions:N").sort("x"),
            x="diff:Q",
            color=alt.condition(
                alt.datum.diff > 0,
                alt.value(colors["col2"]),  # The positive color
                alt.value(colors["col1"]),  # The negative color
            ),
        )
        .properties(width=500, height=300)
    )
    points = (
        alt.Chart(mean_cond)
        .mark_point(orient="horizontal", size=100, opacity=1, fillOpacity=1)
        .encode(
            y=alt.Y("conditions:N").sort("x"),
            x="diff:Q",
            color=alt.condition(
                alt.datum.diff > 0,
                alt.value(colors["col2"]),  # The positive color
                alt.value(colors["col1"]),  # The negative color
            ),
            fill=alt.condition(
                alt.datum.diff > 0,
                alt.value(colors["col2"]),  # The positive color
                alt.value(colors["col1"]),  # The negative color
            ),
        )
        .properties(width=500, height=300)
    )
    return bars + points
