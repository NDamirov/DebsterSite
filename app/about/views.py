from . import about
from flask import render_template, redirect, url_for, request, flash, make_response

@about.route('/')
def about():
    return render_template('about/about.html')