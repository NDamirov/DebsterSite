import os
import click
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db, mail
from app.models import User, Debt, Vault, VaultPayment, VaultSubscription
from flask_script import Shell, Manager

app = create_app()
migrate = Migrate(app, db)
manager = Manager(app)

def make_shell_context():
   return dict(db=db, User=User, Debt=Debt, \
               Vault=Vault, VaultPayment=VaultPayment, \
               VaultSubscription=VaultSubscription, \
               mail=mail, app=app)

manager.add_command('db', MigrateCommand)
manager.add_command("shell", Shell(make_context=make_shell_context))


# with app.app_context():
