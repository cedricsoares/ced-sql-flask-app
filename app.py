from flask import Flask, render_template, send_file, make_response, request
import pyodbc
import io
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
sns.set_style('darkgrid')

app = Flask(__name__, template_folder='./templates')

@app.route('/genre-by-year/<begin>/<end>')

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
    plt.show()
    
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format='png')
    bytes_image.seek(0)

    return render_template('genre-by-year.html', bytes_image= bytes_image)

if __name__ == '__main__':
    app.run(debug=True)