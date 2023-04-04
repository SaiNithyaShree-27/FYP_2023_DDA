import pandas as pd
from flask import Flask, request, render_template, session
from sklearn.ensemble import ExtraTreesClassifier
import sqlite3
import datetime
import warnings
warnings.filterwarnings("ignore")


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


def get_db_conn():
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn.cursor(), conn

def create_table():
    cursor, conn = get_db_conn()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (id INTEGER PRIMARY KEY, name TEXT,phone_number TEXT, email TEXT ,password TEXT)''')
    conn.commit()
def create_table():
    cursor, conn = get_db_conn()
    cursor.execute('''CREATE TABLE IF NOT EXISTS blood_sugar_readings
                      (bid INTEGER PRIMARY KEY,id INTEGER,reading_date DATE ,blood_sugar FLOAT ,FOREIGN KEY (id) REFERENCES users(id))''')
    conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/main',methods=['POST'])
def main():
    return render_template('index.html')

@app.route('/index1')
def index1():
    return render_template('index1.html')

@app.route('/login', methods=['GET','POST'])
def home():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('data.db')
        c = conn.cursor()
        c.execute("select * from users where email = ?" ,(email,))
        data = c.fetchone()
        conn.close()
        if data is not None and password == password:
            session['id'] = data[0]
            return render_template('index1.html')

        else:
            return 'Invalid email or password'


@app.route('/signup', methods = ['GET','POST'])
def signup():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['full-name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        password = request.form['password']
        c.execute("insert into users (name, phone_number, email, password) values (?,?,?,?)", (name, phone_number, email, password))
        conn.commit()
        conn.close()
        return render_template('index.html')
    
@app.route('/home')
def pre_home():
    return render_template('home.html')


# Load the dataset
df = pd.read_csv('meall.csv')
X = df[['Blood_sugar', 'food_type']]
y = df['Recommended food']
# Create an instance of ExtraTreesClassifier with default parameters and fit the model to the data
food_model = ExtraTreesClassifier()
food_model.fit(X, y)


@app.route('/predict', methods=['POST'])
def predict():
    # Get the blood sugar and food type values from the request
    blood_sugar = float(request.form['blood_sugar'])
    food_type = request.form['food_type']

    if request.method == 'POST':
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # get the current date and time
        conn = sqlite3.connect('data.db')

        c = conn.cursor()
        sid = session.get('id')
        c.execute("insert into blood_sugar_readings (blood_sugar, reading_date,id) values (?,?,?)", (blood_sugar, date,sid))
        conn.commit()
        conn.close()

    if blood_sugar > 400:
        return render_template('home.html', blood_sugar=blood_sugar)
    else:
        input_data = [[blood_sugar, food_type]]

        # Use the model to predict the recommended food
        food = food_model.predict(input_data)

        food_list = food[0].split("\n")

        # Render the prediction template with the recommended food
        return render_template('result.html', food=food_list)

@app.route('/graph1',methods=['GET','POST'])
def graph():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    sid = session.get('id')
    # Retrieve the user's blood sugar readings from the database
    c.execute("SELECT blood_sugar, reading_date FROM blood_sugar_readings WHERE id=? AND reading_date >= date('now', '-6 day')", (sid,))
    data = c.fetchall()

    # Convert the readings to a format that can be used by Chart.js
    labels = []
    values = []
    for reading in data:
        labels.append(reading[1])
        values.append(reading[0])

    conn.close()

    return render_template('graph1.html', labels=labels, values=values)




if __name__ == '__main__':
    create_table()
    app.run(debug=True)
