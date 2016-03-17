import httplib, urlparse, base64

class dbInsert:
    def __init__(self, host, username, password, dbname, table):
        p = urlparse.urlparse(host)
        self.host = p.netloc
        self.path = p.path
        self.username = username
        self.password = password
        self.dbname = dbname
        self.table = table

    def send(self, house, meter, value, time= -1):
        conn = httplib.HTTPSConnection(self.host)

        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        headers = {"Authorization": "Basic %s" % base64string, "Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        if time < 0:
            params = self.table + ' value=' + str(value) + ",house=" + str(house) + ",meter=" + str(meter)
        else:
            params = self.table + ' value=' + str(value) + ",house=" + str(house) + ",meter=" + str(meter) + " " + str(time)

        conn.request('POST', self.path + 'write?db=' + self.dbname, params, headers)

        #uncomment for response /debug
        #response = conn.getresponse()
        #print response.status, response.reason, response.read()


