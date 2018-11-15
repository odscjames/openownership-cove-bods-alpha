# openownership-cove-bods-alpha

## Dev installation

    git clone xxxxxxxxxxxxx yyyyyyyyyy
    cd yyyyyyyyy
    virtualenv .ve --python=/usr/bin/python3
    source .ve/bin/activate
    pip install -r requirements_dev.txt
    python manage.py migrate
    python manage.py compilemessages
    python manage.py runserver

