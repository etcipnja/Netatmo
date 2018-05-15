import ast
import requests
import numpy
import os
import sys
import datetime
from Farmware import Farmware

class Netatmo(Farmware):
    def __init__(self):
        Farmware.__init__(self,((__file__.split(os.sep))[len(__file__.split(os.sep)) - 3]).replace('-master', ''))

    # ------------------------------------------------------------------------------------------------------------------
    def load_config(self):
        prefix = self.app_name.lower().replace('-', '_')
        self.private_mode = False
        try:
            self.nes=os.environ.get(prefix + "_ne", "(37.80,-122.38)")
            self.sws=os.environ.get(prefix + "_sw", "(37.70,-122.52)")


            self.ne = ast.literal_eval(self.nes)
            self.sw = ast.literal_eval(self.sws)

            if not isinstance(self.ne, tuple) or not isinstance(self.ne[0], float) or not isinstance(self.ne[1], float):
                raise ValueError
            if not isinstance(self.sw, tuple) or not isinstance(self.sw[0], float) or not isinstance(self.sw[1], float):
                raise ValueError
        except:
            self.private_mode=True

    # ------------------------------------------------------------------------------------------------------------------
    def get_access_token(self, login='', password=''):

        client_id = '5aebaf2b11349f98108c093d'
        client_secret = 'HXPqOM0i5fxWCME5xkXhra2WJnO'

        if login != '':
            payload = {'grant_type': 'password',
                       'username': login,
                       'password': password,
                       'client_id': client_id,
                       'client_secret': client_secret}
        else:
            payload = {'grant_type': 'refresh_token',
                       'refresh_token': '5aebaefe0f21e1d8be8b68c2|325edd10a01a14ed5683dd35fd22cac2',
                       'client_id': client_id,
                       'client_secret': client_secret}

        response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
        response.raise_for_status()
        print("Your access token is: {}".format(response.json()["access_token"]))
        print("Your refresh token is: {}".format(response.json()["refresh_token"]))
        print("Expires in: {}m".format(response.json()["expires_in"] / 60))

        return response.json()["access_token"]

    # ------------------------------------------------------------------------------------------------------------------
    def load_weather(self,weather_station):

        today = datetime.datetime.utcnow().strftime('%Y-%m-%d')
        self.weather = {}
        try:
            self.weather=ast.literal_eval(weather_station['meta']['current_weather'])
            if not isinstance(self.weather, dict): raise ValueError
            # leave only last 7 days
            self.weather = {k: v for (k, v) in self.weather.items() if
                            datetime.date.today() - datetime.datetime.strptime(k,'%Y-%m-%d').date() < datetime.timedelta(days=7)}
            self.log('Historic weather: {}'.format(self.weather))
        except Exception as e:
            pass

        if today not in self.weather: self.weather[today]={'max_temperature':None,'min_temperature':None,'rain24':None}
        return self.weather[today]

    # ----------------------------------------------------------------------------------------------------------------------
    def run(self):

        points=self.get("points")
        tools=self.get("tools")
        try:
            watering_tool=next(x for x in tools if 'water' in x['name'].lower())
            weather_station=next(x for x in points if x['pointer_type']=='ToolSlot' and x['tool_id']==watering_tool['id'])
        except:
            self.log("No watering tool detected (I save weatehr into the watering tool meta)")
            pass
        today=self.load_weather(weather_station)

        #using private weather station
        if self.private_mode:
            self.log('Private mode, contacting your weather station')
            params={'access_token': self.get_access_token(self.nes, self.sws)}
            response = requests.post("https://api.netatmo.com/api/getstationsdata", params=params)
            response.raise_for_status()
            data = response.json()["body"]

            if len(data['devices']) == 0:
                raise ValueError("You don't seem to have a weather station?")

            outside = data['devices'][0]['modules'][0]
            rain = data['devices'][0]['modules'][1]
            self.log('max_temp={:.2f}C, min_temp={:.2f}C, rain={:.2f}mm'.format(outside['dashboard_data']['max_temp'],outside['dashboard_data']['min_temp'],rain['dashboard_data']['sum_rain_24']))

            today['max_temperature']=outside['dashboard_data']['max_temp']
            today['min_temperature']=outside['dashboard_data']['min_temp']
            today['rain24']=rain['dashboard_data']['sum_rain_24']

        # using public data
        else:
            self.log('Community mode: {} - {}'.format(self.ne, self.sw))
            params = {
                'access_token': self.get_access_token(),
                'lat_ne': self.ne[0],
                'lat_sw': self.sw[0],
                'lon_ne': self.ne[1],
                'lon_sw': self.sw[1],
                'filter': 'true',
            }

            response = requests.post("https://api.netatmo.com/api/getpublicdata", params=params)
            response.raise_for_status()
            data = response.json()["body"]

            if len(data)==0:
                raise ValueError('No weataher stations found around you, try to enlarge the box')

            self.log("Averaging on {} stations".format(len(data)))
            temperature=[]
            rain24=[]

            for x in data:
                m=x['measures']
                for n in m:
                    if 'res' in m[n]:
                        for t in m[n]['res']:
                            for i in range(0,len(m[n]['type'])):
                                if m[n]['type'][i]=='temperature':
                                    temperature.append(float(m[n]['res'][t][i]))
                    if 'rain_24h' in m[n]:
                        rain24.append(float(m[n]['rain_24h']))

            mean_t=float('{:.2f}'.format(numpy.mean(temperature)))
            mean_r=float('{:.2f}'.format(numpy.mean(rain24)))

            self.log('mean temp: {:.2f}C std: {:.2f}'.format(mean_t,numpy.std(temperature)))
            self.log('mean rain: {:.2f}mm std: {:.2f}'.format(mean_r,numpy.std(rain24)))
            if today['max_temperature']==None: today['max_temperature']=mean_t
            else: today['max_temperature'] = max(mean_t,today['max_temperature'])
            if today['min_temperature'] == None: today['min_temperature']=mean_t
            else: today['min_temperature'] = min(mean_t,today['min_temperature'])
            today['rain24'] = mean_r

        weather_station['meta']['current_weather']=str(self.weather)
        self.post('points/{}'.format(weather_station['id']),weather_station)

# ----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    app = Netatmo()
    try:
        app.load_config()
        app.run()
        sys.exit(0)

    except requests.exceptions.HTTPError as error:
        app.log('HTTP error {} {} '.format(error.response.status_code,error.response.text[0:100]), 'error')
    except Exception as e:
        app.log('Something went wrong: {}'.format(str(e)), 'error')
    sys.exit(1)
