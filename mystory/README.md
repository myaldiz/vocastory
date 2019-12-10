# <mark style="color:gray;font-size:35px;font-family:courier;">voca</mark><mark style="color:blue;font-weight:bold;font-family:courier;background:#dbdbdb;font-size:35px">story</mark>

## How to install
Please use anaconda for the virtual environment. Install from [command line installer](https://www.anaconda.com/distribution/). Add it to your `$PATH` variable and run the below codes to prepare the environment.
```bash
conda update conda
conda create -n py36 python=3.6 anaconda django spacy
conda activate py36 # Activates the environment named py36
# The followings will download the language files
python -m spacy download en_core_web_sm
```
Now you going to be able to run the website.
```bash
python manage.py runserver
```
## How to populate the database
First you need to ``makemigrations``:
```bash
python manage.py makemigrations
python manage.py makemigrations accounts
python manage.py makemigrations vocastory
```
Commit them:
```bash
python manage.py migrate
```

Manually created database entries are stored in `fixtures` folder, which you can load them by following codes:

```bash
python manage.py loaddata fixtures/accounts.json # for the accounts
python manage.py loaddata fixtures/vocastory.json # for the main models
``` 

In order to save the current state of the DB, run following:
```bash
python manage.py dumpdata vocastory --indent=2 > fixtures/vocastory.json
```
Website is ready to test, guest password is `guest123123`.
