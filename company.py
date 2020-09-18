from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import create_engine


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///company.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

individual_engine = create_engine('sqlite:///individual.db')


class FetchedData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    individual_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(200), nullable=False)
    date_fetched = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Entry %r>' % self.id


@app.route('/')
def company_db():
    items = FetchedData.query.order_by(FetchedData.date_fetched).all()
    return render_template("company_db.html", items=items)


@app.route('/fetch', methods=['GET', 'POST'])
def fetch():
    if request.method == 'POST':
        id = request.form['id']
        access_token = request.form['access_token']
        query = individual_engine.execute(
            f'SELECT id, content FROM personal_data WHERE id={id} AND access_token=\'{access_token}\'')
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
