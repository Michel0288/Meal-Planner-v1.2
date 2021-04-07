"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
import os
from app import app
from flask import render_template, request, redirect, url_for, flash, session, abort,send_from_directory
from werkzeug.utils import secure_filename
from .forms import RecipeForm, SignUpForm, LoginForm, SearchForm,KitchenForm,SearchForm2
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash
from flask_mysqldb import MySQL
import MySQLdb.cursors
from datetime import date, timedelta


app.config['MYSQL_HOST']='127.0.0.1'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='mealplanner'

mysql=MySQL(app)

#This Home function displays the Supermarket Shopping List
@app.route('/')
def home():
    """Render website's home page."""
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('CALL supermarketlist(%s)',(session['id'],))     
    marketlist = cur.fetchall()
    cur.close()
    return render_template('home.html', marketlist=marketlist)

#This function allows a user to login into the application
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    session['loggedin'] = False
    if request.method == "POST" and form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM account WHERE username = % s AND password = % s', (username, password))        
        user = cur.fetchone()
        
        if user:
            session['loggedin'] = True
            session['id'] = user['account_id']
            session['username'] = user['username']
            flash('Success.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Incorrect Username or Password!.', 'danger')
            return redirect(url_for('login'))

    flash_errors(form)
    return render_template("login.html", form=form)

#This function allows a user to log out of the application
@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('mealcart', None)
    session.pop('id', None)
    session.pop('mealcart',None)
    session.pop('username', None)
    return redirect(url_for('login'))    

#This function allows a user to add ingredients that are in their kitchen
@app.route("/kitchen_stock",  methods = ['GET', 'POST'])
def kitchen_stock():
    form=KitchenForm()
    
    if request.method == 'POST' :
        stock_name = form.stock_name.data
        quantity = form.quantity.data

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("INSERT INTO kitchen_stock(stock_name, quantity) VALUES (%s,%s)", (stock_name, quantity))
        mysql.connection.commit()
        cur.close()
        
        return redirect(url_for('home'))

    return render_template('kitchen_stock.html', form=form)

@app.route("/profile" , methods=["GET", "POST"])
def profile():
    form = SearchForm2()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if "loggedin" in session:
        cur.execute('SELECT * FROM account WHERE account_id = %s', (session['id'],)) 
        user = cur.fetchone()

        if request.method == 'POST' :
            
            search=form.search2.data    

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(' SELECT * FROM recipe WHERE recipe_id IN (SELECT recipe_id FROM meal_plan WHERE meal_week = %s)', (search,)) 
            p_meals = cur.fetchall()
            cur.close()
        else:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('SELECT * FROM recipe WHERE recipe_id IN (SELECT recipe_id FROM meal_plan WHERE account_id=%s)',(session['id'],)) 
            p_meals = cur.fetchall()
            cur.close()
            
    return render_template("profile.html", user=user,p_meals=p_meals, form=form)

@app.route('/results', methods = ['GET', 'POST'])
def results():
    recipeform=RecipeForm()

    if request.method == 'GET':
        return render_template('recipe.html', form=recipeform)
    else:
        input_values = request.form.getlist('input_text[]')
        input_values2 = request.form.getlist('input_cal')
        input_values3=request.form.getlist('input_measurements')
        return render_template('dynamic_input_results.html',
                               input_values = input_values,input_values2=input_values2,input_values3=input_values3)

@app.route('/recipe', methods=['POST', 'GET'])
def recipe():
    recipeform=RecipeForm()

    if request.method == 'POST' :
        recipe_name = recipeform.recipe_name.data 
        instructions = recipeform.procedure.data
        prep_time = recipeform.prep_time.data
        mealtype = recipeform.mealtype.data
        servings = recipeform.servings.data
        photo = recipeform.photo.data
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        ingredients_name = request.form.getlist('input_text[]')
        calories = request.form.getlist('input_cal')
        measurements=request.form.getlist('input_measurements')
        totalcalories=0
        for i in calories:
            totalcalories+=int(i)
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO recipe(recipe_name,preparation_time,meal_type,servings,photo,totalcalories) VALUES (%s,%s,%s,%s,%s,%s)", (recipe_name,prep_time,mealtype,servings,filename,totalcalories))
        mysql.connection.commit()
        cur.close()

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT MAX(recipe_id) FROM recipe')        
        recipe_id = cur.fetchone()
        recipe_id=recipe_id['MAX(recipe_id)']
        cur.close()

        for i in range(len(ingredients_name)):
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO ingredients (ingredient_name,calories_count,measurement,recipe_id) VALUES (%s,%s,%s,%s)", (ingredients_name[i], calories[i], measurements[i],recipe_id))
            mysql.connection.commit()
            cur.close()

        instructionslst=instructions.split(',')
        for i in range(len(instructionslst)):
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO instructions (step_no,instruction,recipe_id) VALUES (%s,%s,%s)", (i, instructionslst[i], recipe_id))
            mysql.connection.commit()
            cur.close()

        flash('You have sucessfully added a recipe', 'success')
        return redirect(url_for('home'))
    
    flash_errors(recipeform)
    return render_template('recipe.html', form=recipeform)

def MagerDicts(dict1,dict2):
    if isinstance(dict1,list) and isinstance(dict2,list):
        return dict1+dict2
    elif isinstance(dict1,dict) and isinstance(dict2,dict):
        return dict(list(dict1.items())+list(dict2.items()))
    return False
    
@app.route("/AddMeal", methods=["GET", "POST"])
def AddMeal():
    recipe_id=request.form.get('recipe_id')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM recipe WHERE recipe_id = %s', (recipe_id,))        
    meal = cur.fetchone()
    cur.close()
    if recipe_id and request.method=="POST":
        DictItems={recipe_id:{'name': meal['recipe_name'],'time':meal['preparation_time'],'type': meal['meal_type'],'servings':meal['servings'],'image':meal['photo']}}
        if 'mealcart' in session:
            print(session['mealcart'])
            if recipe_id in session['mealcart']:
                print("Already in cart")
            else:
                session['mealcart']=MagerDicts(session['mealcart'],DictItems)
                return redirect("search_meal")
        else:
            session['mealcart']=DictItems
            return redirect("search_meal")
    return redirect("search_meal")


@app.route("/deleteitemcart/<code>")
def deleteitemcart(code):
    if 'mealcart' not in session and len(session['mealcart'])<=0:
        return redirect('menu')
    session.modifed=True
    for key,item in session['mealcart'].items():
        if key==code:
            session['mealcart'].pop(key,None)
            flash('Item Removed','success')
            return redirect(url_for('getmeals'))
    return redirect(url_for('getmeals'))

@app.route('/checkout', methods=['POST', 'GET'])
def checkout():
    breakfast=0
    lunch=0
    dinner=0
    week_date=request.form.get('week-date')
    for key,item in session['mealcart'].items():
        if(item['type']=='Breakfast'):
            breakfast+=1
        if(item['type']=='Lunch'):
            lunch+=1
        if(item['type']=='Dinner'):
            dinner+=1
    if(breakfast==5 and lunch==5 and dinner==5 and request.method=='POST'):
        for key,item in session['mealcart'].items():
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO meal_plan (meal_week,recipe_id,account_id) VALUES (%s,%s,%s)", (week_date, key, session['id'],))
            mysql.connection.commit()
            cur.close()
        session.pop('mealcart', None)
        return redirect(url_for('search_meal'))
    flash('SELECT 15 MEALS FOR A MEAL PLAN :- 5 FOR EACH MEAL TYPE','danger')
    flash('You only selected '+str(breakfast+lunch+dinner),'danger')
    return redirect(url_for('getmeals'))

@app.route("/meal-plan")
def getmeals():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT MAX(meal_week) FROM meal_plan WHERE account_id = %s', (session['id'],))        
    week = cur.fetchone()
    cur.close()
    if(week['MAX(meal_week)']!=None):
        week=week['MAX(meal_week)']+timedelta(days=5)
    newdate = date.today()
    if 'mealcart' not in session:
        return redirect(request.referrer)
    return render_template('meal_plan.html',week=week,newdate=newdate)


@app.route("/meal_detail/<id>")
def meal_detail(id):
    form = SearchForm()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('CALL FindIngredients(%s)', (id,))     
    ingredient = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('CALL CalculateTotalCalories(%s)', (id,))     
    total_calories = cur.fetchone()
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM recipe WHERE recipe_id = %s', (id,))        
    recipes = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM instructions WHERE recipe_id = %s', (id,))        
    instruction = cur.fetchall()
    cur.close()

    return render_template('meal_detail.html', ingredient=ingredient, recipes=recipes, instruction=instruction, total_calories=total_calories)

@app.route("/search_meal", methods=["GET", "POST"])
def search_meal():
    form = SearchForm()

    if request.method == 'POST' and form.validate_on_submit():
        search = form.search.data

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cur.execute('CALL SearchFilter(%s)', (search,))        
        recipes = cur.fetchall()

        return render_template('view_meals.html', recipes=recipes, form=form)
    else:

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM recipe ORDER BY recipe_id')        
        recipes = cur.fetchall()
    
        return render_template('view_meals.html', recipes=recipes, form=form)


def get_uploaded_images():
    rootdir = os.getcwd()
    photolist = []

    for subdir, dirs, files in os.walk(rootdir + '/uploads'):
        for file in files:
            photolist += [file]
    photolist.pop(0)
    return photolist

@app.route('/uploads/<filename>')
def get_image(filename):
    rootdir2 = os.getcwd()

    return send_from_directory(os.path.join(rootdir2, app.config['UPLOAD_FOLDER']), filename)

@app.route('/SignUp', methods=['POST', 'GET'])
def signup():
    form = SignUpForm()
    if request.method == 'POST' :
        firstname = form.firstname.data
        lastname = form.lastname.data
        username = form.username.data
        password = form.password.data
        age = form.age.data
        gender = form.gender.data
        height = form.height.data
        weight = form.weight.data
        allergies = form.allergies.data
        dietarylifestyle = form.dietarylifestyle.data
        goal = form.goal.data
        photo = form.photo.data
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO account (firstname,lastname,username,password,age,gender,height,weight,allergies,dietarylifestyle,goal,photo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (firstname,lastname,username,password,age,gender,height,weight,allergies,dietarylifestyle,goal,filename))
        mysql.connection.commit()
        cur.close()
        flash("Signup Successful!", 'success')
        return redirect(url_for('login'))
    return render_template('signup.html',form=form)

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
