import sqlite3


from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging
import sys
# Function to get a database connection.
# This function connects to database with the name `database.db`
db_connection_count = 0  # Global variable to track database connections
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the health check of the web application 
@app.route('/healthz')
def status():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )

    return response
 # Define the metrics of the web application
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    response = app.response_class(
            response = json.dumps({"db_connection_count": db_connection_count, "post_count": post_count}),
            status=200,
            mimetype='application/json'
    )

    return response
# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      logging.warning(f"404 Page Not Found: Article {post_id} does not exist")
      return render_template('404.html'), 404
    else:
      logging.info(f"Article {post['title']} retrieved!")
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logging.info("About Us page retrieved")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            logging.info(f"New article created: {title}")
            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
    # Configure logging to STDOUT and STDERR
   log_file = "app.log"
   logging.basicConfig(level=logging.DEBUG,
                    #format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(sys.stdout),  # STDOUT
                        logging.StreamHandler(sys.stderr),  # STDERR
                        logging.FileHandler(log_file)
                    ])
   app.run(host='0.0.0.0', port='3111')
