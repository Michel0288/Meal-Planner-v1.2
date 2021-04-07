import pandas as pd
from faker import Faker
from collections import defaultdict
from sqlalchemy import create_engine
fake = Faker()
import random
from random import randint
from datetime import date
date_today = date.today()
f = open("project.sql", "w")

usertable=200000

for i in range(usertable):
    value=randint(0,1000)
    fname=fake.first_name()
    lname=fake.last_name()
    p_age=randint(1,100)
    height=str(randint(1,8))+' '+'ft'+' '+str(randint(1,10))+' '+'in'
    weight=randint(50,1000)
    allergies=[ 'eggs','peanuts','shellfish','strawberries','tomatoes', 'chocolate','pollen','beef','soy']
    lifestyle=['Vegan','Vegetarian','Pescatarian']
    gender=['Male','Female']
    goal=['None','Lose Weight','Gain Weight','Maintain Weight']
    pic=['db1.jpg','db2.png','db3.png','db4.png','db5.png']
    f.write('INSERT INTO account VALUES('+str(i+1)+','+'"'+fname+'"'+','+'"'+lname+'"'+','+'"'+fname+str(value)+'"'+','+'"'+lname+str(value)+'"'+','+str(p_age)+','+'"'+random.choice(gender)+'"'+','+'"'+height+'"'+','+str(weight)+','+'"'+random.choice(allergies)+'"'+','+'"'+random.choice(lifestyle)+'"'+','+'"'+random.choice(goal)+'"'+','+'"'+random.choice(pic)+'"'+');'+'\n')

instruction_id=0
ingredient_id=0
recipetable=600000
recipe_name=['Hard tacos','Burritos','Burgers','Meatballs and rice','Sloppy Joes','Pot Roast','BBQ Ribs','French Dip Sandwiches','Calzones','Egg Rolls','Chicken Pot Pie','Enchiladas','Stuffed Green Pepers','Curry Chicken','Baked Chicken','BBQ Pigtail','Chicken Parmesan','Chicken Nuggets','Chicken Wings','Chicken Fingers','Orange Chicken','Chessy Bacon Chicken','Chicken','Chicken Vk','Meatloaf','Stuffed Pork Chops','Beef And Broccoli','Ham','Beef or Pork Tenderloin','Salmon','Salmon Patties', 'Fish Sticks','Fish N Chips','Crab Cakes', 'Fish Tacos','Smoked Salmon Bagel','Taco Soup','Minestrone Soup','Chicken Noodle Soup','White Chicken Chili','Clam Chowder','Tomato Bisque','Italian Wedding Soup','Cheeseburger Soup','Corn Chowder','Tortellini Soup','French Onion Soup','Jambalaya','Lasagna','Royini Bake','Vegetable Lasagna','Bolognese Sauce And Pasta','Spinach-Bacon' ,'Mac N Cheese',
'Tomato-bacon pasta','Stuffed Pasta Shells','Manicotti','Spaghetti and Meatballs','Pesto Pasta','Eggplant Parmesan','Tortellini','Stroganoff (Chicken Or Beef)','Crockpot Alfredo Lasagna','Pad Thai','Bowtie Pasta & Vegetables','BBQ Chicken Salad','Grilled Cheese Sandwiches','Tostadas','Club Salad','Grilled Chicken','Steak (Grilled Or Boiled)','Kabobs']
instructions=['Preheat the oven to 350 degrees F.','In the bowl of an electric mixer (or using a hand mixer), beat together the brown sugar and butter until fluffy. Beat in the vanilla. Add the eggs one at a time, scraping the bowl after each one.','Mix together the flour, salt and baking soda in a medium bowl. Add it into the creamed mixture in 2 to 3 batches, mixing until just combined. Mix in the oats until just combined.','Use your preferred size cookie scoop (or a regular spoon) to drop portions of dough onto baking sheets, spacing them a couple inches apart. Bake until dark and chewy, 12 to 13 minutes. If youd like a crispier cookie, just cook a little longer!','Let the cookies cool slightly on the baking sheets, then transfer onto a plate for serving.','Add 1/2 cup finely chopped nuts to the flour mixture if youd like a nutty flavor and crunch.']
meal_type=['Breakfast','Lunch','Dinner']
photo=['food1','food2','food3']
ingredient=['Apple','Cheese','Bacon','Rice']
measurement=['1/2 Cup','1 Cup','2 Cups']
for i in range(recipetable):
    id=i+1
    p_time=randint(5,120)
    servings=randint(1,10)
    f.write('INSERT INTO recipe(recipe_id,recipe_name,preparation_time,meal_type,servings,photo,dateadded) VALUES('+str(id)+','+'"'+random.choice(recipe_name)+'"'+','+str(p_time)+','+'"'+random.choice(meal_type)+'"'+','+str(servings)+','+'"'+random.choice(photo)+'"'+','+'"'+str(date_today)+'"'+');'+'\n')
    for x in range(recipetable):
        instruction_id+=(x+3)
        step_no=x+1
        f.write('INSERT INTO instructions VALUES('+str(instruction_id)+','+str(step_no)+','+'"'+random.choice(instructions)+'"'+','+str(id)+');'+'\n')
    for m in range(recipetable):
        ingredient_id+=(m+2)
        calories=randint(1,200)
        f.write('INSERT INTO ingredients VALUES('+str(ingredient_id)+','+'"'+random.choice(ingredient)+'"'+','+str(calories)+','+'"'+random.choice(measurement)+'"'+','+str(id)+');'+'\n')
f.close()
