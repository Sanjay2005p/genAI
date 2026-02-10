from flask import Flask, render_template
from controller.confige import config
from controller.database import db
from controller.model import User, role, user_role
app = Flask(__name__)
