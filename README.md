# University_Marketplace
Django==2.2.28
pillow==12.1.0
Python 3.11.14 (WADenv)

Steps to set up the django project

1) Clone repo and cd into the file
   
         git clone https://github.com/2889073s/University_Marketplace.git
   
         cd University_Marketplace

2) Create a virtual enviromenet and activate it - we are using a venv so it’s isolated and doesn’t affect global installs
   - please note the venv is named "WADenv" 
     
             conda create -n WADenv python=3.11

             conda activate WADenv 

3) intall requirements using the requirements.txt

           pip install -r requirements.txt
           
   - ------extra----- if you change the requirments you can update the txt by pip freeze > requirements.txt

4) migrate and run the project

           python manage.py migrate

           python manage.py runserver

   - ------extra------ in vs code to change to the correct interpreter by shift+command+p then "python select interpreter" then "Python 3.11.14 (WADenv)"

7) To fill the database with sample data, run the following command in your terminal after activating your virtual environment (you also need to create a superuser to acess the admin page):

                python population_script.py

               python3 manage.py createsuperuser
   

How to update code when the repo changes:

1) go into project and activate env
   
                cd University_Marketplace
           
                conda activate WADenv
   
3) pull code from github
   
                git pull

    






