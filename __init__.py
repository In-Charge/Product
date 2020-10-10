from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from secrets import token_hex
from sqlalchemy import create_engine

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///individual.db'
app.config['SQLALCHEMY_BINDS'] = {'company': 'sqlite:///company.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

individual_engine = create_engine('sqlite:///individual.db')


class PersonalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    access_token = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Entry %r>' % self.id


class FetchedData(db.Model):
    __bind_key__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    individual_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(200), nullable=False)
    date_fetched = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Entry %r>' % self.id


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        content = request.form['content']
        new_item = PersonalData(content=content, access_token=token_hex(16))

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
        item.content = request.form['content']

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
        query = individual_engine.execute(
            f"SELECT id, content FROM personal_data WHERE id={id} AND access_token='{access_token}'")
        print(query)
        result = query.fetchone()
        print(result)
        wrong = result is None

        if wrong:
            return render_template('fetch.html', wrong=True)
        else:
            content = result[1]
            new_item = FetchedData(individual_id=id, content=content)
            db.session.add(new_item)
            db.session.commit()
            return render_template('fetch.html', wrong=False)
    else:
        return render_template('fetch.html', wrong=False)


if __name__ == '__main__':
    app.run()
