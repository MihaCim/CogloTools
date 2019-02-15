import time

import requests
import schedule
import logging
import datetime
import json
import modules.data_sourcing.database.xboris_dump
from modules.data_sourcing.database.xboris_dump import XBorISEvent, PostgresConnector

class PS_Grabber:
    def __init__(self, db_connector):
        self._task = None
        self.db_connector = db_connector
        self._logger = logging.getLogger(self.__class__.__name__ + "_logger")

        self._xboris_url = "https://edataex.posta.si/xboris/api/GetData"

        self._status_code = {
            200: "OK", 401: "AuthenticationError", 404: "NoData", 405: "InvalidArguments", 500: "ServerError"
        }
        self.existing_event_ids = []
        self.load_cache()



    def schedule(self, period=10): #TODO change period
        self._scrape()
        #schedule.every(period).seconds.do(self._scrape)

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

                new_events = []
                for event in data["xBorISData"]:
                    if event['Itemid'] not in self.existing_event_ids:
                        new_events.append(XBorISEvent(event_id=event['Itemid'], timestamp=int(time.time()), data=event))
                        self.existing_event_ids.append(event['Itemid'])

                self.db_connector.store(new_events)
            else:
                self._logger.error("[{}] {} : {}".format(req.status_code, self._status_code[req.status_code], req.text))
        except Exception as e:
            self._logger.error(e)

    def load_cache(self):
        age = time.time() - 60*60*24 #last 24 hours

        self.existing_event_ids = self.db_connector.retrieve_ids(age=age)



if __name__ =='__main__':

    logging.basicConfig(level=logging.DEBUG)
    db = PostgresConnector(host="localhost")
    xb = PS_Grabber(db)


    xb.schedule()

    # while True:
    #     time.sleep(10)
    #     schedule.run_pending()

