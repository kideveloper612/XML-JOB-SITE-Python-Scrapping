from xml.etree import ElementTree
import mysql.connector
from mysql.connector import Error


def get_data():
    dom = ElementTree.parse('Total.xml')
    root = dom.getroot()
    # compose the argument list in one line, drop the big copied/pasted block
    args_list = (
        [(t.get('Employer'), t.get('Title'), t.get('Sector'), t.get('Location'), t.get('Provider'), t.get('Link')) for t
         in
         root.iter('job')])
    return args_list


try:
    connection_config_dict = {
        'user': 'thame_wordpres_e',
        'password': '0#5wtnIKC6',
        'host': '149.255.61.49',
        'database': 'thamesva_wordpress_0',
    }
    connection = mysql.connector.connect(**connection_config_dict)
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        values = get_data()
        values = ('Peter', 'Lowstreet 4', 'Lowstreet 4', 'Lowstreet 4', 'Lowstreet 4', 'Lowstreet 4')

        cursor = connection.cursor()
        query = "INSERT INTO test (`Employer`,`Title`,`Sector`,`Location`,`Provider`,`Link`) VALUES (%s, %s, %s, %s, " \
                "%s, %s) "
        cursor.execute(
            "INSERT INTO test(`Employer`,`Title`,`Sector`,`Location`,`Provider`,`Link`) VALUES ('Mohan', 'Mohan', "
            "'Mohan', 'M', '2000', '2000')")
except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
