"""
Application entry point.
"""
from hbnb.app import create_app

app = create_app('development')

if __name__ == '__main__' or __name__ == 'hbnb.run':
    app.run(debug=True)

