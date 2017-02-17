# CAPNow

A secure and trusted platform that empowers courts to quickly and easily publish case law


## Development

CAPNow requires Python 3.

### Setup your vitual env and install the requirements
`mkvirtualenv --python=/usr/local/bin/python3.4 capnow; pip install -r requirements.txt`

### Setup webpack
`npm install`

If you change JS or CSS, then before commiting, run `npm run build` to build the production assets.

### Local settings file
Setup your local settings file
`cd settings; touch settings.py`

with about these contents
```
from .settings_common import *

SECRET_KEY = 'your key'
CLOUDCONVERT_API_KEY = 'your key'
```

### Create the DB
```
mysql -u root -psomepasshere
mysql> create database capnow character set utf8; grant all on capnow.* to capnow@'localhost' identified by 'capnow';
mysql -u capnow -pcapnow
mysql> show databases;
```

### Create the DB, load the developer data, and run Django
`fab init_db; python manage.py loaddata fixtures/users.json; fab run`

### Yay!
Open [the local address](http://localhost:9001/) in your browser and let the hacking begin!


## License

Dual licensed under the MIT license (below) and [GPL license](http://www.gnu.org/licenses/gpl-3.0.html).

<small>
MIT License

Copyright (c) 2013 The Harvard Library Innovation Lab

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
</small>
