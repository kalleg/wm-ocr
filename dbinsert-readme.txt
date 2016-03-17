dbInsert has three dependencies; httplib, urlparse & base64
Requests are sent with httplib
The class dbInsert has two methods:

send(house, meter, value)
Requests a single insertion into database. Timestamp is handled automatic by database
Time will be set to the database's current time on retrival of request

send2(house, meter, value, time)
Requests a single insertion into database. Timestamp is handled manually(forth argument).

Note: None of the methods have return types. For debugging uncomment lines regarding reading response.
A '204 No content' is a successful write. A 400 return code is invalid influxdb syntax (followed by a reason).

sources used:
https://docs.influxdata.com/influxdb/v0.10/write_protocols/write_syntax/#http
https://docs.python.org/release/2.6/library/httplib.html