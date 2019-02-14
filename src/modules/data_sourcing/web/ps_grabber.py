import time

import requests
import schedule
import logging
import datetime
import json

class PS_Grabber:
    def __init__(self):
        self._task = None
        self._logger = logging.getLogger(self.__class__.__name__ + "_logger")
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.DEBUG)

        self._xboris_url = "https://edataex.posta.si/xboris/api/GetData"

        self._status_code = {
            200: "OK", 401: "AuthenticationError", 404: "NoData", 405: "InvalidArguments", 500: "ServerError"
        }

    def schedule(self, period=1): #TODO change period
        schedule.every(period).minutes.do(self._scrape)

    def _scrape(self):
        try:
            payload = {"DateRequest": datetime.date.today().strftime('%Y%m%d')}

            headers = {
                'Content-Type': "application/json",
                'Authorization': "Basic SUpTWEJvcklTOnNhaHJoZ2V3XzQzN2Ryc2h3MzQ1NjM=",
            }

            req = requests.post(self._xboris_url, data=json.dumps(payload), headers=headers, verify=False)



            if req.status_code == 200:
                data = json.loads(req.content)
                self._logger.debug("Request OK, read {} records".format(len(data["xBorISData"])))
            else:
                self._logger.error("[{}] {} : {}".format(req.status_code, self._status_code[req.status_code], req.text))
        except Exception as e:
            self._logger.error(e)


if __name__ =='__main__':

    logging.basicConfig(level=logging.DEBUG)

    xb = PS_Grabber()

    xb.schedule()

    while True:
        time.sleep(1)
        schedule.run_pending()

