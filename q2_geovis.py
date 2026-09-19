"""
Question 2: Geovisualization with Plotly Express (3 points in total)

In this question, we are going to use plotly express to create a choropleth map 
that shows the life expentancy of each country for the year 2007. The data 
we are going to use is from plotly express gapminder.

For the plot, please satisfy the following requirements:
- color: use the lifeExp column to color the country (1 point)
- color scale: px.colors.sequential.Blues_r (1 point)
- title: '2007 Life Expectancy' (1 point)

*Hint:* Use locations='iso_alpha' setting to specify the geolocation information
Related documentation: https://plotly.com/python/choropleth-maps/

"""

import plotly.express as px
import plotly.io as pio

# opens the figure as a local HTML page in your default browser
pio.renderers.default = "browser"

# load the gapminder dataset
df = px.data.gapminder()
# df.head()


# filter the data for the year 2007
# TODO: complete the code below
df_2007 = df.query()

# create a choropleth map using plotly express
# TODO: complete the code below
q2_fig = 

q2_fig.show()


# If the figure does not open in a browser, un-comment the following line to
# save the figure as a local HTML file and open it locally.

# q2_fig.write_html("q2_fig.html")