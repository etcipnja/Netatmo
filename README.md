# Problem:

Those of you who wanted to base your decision about watering on actual weather readings (precipitation and temperature)
rather then on soil sensor may find this Farmware interesting.
It allows you to get needed values either from your own netatmo weather station or from stations nearby.

IMPORTANT: currently this farmware is useless because it only prints information to the log and saves it to a file.
Later I plan to update MLH farmware to use this data for more intelligent watering

# Reference:

- NORTH-EAST CORNER: (longitude, latitude) of the north-east corner of the region around your garden
   - example: (37.80,-122.38)
- SOUTH-WEST CORNER (longitude, latitude) of the south-west corner of the region around your garden
   - Example: (37.70,-122.52)


# Installation:

Use this manifest to register farmware
https://raw.githubusercontent.com/etcipnja/Netatmo/master/Netatmo/manifest.json

# Bugs:

I noticed that if you change a parameter in WebApplication/Farmware form - you need to place focus on some other
field before you click "RUN". Otherwise old value is  passed to farmware script even though the new value
is displayed in the form.

