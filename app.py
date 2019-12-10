from flask import Flask, render_template
import pyodbc
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
sns.set_style('darkgrid')

cnx = pyodbc.connect(
    server="azuresqlorange.database.windows.net",
    database="orange_azure",
    user='orange',
    tds_version='7.4',
    password="Supermotdepasse!42",
    port=1433,
    driver = [item for item in pyodbc.drivers()][-1]
)

app = Flask(__name__, 
            template_folder='templates',
            static_folder = 'static')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/genres-by-year/<begin>/<end>')

def genres_by_year(begin=None, end=None):

    """
    Display number of films by genres for each year in a specific range
    
    
    Args :
    
        begin (int) : year to start the range 
        
        end : year to end the range 
        
    Return :
        
        none 
    
    """

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
    plt.show()
    plt.savefig('static/images/plot.png')

    return render_template('genres-by-year.html', url='/static/images/plot.png')

if __name__ == '__main__':
    app.run()
