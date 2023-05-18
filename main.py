from flask import redirect
from bson import ObjectId
from flask import Flask, render_template, request, session
from flask import url_for
from pymongo import MongoClient
import json
from werkzeug.utils import secure_filename
import os

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired

with open ("config.json", "r") as c:
  params = json.load(c)["params"]


app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'secretkey'

client = MongoClient("mongodb+srv://asad:asad@blogdb.acnss0h.mongodb.net/?retryWrites=true&w=majority")

db = client['blog']
collection = db['posts']




@app.route("/")
def home():
  
    # Get all the blog posts from the database
  posts = collection.find()

  
  
  

  return render_template("index.html",posts=posts, params=params)

@app.route("/post/<post_id>")
def post(post_id):
    # Get the individual blog post from the database
    post = collection.find_one({"_id": ObjectId(post_id)})
    return render_template("post.html", post=post, params=params)


app.config['UPLOAD_FOLDER'] = 'static/images'


class Post:
    def __init__(self, title, content, file,replitlink,githublink):
        self.title = title
        self.content = content
        self.file = file
        self.replitlink = replitlink
        self.githublink = githublink

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    file = FileField('Image')
    replitlink = TextAreaField('Replit', validators=[DataRequired()])
    githublink = TextAreaField('Replit', validators=[DataRequired()])
 

    submit = SubmitField('Submit')



@app.route('/create', methods=['GET', 'POST'])
def create():

  form = PostForm(request.form)
  if form.validate_on_submit():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        file = request.files['file']
        # Save the file to a directory on your server
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        replitlink = request.form['replitlink']
        githublink = request.form['githublink']
        # Save the post data and file name/path to the database
        collection.insert_one({
            "title": title,
            "content": content,
            "file": filename,
            "replitlink": replitlink,
            "githublink": githublink
        })
        return redirect(url_for('home'))
    
  return render_template('create.html',params=params,form=form)
    


    


@app.route("/about")
def about():
  return render_template('about.html',params=params)



@app.route('/admin')
def admin():
    # Check if user is logged in
    if 'user' in session:
        posts = db.posts.find()
        return render_template('admin.html', posts=posts,params=params)
  
    else:
        # Redirect to login page if user is not logged in
        return redirect('/login')


  
class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    file = FileField('Image')
    submit = SubmitField('Save Changes')



@app.route('/edit/<post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    if request.method == 'POST':
        db.posts.update_one({'_id': post['_id']}, {'$set': {'title': request.form['title'], 'content': request.form['content']}})
        return redirect(url_for('admin'))
    return render_template('edit.html', post=post,params=params)


    



@app.route('/delete/<post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    post = db.posts.find_one({'_id': ObjectId(post_id)})
    if request.method == 'POST':
        db.posts.delete_one({'_id': post['_id']})
        return redirect(url_for('admin'))
    return render_template('delete.html', post=post,params=params)


app.secret_key = "admin"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Check if username and password are correct
        if username == 'admin' and password == 'password':
            # Store the user in a session
            session['user'] = username
            # Redirect to the admin panel
            return redirect('/admin')
        else:
            # Display an error message
            error = 'Invalid username or password'
            return render_template('login.html', error=error, params=params)
    else:
        return render_template('login.html',params=params)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/discord')
def discord():
  return redirect('https://discord.gg/rDMJ9ZkVhE')


@app.route('/instagram')
def insta():
  return redirect('https://www.instagram.com/notrana12/')

app.run(host="0.0.0.0", port="8080",debug=True)