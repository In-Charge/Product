from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from secrets import token_hex

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///individual.db'
app.config['SQLALCHEMY_BINDS'] = {'company': 'sqlite:///company.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class PersonalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    blood = db.Column(db.String(20), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    access_token = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Entry %r>' % self.id


class FetchedData(db.Model):
    __bind_key__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    individual_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    blood = db.Column(db.String(20), nullable=False)
    date_fetched = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Entry %r>' % self.id


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        blood = request.form['blood']
        new_item = PersonalData(name=name, email=email, phone=phone, blood=blood, access_token=token_hex(16))

        db.session.add(new_item)
        db.session.commit()
        return redirect('/')
    else:
        items = PersonalData.query.order_by(PersonalData.date_created).all()
        return render_template('index.html', items=items)


@app.route('/delete/<int:id>')
def delete(id):
    items_to_delete = PersonalData.query.get_or_404(id)

    try:
        db.session.delete(items_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting the entry'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    item = PersonalData.query.get_or_404(id)

    if request.method == 'POST':
        item.name = request.form['name']
        item.email = request.form['email']
        item.phone = request.form['phone']
        item.blood = request.form['blood']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating the entry'

    else:
        return render_template('update.html', item=item)


@app.route('/company')
def company_db():
    items = FetchedData.query.order_by(FetchedData.date_fetched).all()
    return render_template("company_db.html", items=items)


@app.route('/fetch', methods=['GET', 'POST'])
def fetch():
    if request.method == 'POST':
        id = request.form['id']
        access_token = request.form['access_token']
        query = PersonalData.query.filter_by(id=id).filter_by(access_token=access_token)
        result = query.first()
        wrong = result is None

        if wrong:
            return render_template('fetch.html', wrong=True)
        else:
            name = result.name
            email = result.email
            phone = result.phone
            blood = result.blood
            new_item = FetchedData(individual_id=id, name=name, email=email, phone=phone, blood=blood)
            db.session.add(new_item)
            db.session.commit()
            return render_template('fetch.html', wrong=False)
    else:
        return render_template('fetch.html', wrong=False)


if __name__ == '__main__':
    app.run()
