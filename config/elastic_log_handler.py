import json
import logging
import time

from elasticsearch import Elasticsearch


class ElasticsearchHandler(logging.Handler):
    def __init__(self, host, port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.es = Elasticsearch(f'http://{host}:{port}')

    def emit(self, record):
        log_entry = {
            'timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            'level': record.levelname,
            'message': json.loads(self.format(record))
        }

        self.es.index(index=self.get_index_name(), document=log_entry)

    def get_index_name(self):
        return f'log_{time.strftime("%Y_%m_%d")}'
