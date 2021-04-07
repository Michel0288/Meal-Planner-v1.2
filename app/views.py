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
from .forms import RecipeForm, SignUpForm, LoginForm, SearchForm,KitchenForm
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

###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
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
            flash('Error.', 'danger')
            return "error"
        # user = UserProfile.query.filter_by(username=username).first()
        # if user is not None and check_password_hash(user.password,password):
        #     remember_me = False
        #     if 'remember_me' in request.form:
        #         remember_me = True
        #     login_user(user, remember=remember_me)
        #     flash('Login successful!', 'success')
        #     return redirect(url_for("secure_page"))
        # else:
        #     flash('Username or password is incorrect.', 'danger')   
    flash_errors(form)
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.pop('loggedin', None)
    session.pop('mealcart', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))    

@app.route("/kitchen_stock")
def kitchen_stock():
    form=KitchenForm()
    return render_template('kitchen_stock.html', form=form)



@app.route("/profile")
# @login_required
def profile():
   

    # cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cur.execute('SELECT * FROM recipe WHERE recipe_id = %s', (p_meals['recipe_id']))     
    # p_recipe = cur.fetchall()
    # cur.close()
    


    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if "loggedin" in session:
        cur.execute('SELECT * FROM account WHERE account_id = %s', (session['id'],))        
        user = cur.fetchone()
        # firstname = user['firstname']
        # lastname = user['lastname']
        # username = user['username']
        # firstname = user['firstname']
        # age = user['age']
        # gender = user['gender']
        # weight = user['weight']
        # height = user['height']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cur.execute('SELECT * FROM meal_plan join instructions on recipe_id join ingredients on recipe_id WHERE account_id = %s and', (session['id'],)) 
        cur.execute('SELECT * FROM meal_plan JOIN instructions ON instructions.recipe_id=meal_plan.recipe_id JOIN recipe ON recipe.recipe_id=meal_plan.recipe_id JOIN ingredients ON ingredients.recipe_id=meal_plan.recipe_id')     
        p_meals = cur.fetchall()
        cur.close()
        
    return render_template("profile.html", user=user,p_meals=p_meals)

@app.route('/results', methods = ['GET', 'POST'])
def results():
    recipeform=RecipeForm()

    if request.method == 'GET':
        return render_template('recipe.html', form=recipeform)
    else:
        input_values = request.form.getlist('input_text[]')
        input_values2 = request.form.getlist('input_cal')
        return render_template('dynamic_input_results.html',
                               input_values = input_values,input_values2=input_values2)

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
        totalcalories=0
        for i in calories:
            totalcalories+=int(i)
        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO recipe(recipe_name,preparation_time,meal_type,servings,photo,totalcalories) VALUES (%s,%s,%s,%s,%s,%s)", (recipe_name,prep_time,mealtype,servings,filename,totalcalories))
        mysql.connection.commit()
        cur.close()



        # ingredient_name = recipeform.ingredient_name.data
        # calories = recipeform.calories.data
        measurements = recipeform.measurements.data

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT MAX(recipe_id) FROM recipe')        
        recipe_id = cur.fetchone()
        recipe_id=recipe_id['MAX(recipe_id)']
        cur.close()


        for i in range(len(ingredients_name)):
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO ingredients (ingredient_name,calories_count,measurement,recipe_id) VALUES (%s,%s,%s,%s)", (ingredients_name[i], calories[i], measurements,recipe_id))
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

# @app.route("/view_meals")
# def view_meals():

#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
#     if "loggedin" in session:
#         cur.execute('SELECT * FROM recipe ORDER BY recipe_id')        
#         recipes = cur.fetchall()
    
#         return render_template('view_meals.html', recipes=recipes)


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
                # for key,item in session['mealcart'].items():
                #     if int(key)==int(recipe_id):
                #         session.modified=True
                        # meal['quantity'] += 1
                    # Check over part 28 still not working
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
    week_date=request.form.get('week-date')
    if request.method=='POST':
        for key,item in session['mealcart'].items():
            cur=mysql.connection.cursor()
            cur.execute("INSERT INTO meal_plan (meal_week,recipe_id,account_id) VALUES (%s,%s,%s)", (week_date, key, session['id'],))
            mysql.connection.commit()
            cur.close()
        # session.pop('mealcart', None)
        return redirect(url_for('search_meal'))
    return render_template('meal_plan.html')

@app.route("/meal-plan")
def getmeals():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT MAX(meal_week) FROM meal_plan WHERE account_id = %s', (session['id'],))        
    week = cur.fetchone()
    cur.close()
    week=week['MAX(meal_week)']
    #probablt afi pop d time
    #try stroring in list and then pop n add
    #test the date part still not fix 
    # if(week=='None'):
    #     week=week['MAX(meal_week)']+timedelta(days=10)
    newdate = date.today()
    if 'mealcart' not in session:
        return redirect(request.referrer)
    return render_template('meal_plan.html',week=week,newdate=newdate)


@app.route("/meal_detail/<id>")
def meal_detail(id):
    form = SearchForm()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM ingredients WHERE recipe_id = %s', (id,))     
    ingredient = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM recipe WHERE recipe_id = %s', (id,))        
    recipes = cur.fetchall()
    cur.close()

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('SELECT * FROM instructions WHERE recipe_id = %s', (id,))        
    instruction = cur.fetchall()
    cur.close()

    return render_template('meal_detail.html', ingredient=ingredient, recipes=recipes, instruction=instruction)
    # return redirect(url_for("search_meal"))

@app.route("/search_meal", methods=["GET", "POST"])
def search_meal():
    form = SearchForm()

    if request.method == 'POST' and form.validate_on_submit():
        search = form.search.data

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM recipe WHERE recipe_name like %s OR totalcalories <= %s', ('%' + search + '%', search,)) 
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
    if request.method == 'POST' and form.validate_on_submit():
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
        dietaryrestrictions = form.dietaryrestrictions.data 
        goal = form.goal.data
        dailycalories = form.dailycalories.data
        photo = form.photo.data
        filename = secure_filename(photo.filename)
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        cur=mysql.connection.cursor()
        cur.execute("INSERT INTO account (firstname,lastname,username,password,age,gender,height,weight,allergies,dietarylifestyle,dietaryrestrictions,goal,dailycalories,photo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (firstname,lastname,username,password,age,gender,height,weight,allergies,dietarylifestyle,dietaryrestrictions,goal,dailycalories,filename))
        mysql.connection.commit()
        cur.close()
        flash("Signup Successful!", 'success')
        return redirect(url_for('login'))
    return render_template('signup.html',form=form)
###
# The functions below should be applicable to all Flask apps.
###

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
