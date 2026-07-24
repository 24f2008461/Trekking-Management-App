from flask import session, request, render_template, Blueprint, flash, url_for, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, USER


user_bp = Blueprint("user",__name__)