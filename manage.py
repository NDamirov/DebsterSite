from Debts import manager, User, app

@manager.command 
def deploy():
    pass

if __name__ == '__main__':
    manager.run()