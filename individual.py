from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from secrets import token_hex

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///individual.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class PersonalData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    access_token = db.Column(db.String(200), nullable=False)

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


if __name__ == '__main__':
    app.run()
