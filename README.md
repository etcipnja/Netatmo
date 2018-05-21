# Problem:

Those of you who wanted to base your decision about watering on actual weather readings (precipitation and temperature)
rather than on soil sensor may find this Farmware interesting.
It allows you to get needed values either from your own netatmo weather station (private mode) or from stations nearby
(community mode).

There is no way to pass parameters between sequences and/or farmware. This is why I decided to store weather in meta of
your watering tool. Any other farmware can read it from there. Only last seven days are saved.
The key in meta is 'current_weather'

'''
{'2018-05-20': {'max_temperature': 20, 'min_temperature': 12, 'rain24': 24.9}, '2018-05-21': {'max_temperature': 35, 'min_temperature': 17.11, 'rain24': 0.02}}
'''

Due to limitation of Netatmo API I can only query what happened "today" (your local timezone)
(need to verify this in TZ other than US/Eastern).
If you want an accurate reading to be recorded - you need to call this farmware at 11:59pm. This way you get complete
reading for a day. Also, in community mode, if you rely on max and min temperature - call this farmware several times a
day, otherwise min will be equal to max because netatmo doesn't provide min and max temperature.

This Farmware will fail if none of selected stations equiped with a rain gauge.

# Reference:

- NORTH-EAST CORNER: (longitude, latitude) of the north-east corner of the region around your garden
   - example: (37.80,-122.38)
- SOUTH-WEST CORNER (longitude, latitude) of the south-west corner of the region around your garden
   - Example: (37.70,-122.52)

If you want to fetch data from your own netatmo weather station - use the following
- NORTH-EAST CORNER: <netatmo_login>
- SOUTH-WEST CORNER: <netatmo_password>


# Installation:

Use this manifest to register farmware
https://raw.githubusercontent.com/etcipnja/Netatmo/master/Netatmo/manifest.json

More details: https://farm.bot

# Bugs:

I noticed that if you change a parameter in WebApplication/Farmware form - you need to place focus on some other
field before you click "RUN". Otherwise old value is  passed to farmware script even though the new value
is displayed in the form.

