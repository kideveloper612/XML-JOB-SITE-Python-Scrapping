from xml.etree import ElementTree
# import mysql.connector

dom = ElementTree.parse('Total.xml')
root = dom.getroot()
# compose the argument list in one line, drop the big copied/pasted block
args_list = ([t['Employer'] for t in root.iter('job')])

print(args_list)
exit()
# db connection code is unchanged
# db = mysql.connector.Connect(host = 'localhost', user = 'root', password ='root' , database = 'nldb_project')
# cur = db.cursor()
# # this part could be optimized with a dictionary to relate to the tag names
# query = "INSERT INTO profiles(`prof_ticker`,`name`,`address`,`phonenum`,`website`,`sector`,`industry`,full_time`,`bus_summ`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

# # create the tuples from the argument list
# sqltuples = list(zip(*args_list))

# # execute query (unchanged)
# cur.executemany(query,sqltuples)