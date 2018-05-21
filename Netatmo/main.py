import numpy
from Farmware import *

class Netatmo(Farmware):
    def __init__(self):
        Farmware.__init__(self,((__file__.split(os.sep))[len(__file__.split(os.sep)) - 3]).replace('-master', ''))

    # ------------------------------------------------------------------------------------------------------------------
    def load_config(self):

        super(Netatmo, self).load_config()

        self.private_mode = False
        try:
            self.nes=self.get_arg('ne', "(37.80,-122.38)")
            self.sws = self.get_arg('sws', "(37.70,-122.52)")

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

        client_id = '5afc26dd13475dee138c5873'
        client_secret = 'J6mWnRcq4BRh3CnFOvAI900EEjRJD6LdDpOzMnLWicVqS'

        if login != '':
            payload = {'grant_type': 'password',
                       'username': login,
                       'password': password,
                       'client_id': client_id,
                       'client_secret': client_secret}
        else:
            payload = {'grant_type': 'refresh_token',
                       'refresh_token': '5afc25d7923dfe791f8b5fcc|d6e069df8e512da02731449e80ffdc0e',
                       'client_id': client_id,
                       'client_secret': client_secret}

        response = requests.post("https://api.netatmo.com/oauth2/token", data=payload)
        response.raise_for_status()
        #print("Your access token is: {}".format(response.json()["access_token"]))
        #print("Your refresh token is: {}".format(response.json()["refresh_token"]))
        #print("Expires in: {}m".format(response.json()["expires_in"] / 60))

        return response.json()["access_token"]


    # ----------------------------------------------------------------------------------------------------------------------
    def run(self):

        self.load_weather()
        td = d2s(today_local())
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

            self.weather[td]={}
            self.weather[td]['max_temperature']=outside['dashboard_data']['max_temp']
            self.weather[td]['min_temperature']=outside['dashboard_data']['min_temp']
            self.weather[td]['rain24']=rain['dashboard_data']['sum_rain_24']

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

            if len(temperature)==0 or len(rain24)==0:
                raise ValueError('Did not get data about rain or temperature from stations in this area, try to enlarge the box')
            mean_t=float('{:.2f}'.format(numpy.mean(temperature)))
            mean_r=float('{:.2f}'.format(numpy.mean(rain24)))

            if td not in self.weather:
                self.weather[td]['min_temperature'] = mean_t
                self.weather[td]['max_temperature']=mean_t
            else:
                self.weather[td]['max_temperature'] = max(mean_t,self.weather[td]['max_temperature'])
                self.weather[td]['min_temperature'] = min(mean_t,self.weather[td]['min_temperature'])
            self.weather[td]['rain24'] = mean_r

        self.log('Weather: {}'.format(self.weather))
        self.save_weather()

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
