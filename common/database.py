from pymongo import Connection

connection = Connection('localhost', 24107) #15186 27017
db = connection.obs
db.authenticate('marsad','je97ge8AgEb7OTV8c8c868rh84d4lhMdY0')

db_test = connection.test