from website import create_app


#calling the function create_app() from __init__.py to create app
app=create_app()




#Only if we run the main.py file (not import), will we run this line. So that if you import main.py to another file, it won't run this
if __name__=='__main__':
   #start a web server and run the flask application, debug=true means everytime we make a change to the python code its going to automatically re-run the web server
   app.run(debug=True)
