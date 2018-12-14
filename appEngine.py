from flask import Flask, render_template, flash, redirect, request, url_for, send_file
from meetupModule import *
import time

app = Flask(__name__)
# Secret key to run Flask secure
app.config['SECRET_KEY'] = '123456789'

# Route to the website
@app.route('/', methods=['GET', 'POST'])
def meetups():
    if request.method =="POST":
        zipcode = request.form['zipcode']
        graph = generateGroupPlots(str(zipcode))
    else:
        zipcode = "Enter a new zipcode"
        graph = generateGroupPlots('98105')
    return render_template('layout.html', zipcode=zipcode, graph=graph)


if __name__ == "__main__":
    app.run()





