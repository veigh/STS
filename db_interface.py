from mysql.connector import connect, Error as MysqlError, errorcode
from typing import Dict, List, Optional

from resources.config import DbConfig

table_name = DbConfig.table_name
status_field = DbConfig.status_field
status_message_field = DbConfig.status_message_field


class DBInterface(object):

    query_get = f'SELECT * FROM {table_name} WHERE {status_field} = 1'

    query_update = f'UPDATE {table_name} SET %(field)s = %(value)s WHERE id = %(id)s'

    query_create = (
        f"CREATE TABLE `{table_name}` ("
        "  `id` int NOT NULL AUTO_INCREMENT,"
        "  `user` varchar(14) NOT NULL,"
        "  `creation` varchar(20) NOT NULL,"
        "  `cf` varchar(20) NOT NULL,"
        "  `cf-proprietario` varchar(20) NOT NULL,"
        "  `p-iva` varchar(20) NOT NULL,"
        "  `ndoc` int NOT NULL,"
        "  `datafatt` varchar(12) NOT NULL,"
        "  `descr1` varchar(30) NOT NULL,"
        "  `qty1` int NOT NULL,"
        "  `um1` varchar(5) NOT NULL,"
        "  `pru1` varchar(10) NOT NULL,"
        "  `iva1` varchar(20) NOT NULL,"
        "  `tot1` varchar(10) NOT NULL,"
        "  `descr2` varchar(30) NOT NULL,"
        "  `qty2` int NOT NULL,"
        "  `um2` varchar(5) NOT NULL,"
        "  `pru2` varchar(10) NOT NULL,"
        "  `iva2` varchar(20) NOT NULL,"
        "  `tot2` varchar(10) NOT NULL,"
        "  `descr3` varchar(30) NOT NULL,"
        "  `qty3` int NOT NULL,"
        "  `um3` varchar(5) NOT NULL,"
        "  `pru3` varchar(10) NOT NULL,"
        "  `iva3` varchar(20) NOT NULL,"
        "  `tot3` varchar(10) NOT NULL,"
        "  `percent-cassa` int NOT NULL,"
        "  `iva-cassa` varchar(20) NOT NULL,"
        "  `totc` varchar(10) NOT NULL,"
        "  `grantot` varchar(10) NOT NULL,"
        "  `tot-iva` varchar(10) NOT NULL,"
        "  `ggt` varchar(10) NOT NULL,"
        "  `pag-tracciato` int NOT NULL,"
        f"  {status_field} int NOT NULL,"
        f"  {status_message_field} varchar(30) NOT NULL,"
        "  PRIMARY KEY (`id`)"
        ") ENGINE=InnoDB"
    )

    query_insert_initial = (
        f"INSERT INTO {table_name} ("
        "  `user`,"
        "  `creation`,"
        "  `cf`,"
        "  `cf-proprietario`,"
        "  `p-iva`,"
        "  `ndoc`,"
        "  `datafatt`,"
        "  `descr1`,"
        "  `qty1`,"
        "  `um1`,"
        "  `pru1`,"
        "  `iva1`,"
        "  `tot1`,"
        "  `descr2`,"
        "  `qty2`,"
        "  `um2`,"
        "  `pru2`,"
        "  `iva2`,"
        "  `tot2`,"
        "  `descr3`,"
        "  `qty3`,"
        "  `um3`,"
        "  `pru3`,"
        "  `iva3`,"
        "  `tot3`,"
        "  `percent-cassa`,"
        "  `iva-cassa`,"
        "  `totc`,"
        "  `grantot`,"
        "  `tot-iva`,"
        "  `ggt`,"
        "  `pag-tracciato`,"
        f"  {status_field},"
        f"  {status_message_field}"
        ") VALUES ("
        "  'vincenzo',"
        "  '2023-01-09 09:30:43',"
        "  'RSSMRA67A07H501O',"
        "  'PROVAX00X00X000Y',"
        "  '01718520768',"
        "  '1',"
        "  '2023-01-09',"
        "  'visita1',"
        "  '1',"
        "  'nr',"
        "  '100.00',"
        "  'esente',"
        "  '100.00',"
        "  'visita2',"
        "  '1',"
        "  'nr',"
        "  '100.00',"
        "  'esente',"
        "  '100.00',"
        "  'visita3',"
        "  '1',"
        "  'nr',"
        "  '100.00',"
        "  'esente',"
        "  '100.00',"
        "  '2',"
        "  'esente',"
        "  '6.00',"
        "  '300.00',"
        "  '0.00',"
        "  '300.00',"
        "  '1',"
        "  '1',"
        "  'unprocessed'"
        ")"
    )

    @staticmethod
    def do_query(query, commit=False, **kwargs) -> Optional[List[Dict]]:
        try:
            cnx = connect(**DbConfig.connect_config)
            cursor = cnx.cursor()

            cursor.execute(query % kwargs)

            rows = [dict(zip(cursor.column_names, r)) for r in cursor]
            [print(r) for r in rows]

            if commit:
                # Make sure data is committed to the database
                cnx.commit()

        except MysqlError as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Already exists.")
            elif err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                raise ValueError("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                raise ValueError("Database does not exist")
            else:
                raise err
        else:
            print("OK")
            cursor.close()
            cnx.close()
            return rows

    @staticmethod
    def create_table(insert_initial_data: bool = False):
        print(f"Creating table '{table_name}'")
        DBInterface.do_query(DBInterface.query_create)

        if insert_initial_data:
            print("Inserting initial data...")
            DBInterface.do_query(DBInterface.query_insert_initial, commit=True)

    @staticmethod
    def update_row(**kwargs):
        DBInterface.do_query(DBInterface.query_update, commit=True, **kwargs)

    @staticmethod
    def get_rows() -> List[Dict]:
        return DBInterface.do_query(DBInterface.query_get)

    @staticmethod
    def set_ready(row):
        DBInterface.update_row(
            field=status_field,
            value=2,
            id=row["id"]
        )
        DBInterface.update_row(
            field=status_message_field,
            value="'ready for processing'",
            id=row["id"]
        )

    @staticmethod
    def set_finished(row):
        DBInterface.update_row(
            field=status_field,
            value=3,
            id=row["id"]
        )
        DBInterface.update_row(
            field=status_message_field,
            value="'processing finished'",
            id=row["id"]
        )


# only for testing purposes
if __name__ == "__main__":
    # DBInterface.create_table()
    DBInterface.get_rows()
    print("Connection to the database is working!")
