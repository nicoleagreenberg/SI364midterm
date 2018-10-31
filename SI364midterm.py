###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError, RadioField # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required # Here, too
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
import requests
import json

## App setup code
app = Flask(__name__)
app.debug = True

## All app.config values
app.config['SECRET_KEY'] = 'hard to guess string from si364'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://nicoleackermangreenberg@localhost:5432/cooking"

db = SQLAlchemy(app)

######################################
######## HELPER FXNS (If any) ########
######################################

def get_or_create_recipes(ingred):
    baseurl = "https://api.edamam.com/search"
    params = {}
    params["q"] = ingred.ingred
    params["app_id"] = 'e4e80ba4'
    params["app_key"] = '648e3b6268fc14c9889a4013d4aaff9b'
    resp = requests.get(baseurl,params=params)
    
    hits = json.loads(resp.text)['hits']
    recipes = []
    for item in hits:
    	title = item['recipe']['label']
    	recipe_url = item['recipe']['url']
    	health = 'No health label'
    	if item['recipe']['healthLabels']:
    		health = item['recipe']['healthLabels'][0].lower()
    	recipe = Recipe(title=title,recipe_url=recipe_url, health=health, ingred_id=ingred.id)
    	recipes.append(recipe)
    	db.session.add(recipe)
    db.session.commit()
    return recipes

##################
##### MODELS #####
##################

class Recipe(db.Model):
	__tablename__ = "recipes"
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String())
	recipe_url = db.Column(db.String())
	health = db.Column(db.String())
	ingred_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'))

	def __repr__(self):
		return "{} (ID: {})".format(self.title, self.id)


class Ingredient(db.Model):
	__tablename__ = "ingredients"
	id = db.Column(db.Integer,primary_key=True)
	ingred = db.Column(db.String())
	recipes = db.relationship("Recipe", backref="Ingredient")

	def __repr__(self):
		return "{} (ID: {})".format(self.ingred, self.id)


###################
###### FORMS ######
###################

class IngredForm(FlaskForm):
	ingred=StringField("Enter an ingredient to find recipes made with it (ingredient must be one word): ", validators=[Required()])
	submit = SubmitField("Search for recipes")


	def validate_ingred(self, field):
		display_name_input = field.data.split()
		if len(display_name_input)>1:
			raise ValidationError("Your display name can only be one word.")

class HealthForm(FlaskForm):
	health = RadioField('Select one dietary restriction to find recipes that fit your diet.', choices=[('dairy-free','Dairy Free'),('high-protein','High Protein'),('low-carb','Low Carb'), ('low-fat','Low Fat'), ('gluten-free','Gluten Free'), ('alcohol-free', 'Alcohol Free'), ('vegan', 'Vegan'), ('sugar-conscious', "Sugar Conscious")], validators=[Required()])
	submit = SubmitField("Search for recipes")

#######################
###### VIEW FXNS ######
#######################

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
	form = IngredForm()

	return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
	form = IngredForm()

	return render_template('500.html'), 500


@app.route('/', methods=['GET'])
def home():
	form = IngredForm()

	return render_template('form.html',form=form)

@app.route('/recipe_results', methods=['POST'])
def recipe_results():
	form = IngredForm()
	ingred = form.ingred.data
	recipes = []

	if form.validate_on_submit():

		ingred_objects = Ingredient.query.all()

	## Find out if ingred is duplicate
		
		
		ingred_check = Ingredient.query.filter_by(ingred=ingred).first() #if something is returned, ingred is True, returns None if there isn't anything in the database

		if ingred_check:
			flash("This ingredient has already been searched for.")
			return redirect(url_for('home'))

	## Get the data from the form
	## If this isn't a duplicate, add it
		if not ingred_check:
			db_ingred = Ingredient(ingred=ingred)
			db.session.add(db_ingred)
			db.session.commit()

			recipes = get_or_create_recipes(ingred=db_ingred)
			if not recipes:
				flash("There are no recipes for this ingredient. Search another one.")
	flash(form.errors)			
	return render_template('recipe_results.html',ingred=ingred,recipes=recipes, form=form)			

@app.route('/all_recipes')
def all_recipes():
	form = IngredForm()

	recipes = Recipe.query.all()
	return render_template('all_recipes.html',recipes=recipes, form=form)

@app.route('/all_ingred')
def all_ingred():
	form = IngredForm()

	ingred = Ingredient.query.all()
	return render_template('all_ingred.html', ingred=ingred, form=form)

@app.route('/health', methods = ["GET"])
def health():
	form = HealthForm(request.args) 
	health_results = None
	health_label = None
	if form.validate():
		health_label = form.health.data
		health_results = Recipe.query.filter_by(health=health_label).all()
		if not health_results:
			flash ("Nothing found - keep searching for ingredients and then try again.")
	return render_template('healthform.html', health_label=health_label, health_results=health_results, form=form)

## Code to run the application...

if __name__ == '__main__':
	db.create_all() # Will create any defined models when you run the application
	app.run(use_reloader=True,debug=True) 

# The usual
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
