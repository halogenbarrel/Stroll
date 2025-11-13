
# Stroll
## Details
Stroll is a web application built on django, for both front and backend.
## Dev Instructions
This project has an .env file, which is purposefully ignored in every commit. \
**Please** do not force it into your commits.

``` sh
git clone https://github.com/halogenbarrel/Stroll.git && cd Stroll
```
``` sh
python -m venv .env_stroll && source .env_stroll/bin/activate
```

Requirements install
``` sh
pip install -r requirements.txt
```

To start up the dev server
``` sh
python app/manage.py runserver
```

### Contributing

Update any requirements that may have been added
``` sh
pip freeze > requirements.txt
```

please make ur commits look nice-ish :)
