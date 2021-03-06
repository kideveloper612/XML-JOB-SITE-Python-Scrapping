import os
import xml.etree.cElementTree as ET
from xml.etree import ElementTree
from xml.dom import minidom
import html
import mysql.connector


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(html.unescape(elem), 'utf-8')
    rep = minidom.parseString(rough_string)
    return rep.toprettyxml(indent="  ")


def generator_xml(lines, filename):
    filename = 'output/' + filename
    root = ET.Element("jobs")

    for line in lines:
        ET.SubElement(root, "job", {
            'Employer': line[0],
            'Title': line[1],
            'Sector': line[2],
            'Location': line[3],
            'Provider': line[4],
            'Link': line[5]
        })

    output_file = open(filename, 'w')
    output_file.write(prettify(root))
    output_file.close()


def Add():
    path = 'output/'
    lines = []
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="test"
    )
    for origin, directories, files in os.walk(path):
        for file in files:
            print(file, '===========================================================================')
            base_tree = ElementTree.parse(path + file).getroot()
            for item in base_tree.iter('job'):
                employer = item.attrib['Employer']
                title = item.attrib['Title']
                sector = item.attrib['Sector']
                location = item.attrib['Location']
                provider = item.attrib['Provider']
                link = item.attrib['Link']
                line = [employer, title, sector, location, provider, link]
                if line not in lines:
                    if connection.is_connected():
                        cursor = connection.cursor()
                        sql = "INSERT INTO xml (Employer, Title, Sector, Location, Provider, Link) VALUES (%s, %s, " \
                              "%s, %s, %s, %s) "

                        cursor.execute(sql, line)
                        print(line)
                        connection.commit()
                    lines.append(line)
        # generator_xml(lines=lines, filename='Total.xml')
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")


if __name__ == '__main__':
    print('=============================Start===============================')
    Add()
    print('============================= The End ===========================')
