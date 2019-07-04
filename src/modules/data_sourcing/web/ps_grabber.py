import datetime
import json
import logging
import time

import requests
import schedule

from modules.data_sourcing.database.xboris_dump import XBorISEvent, PostgresConnector


class PS_Grabber:
    def __init__(self, db_connector):
        self._task = None
        self.db_connector = db_connector
        self._logger = logging.getLogger(self.__class__.__name__ + "_logger")

        self._data_url = "https://edataex.posta.si/xboris/api/GetData"

        self._status_code = {
            200: "OK", 401: "AuthenticationError", 404: "NoData", 405: "InvalidArguments", 500: "ServerError"
        }
        self._existing_event_ids = []
        self._load_id_cache()

    def schedule(self, period=10):  # TODO change period
        '''
        Initializes periodical web source polling
        :param period: How often to poll data (minutes), default is 10
        '''

        schedule.every(period).minutes.do(self._scrape)

    def _scrape(self):
        try:
            payload = {"DateRequest": datetime.date.today().strftime('%Y%m%d')}

            headers = {
                'Content-Type': "application/json",
                'Authorization': "Basic SUpTWEJvcklTOnNhaHJoZ2V3XzQzN2Ryc2h3MzQ1NjM=",
            }

            req = requests.post(self._data_url, data=json.dumps(payload), headers=headers, verify=False)

            if req.status_code == 200:
                data = json.loads(req.content)

                self.save_new_events(data)
            else:
                self._logger.error("[{}] {} : {}".format(req.status_code, self._status_code[req.status_code], req.text))
        except Exception as e:
            self._logger.error(e)

    def save_new_events(self, data):
        new_events = []
        for event in data["xBorISData"]:
            if event['Itemid'] not in self._existing_event_ids:
                new_events.append(XBorISEvent(event_id=event['Itemid'], timestamp=int(time.time()), data=event))
                self._existing_event_ids.append(event['Itemid'])
        self.db_connector.store(new_events)

    def _load_id_cache(self):
        '''
        Loads recent (24 hours) event IDs from database for duplicate detection
        '''
        age = time.time() - 60 * 60 * 24  # last 24 hours

        self._existing_event_ids = self.db_connector.retrieve_ids(age=age)


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    db_conn = PostgresConnector(host="localhost")
    poller = PS_Grabber(db_conn)

    poller.schedule(period=30)

    while True:
        time.sleep(30)
        schedule.run_pending()
