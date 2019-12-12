from flask import Flask, render_template, request, redirect #flask framework packages
import pandas as pd #manage dataframes
from matplotlib import pyplot as plt #manage plot parameters
import seaborn as sns #make plots
sns.set_style('darkgrid') #set a plot style

from flask_bootstrap import Bootstrap #manage bootstrap front-end framework
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Text, Separator

from flask_wtf import FlaskForm #manage forms
from wtforms import  StringField, IntegerField, validators #field types
from wtforms.validators import DataRequired

import pyodbc #manage db connection 
from dotenv import load_dotenv #manage secret keys
import os #manage app files 

project_folder = os.path.expanduser('~/ced-sql-flask-app')  
load_dotenv(os.path.join(project_folder, '.env'))

cnx = pyodbc.connect(
    server=os.getenv('SERVER'),
    database=os.getenv('DATABASE'),
    user=os.getenv('USER'),
    tds_version=os.getenv('TDS_VERSION'),
    password=os.getenv('PASSWORD'),
    port=os.getenv('PORT'),
    driver = [item for item in pyodbc.drivers()][-1]
)


app = Flask(__name__, 
            template_folder='templates',
            static_folder = 'static')

app.config['SECRET_KEY'] = 'secret key' #generate a secret key used by forms
Bootstrap(app)
nav = Nav(app)

nav.register_element('my_navbar', Navbar(
    'Movie dashboard',
    View('Home Page', 'home')))




nav.init_app(app)

class YearsRange(FlaskForm): #define form to get values for genres_by_years() function
    begin = IntegerField('Begin', [validators.DataRequired()])
    end = IntegerField('End', [validators.DataRequired()])

@app.route('/', methods=['GET', 'POST'])
def home():
    year_range_form = YearsRange() #create a form

    if request.method == "POST" and year_range_form.validate_on_submit():
        range_begin = year_range_form.begin.data 
        range_end = year_range_form.end.data
        return redirect(f'/genres-by-year/{range_begin}/{range_end}')    
    return render_template('home.html', year_range_form=year_range_form)

@app.route('/genres-by-year/<int:begin>/<int:end>')

def genres_by_year(begin=None, end=None):

    """
    Display number of films by genres for each year in a specific range
    
    
    Args :
    
        begin (int) : year to start the range 
        
        end : year to end the range 
        
    Return :
        genres-by-year.html (HTML) : HTML template to display the visualization
        url (str) : Url of generated png from the visualization
         
    
    """

    os.remove('static/images/plot.png') #remove previous visualization

    query = f""" SELECT COUNT(CAST(amg.genre AS CHAR)) as films_by_genre, CAST(amg.genre AS CHAR) as genre, am.year
    FROM analysis_movies_genres amg
    LEFT JOIN analysis_movies AS am
    ON am.id = CAST(CAST(amg.movie_id AS CHAR) AS INT)
    WHERE am.year BETWEEN {begin} AND {end} 
    GROUP BY CAST(amg.genre AS CHAR), am.year
    ORDER BY am.year
    """

    df = pd.read_sql(query, cnx)
    
    plt.figure(figsize=(12,8))
    sns.barplot(x= 'year', y='films_by_genre', hue='genre', data=df)
    plt.title(f'Number of films by genre from {begin} to {end}')
    plt.savefig('static/images/plot.png')

    return render_template('genres-by-year.html', url='/static/images/plot.png')

if __name__ == '__main__':
    app.run(debug=True)
