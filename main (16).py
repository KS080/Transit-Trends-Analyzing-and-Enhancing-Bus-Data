import pandas
import sqlite3
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import json
import shutil
import os

# Function to convert CSV data to a SQLite database
def convert(filename, dbname):
  if os.path.exists('bus_data.db'):
      print("Can’t convert: destination file already exists")
      return
  # Reading data from CSV file
  data = pandas.read_csv("bus_data.csv")
  # Connecting to SQLite database
  conn = sqlite3.connect(dbname)
  cur = conn.cursor()
  # Creating a new table for bus data
  cur.execute("DROP table IF EXISTS bus_data")
  cur.execute("CREATE TABLE bus_data (route text, date text, daytype text, rides float)")
  # Inserting data into the table
  for i in range(len(data)):
    formatted_data = {key: f"'{data[key][i]}'" if key in ['route', 'date', 'daytype'] else data[key][i] for key in data}
    a, b, c, d = formatted_data['route'], formatted_data['date'], formatted_data['daytype'], formatted_data['rides']
    cur.execute("INSERT INTO bus_data VALUES (%s, %s, %s, %f)" % (a, b, c, d))
  # Committing and closing the connection
  conn.commit()
  conn.close()

# Converting the CSV file to SQLite database
convert("bus_data.csv", "bus_data.db")

# Function to get data about a specific route
def route_data():
  # Connecting to the SQLite database
  conn = sqlite3.connect("bus_data.db")
  cur = conn.cursor()
  # Calculating average daily ridership
  cur.execute("SELECT AVG(rides) FROM bus_data WHERE route LIKE ?", (input_route,))
  average_rides = cur.fetchone()[0]
  print(f"Average daily ridership for route {input_route} is {average_rides}")
  # Fetching underused days
  cur.execute("SELECT rides FROM bus_data WHERE rides < 200 AND route LIKE ?", (input_route,))
  underused_data = cur.fetchall()
  underused_days = [day[0] for day in underused_data]
  # Calculating total days
  cur.execute("SELECT rides FROM bus_data WHERE route LIKE ?", (input_route,))
  total_days_data = cur.fetchall()
  total_days = [day[0] for day in total_days_data]
  # Computing percentage of underused days
  percentage_underused = (len(underused_days) / len(total_days)) * 100 if total_days else 0
  print(f"Percentage of days for which route {input_route} is underused: {percentage_underused:.2f}%")
  # Closing the database connection
  conn.close()

# Taking user input for a bus route
input_route = input("Enter route: ")
# Getting data for the input route
route_data()

# Function to find the route with the highest one-day ridership each year
def yearly_max():
  year_max_dict = {}
  # Connecting to the SQLite database
  with sqlite3.connect("bus_data.db") as conn:
    cur = conn.cursor()
    # Iterating through the years
    for year in range(2001, 2022):
      cur.execute("""
          SELECT route, MAX(rides)
          FROM bus_data
          WHERE date LIKE '%{}%'
          GROUP BY route
          ORDER BY MAX(rides) DESC
          LIMIT 1
      """.format(year))
      result = cur.fetchone()
      if result:
        year_max_dict[year] = result[0]  # Storing the highest ridership route for each year
  # Writing results to a JSON file
  with open("year_max.json", "w") as json_file:
      json.dump(year_max_dict, json_file, indent=4)
# Executing the function to find yearly max ridership routes
yearly_max()

# Function to plot annual average bus ridership
def my_func():
  # Connecting to the SQLite database
  conn = sqlite3.connect("bus_data.db")
  cur = conn.cursor()
  # Defining years for comparison
  years = ["2018", "2019", "2020", "2021", "2022"]
  annual_ridership = {}
  # Getting average rides for each year
  for year in years:
    cur.execute("SELECT AVG(rides) FROM bus_data WHERE date LIKE '%{}%'".format(year))
    avg_rides = cur.fetchone()[0]
    annual_ridership[year] = avg_rides
  # Closing the database connection
  conn.close()
  # Plotting the data
  plt.style.use("ggplot")
  plt.bar(annual_ridership.keys(), annual_ridership.values(), color=np.random.rand(len(years), 3), alpha=0.7)
  # Customizing the plot
  plt.title("Annual Average Bus Ridership: 2018-2022")
  plt.xlabel("Year")
  plt.ylabel("Average Rides")
  plt.xticks(rotation=45)
  plt.tight_layout()
  plt.show()
  # Saving the plot as a PNG file
  plt.savefig("annual_ridership_trends.png")

# Executing the function to plot annual ridership trends
my_func()

# Function to update the database
def update():
  # Creating a backup of the database
  shutil.copyfile("bus_data.db", "bus_data_backup.db")
  # Connecting to the original database
  conn = sqlite3.connect("bus_data.db")
  cur = conn.cursor()
  # Increasing "rides" by 15% for "U" daytype, rounding down with the floor function
  cur.execute("UPDATE bus_data SET rides = FLOOR(rides * 1.15) WHERE daytype = 'U'")
  # Committing the changes to the database
  conn.commit()
  # Closing the database connection
  conn.close()

# Calling the update function to apply changes to the database
update()
