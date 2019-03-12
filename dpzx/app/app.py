from flask import Flask, redirect, session, url_for, render_template  # , request, make_response, flash, abort
from flask_script import Manager, Shell
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
import os
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Flask-WTF 使用这个密钥生成加密令牌
app.config['SECRET_KEY'] = 'hhhhzzzz'
# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@10.201.219.3/flaskData'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
# 邮件配置
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '1161558667@qq.com'
app.config['MAIL_PASSWORD'] = 'HHuangzhen610,.'
app.config['FLASK_MAIL_SUBJECT_PROFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = '1161558667@qq.com'
app.config['FLASKY_ADMIN'] = 'hz_temporary@sina.com'

manager = Manager(app)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)
manager.add_command('db', MigrateCommand)


# 电子邮件支持
def send_email(to, subject, template, **kwargs):
    # logging.debug("%s send a mail to %s" % (app.config['FLASK_MAIL_SENDER'], to))
    msg = Message(app.config['FLASK_MAIL_SUBJECT_PROFIX'] + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)


# 定义Role和User模型
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    logger.debug("index")
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            # if app.config['FLASKY_ADMIN']:
            send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session.get('name'),
                           known=session.get('known', False))
    # old_name = session.get("name")
    # if old_name is not None and old_name != form.name.data:
    #     flash("Looks like you have changed your name")
    # session['name'] = form.name.data
    #     return redirect(url_for('index'))
    # return render_template('index.html', form=form, name=session.get('name'))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


@app.shell_context_processor
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


if __name__ == '__main__':
    # manager.add_command("shell", Shell(make_context=make_shell_context))
    # app.run(debug=True)
    manager.run()
