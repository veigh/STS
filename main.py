from time import sleep

from db_interface import DBInterface
from xml_handler import XMLHandler

INTERVAL_MINUTES = 5


def run_send_script(row):
    xml_handler = XMLHandler(row)

    xml_handler.generate_xml()
    xml_handler.validate_xml()

    # invia il file XML al sistema TS
    xml_handler.send_xml()


def db_read_and_process():
    rows = DBInterface.get_rows()

    # set matching rows to "ready for processing" state
    for row in rows:
        DBInterface.set_ready(row)

    for row in rows:
        # create and send XML for every matching row
        run_send_script(row)

        # set matching rows to "processing finished" state
        DBInterface.set_finished(row)


if __name__ == '__main__':
    while True:
        db_read_and_process()
        sleep(INTERVAL_MINUTES * 60)
