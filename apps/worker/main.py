import time
from apps.api.app.db import init_db
if __name__ == '__main__':
    init_db(); print('worker ready: ingestion abstraction active')
    while True: time.sleep(30)
