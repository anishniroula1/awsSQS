#!/usr/bin/env python
# coding: utf-8

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

# Load the data using pandas
data = pd.read_csv(
    "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
)

# Initialize the Dash app
app = dash.Dash(__name__)

# Set the title of the dashboard
app.title = "Automobile Statistics Dashboard"

# Create the dropdown menu options
dropdown_options = [
    {"label": "Yearly Statistics", "value": "Yearly Statistics"},
    {"label": "Recession Period Statistics", "value": "Recession Period Statistics"},
]

# List of years
year_list = [i for i in range(1980, 2024, 1)]

app.layout = html.Div(
    [
        html.H1(
            "Automobile Sales Statistics Dashboard",
            style={"textAlign": "center", "color": "#503D36", "fontSize": 24},
        ),
        html.Div(
            [
                html.Label("Select Statistics:"),
                dcc.Dropdown(
                    id="dropdown-statistics",
                    options=dropdown_options,
                    placeholder="Select Statistics",
                    style={
                        "width": "80%",
                        "padding": "3px",
                        "fontSize": "20px",
                        "textAlignLast": "center",
                    },
                ),
            ]
        ),
        html.Div(
            dcc.Dropdown(
                id="select-year",
                options=[{"label": i, "value": i} for i in year_list],
                placeholder="Select a year",
                style={
                    "width": "80%",
                    "padding": "3px",
                    "fontSize": "20px",
                    "textAlignLast": "center",
                },
            )
        ),
        html.Div(
            id="output-container", className="chart-grid", style={"display": "flex"}
        ),
    ]
)


# Define the callback function to update the input container based on the selected statistics
@app.callback(Output("select-year", "disabled"), Input("dropdown-statistics", "value"))
def update_input_container(selected_statistics):
    return selected_statistics != "Yearly Statistics"


# Define the callback function to update the output container based on the selected statistics
@app.callback(
    Output("output-container", "children"),
    [Input("select-year", "value"), Input("dropdown-statistics", "value")],
)
def update_output_container(input_year, selected_statistics):
    if selected_statistics == "Recession Period Statistics":
        recession_data = data[data["Recession"] == 1]

        yearly_rec = (
            recession_data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        )
        R_chart1 = dcc.Graph(
            figure=px.line(
                yearly_rec,
                x="Year",
                y="Automobile_Sales",
                title="Average Automobile Sales fluctuation over Recession Period",
            )
        )

        average_sales = (
            recession_data.groupby("Vehicle_Type")["Automobile_Sales"]
            .mean()
            .reset_index()
        )
        R_chart2 = dcc.Graph(
            figure=px.line(
                average_sales,
                x="Vehicle_Type",
                y="Automobile_Sales",
                title="Average Number of Vehicles Sold by Vehicle Type",
            )
        )

        exp_rec = (
            recession_data.groupby("Vehicle_Type")["Total_Expenditure"]
            .sum()
            .reset_index()
        )
        R_chart3 = dcc.Graph(
            figure=px.pie(
                exp_rec,
                values="Total_Expenditure",
                names="Vehicle_Type",
                title="Total Expenditure Share by Vehicle Type during Recessions",
            )
        )

        em_tysa = (
            recession_data.groupby("Vehicle_Type")
            .agg({"Unemployment_Rate": "mean", "Automobile_Sales": "mean"})
            .reset_index()
        )
        R_chart4 = dcc.Graph(
            figure=px.bar(
                em_tysa,
                x="Unemployment_Rate",
                y="Automobile_Sales",
                color="Vehicle_Type",
                title="Effect of Unemployment Rate on Vehicle Type and Sales",
            )
        )

        return [
            html.Div(
                className="chart-item",
                children=[R_chart1, R_chart2],
                style={"display": "flex"},
            ),
            html.Div(
                className="chart-item",
                children=[R_chart3, R_chart4],
                style={"display": "flex"},
            ),
        ]
    elif input_year and selected_statistics == "Yearly Statistics":
        yearly_data = data[data["Year"] == input_year]

        yas = data.groupby("Year")["Automobile_Sales"].mean().reset_index()
        Y_chart1 = dcc.Graph(
            figure=px.line(
                yas, x="Year", y="Automobile_Sales", title="Yearly Automobile Sales"
            )
        )

        totmonsal = yearly_data.groupby("Month")["Automobile_Sales"].sum().reset_index()
        Y_chart2 = dcc.Graph(
            figure=px.line(
                totmonsal,
                x="Month",
                y="Automobile_Sales",
                title="Total Monthly Automobile Sales",
            )
        )

        avr_vdata = (
            yearly_data.groupby("Vehicle_Type")["Automobile_Sales"].mean().reset_index()
        )
        Y_chart3 = dcc.Graph(
            figure=px.bar(
                avr_vdata,
                x="Vehicle_Type",
                y="Automobile_Sales",
                title=f"Average Vehicles Sold by Vehicle Type in the year {input_year}",
            )
        )

        exp_data = (
            yearly_data.groupby("Vehicle_Type")["Advertisement_Expenditure"]
            .sum()
            .reset_index()
        )
        Y_chart4 = dcc.Graph(
            figure=px.pie(
                exp_data,
                values="Advertisement_Expenditure",
                names="Vehicle_Type",
                title=f"Total Advertisement Expenditure by Vehicle Type in the year {input_year}",
            )
        )

        return [
            html.Div(
                className="chart-item",
                children=[Y_chart1, Y_chart2],
                style={"display": "flex"},
            ),
            html.Div(
                className="chart-item",
                children=[Y_chart3, Y_chart4],
                style={"display": "flex"},
            ),
        ]
    else:
        return None


# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
