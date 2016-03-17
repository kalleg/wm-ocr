import dbInsert

username = 'pi'
password = 'piocr111111111111#' #writer


thing = dbInsert.dbInsert('https://sure.testbed.se/db/api/', username, password, 'utilities', 'water.usage')
thing.send(0, 0, 77777)


