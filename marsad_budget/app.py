from flask import Flask, Blueprint, g, abort
from flask_login import LoginManager
from flask_babel import Babel
from flask_uploads import configure_uploads
from pymongo import Connection
from common.finders import Finder
from common.finders import FinderModifier
from common.users import get_user_by_id, get_user_by_token
import filters
import files
import views

app = Flask(__name__)
app.config.from_pyfile('conf.py')

babel = Babel(app, 'ar_TN')

@babel.localeselector
def locale_select():
    return app.config['LANGS'][g.lang_code]

configure_uploads(app, files.uploaded_images)
configure_uploads(app, files.uploaded_documents)

finder = Finder(app)
finderModifier = FinderModifier(app)

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'root.login'
login_manager.user_loader(get_user_by_id)
login_manager.token_loader(get_user_by_token)
app.jinja_env.filters['summerize'] = filters.summerize
app.jinja_env.filters['highlight'] = filters.highlight
app.jinja_env.filters['remove_html']= filters.remove_html
app.jinja_env.filters['lang'] = filters.set_lang_suffix
app.jinja_env.filters['fileurl'] = filters.get_file_url
app.jinja_env.globals['isinstance'] = isinstance
app.jinja_env.globals['int'] = int

root = Blueprint('root', __name__)

root.add_url_rule('/', 'home', views.index)
root.add_url_rule('/login', 'login', views.login)
root.add_url_rule('/wiki', 'wiki', views.wiki_view)
root.add_url_rule('/budget_raw/<year>/<budget_type>', 'budget_raw', views.budget_raw_view)
root.add_url_rule('/budget_etat', 'budget_etat', views.budget_etat_view)
root.add_url_rule('/acces_information', 'acces_information', views.acces_information_view)
root.add_url_rule('/processus_budgetaire', 'processus_budgetaire', views.processus_budgetaire_view)
root.add_url_rule('/<ministere_id>', 'ministere', views.ministere_view)
root.add_url_rule('/focus/<focus_id>', 'focus', views.focus_view)
root.add_url_rule('/page/<page_id>', 'page', views.page_view)
#faq
root.add_url_rule('/faq', 'faq', views.faq)
#resources
root.add_url_rule('/resources_raw/<year>/<resource_type>/<lang>', 'resources_raw', views.resources_raw_view)
# projects
root.add_url_rule('/map' , 'map' , views.map_view)
root.add_url_rule('/govs/<lang>' , 'govs' , views.govs)
root.add_url_rule('/ministeres/<lang>' , 'ministeres' , views.ministeres)
root.add_url_rule('/secteurs/<lang>' , 'secteurs' , views.secteurs)
root.add_url_rule('/projects' , 'projects' , views.projects)
#root.add_url_rule('/widgets/visual_editor', 'widgets_visual_editor',
#views.widgets_visual_editor)
# blog
root.add_url_rule('/blog/', 'actualite', views.actualite, defaults={'page':0})
root.add_url_rule('/blog/<page>', 'actualite', views.actualite)
# article
root.add_url_rule('/article/<article_id>', 'article', views.article)
# search
root.add_url_rule('/search' , 'search' , views.search)

@root.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', g.lang_code)

@root.url_value_preprocessor
def pull_lang_code(endpoint, values):
    lng = values.pop('lang_code')
    lng in app.config['LANGS'] or abort(404)
    g.lang_code = lng

app.register_blueprint(root, url_defaults={'lang_code':'ar'})
app.register_blueprint(root, url_prefix='/<lang_code>')
