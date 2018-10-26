###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
# Import statements
import os
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError# Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import Required # Here, too
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell

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



##################
##### MODELS #####
##################

class Recipe(db.Model):
	__tablename__ = "recipes"
	id = db.Column(db.Integer,primary_key=True)
	title = db.Column(db.String())
	#recipe_url = db.Column(db.String())
	#image_url = db.Column(db.String())
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


#######################
###### VIEW FXNS ######
#######################

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def home():
	form = IngredForm() # User should be able to enter name after name and each one will be saved, even if it's a duplicate! Sends data with GET
	ingred_objects = Ingredient.query.all()

	if form.validate_on_submit():
	
	## Find out if ingred is duplicate
		ingred = form.ingred.data
		
		ingred_check = Ingredient.query.filter_by(ingred=ingred).first() #if something is returned, ingred is True, returns None if there isn't anything in the database
		if ingred_check:
			return redirect(url_for('all_recipes'))

	## Get the data from the form
	## If this isn't a duplicate, add it
		if not ingred_check:
			db_ingred = Ingredient(ingred=ingred)
			db.session.add(db_ingred)
			db.session.commit()
			return redirect(url_for('all_recipes'))
	return render_template('base.html',form=form)

@app.route('/all_recipes')
def all_recipes():
	recipes = Recipe.query.all()
	return render_template('all_recipes.html',recipes=recipes)

@app.route('/all_ingred')
def all_ingred():
	ingred = Ingredient.query.all()
	return render_template('all_ingred.html', ingred=ingred)

## Code to run the application...

if __name__ == '__main__':
	db.create_all() # Will create any defined models when you run the application
	app.run(use_reloader=True,debug=True) 

# The usual
# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!
