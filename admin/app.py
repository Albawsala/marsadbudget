from flask import Blueprint, Flask
from flask_login import LoginManager
try:
	from flaskext.uploads import configure_uploads
except ImportError:
	from flask_uploads import configure_uploads
from files import uploaded_images, uploaded_documents
from common.users import get_user_by_id, get_user_by_token
from common.finders import FinderModifier
import filters
import views
import uwsgi
import jinja2

app = Flask(__name__)
app.config.from_object('admin.conf')
app.config.from_pyfile(uwsgi.opt['conf'])

configure_uploads(app, uploaded_images)
configure_uploads(app, uploaded_documents)

finder = FinderModifier(app)

login_manager = LoginManager()
login_manager.setup_app(app)
login_manager.login_view = 'admin.login'
login_manager.user_loader(get_user_by_id)
login_manager.token_loader(get_user_by_token)

app.jinja_env.filters['featured'] = filters.get_featured
app.jinja_env.filters['json'] = filters.to_json
app.jinja_env.filters['path'] = filters.get_file_url
app.jinja_env.filters['is_list'] = filters.is_list
app.jinja_env.filters['yaml'] = filters.yaml_dump
app.jinja_env.globals['isinstance'] = isinstance
app.jinja_env.globals['list'] = list
app.jinja_env.cache = None

root = Blueprint('admin', __name__, url_prefix='%s/admin' % app.config.get('PREFIX',''))

root.add_url_rule('/', 'index', views.index)

root.add_url_rule('/test', 'test', views.test)
root.add_url_rule('/collections', 'collections', views.collections)
root.add_url_rule('/add/collection', 'add_collection', views.add_collection, methods=['GET', 'POST'])
root.add_url_rule('/del/collection/<collection>', 'del_collection', views.del_collection, methods=['GET', 'POST'])
root.add_url_rule('/edit/collection/<collection>', 'edit_collection', views.edit_collection, methods=['GET', 'POST'])

root.add_url_rule('/documents/<collection>', 'documents', views.documents)
root.add_url_rule('/add/document/<collection>', 'add_document', views.add_document, methods=['GET', 'POST'], defaults={'doc_id':None})
root.add_url_rule('/add/document/<collection>/<doc_id>', 'add_document', views.add_document, methods=['GET', 'POST'])
root.add_url_rule('/del/document/<collection>/<doc_id>', 'del_document', views.del_document, methods=['GET', 'POST'])
root.add_url_rule('/edit/document/<collection>/<doc_id>', 'edit_document', views.edit_document, methods=['GET', 'POST'])
root.add_url_rule('/touch/document/<collection>/<doc_id>', 'touch_document', views.touch_document)
root.add_url_rule('/find/document/<collection>', 'find_document', views.find_document, methods=['POST'])

root.add_url_rule('/files', 'files', views.files)
root.add_url_rule('/add/file', 'add_file', views.add_file, methods=['GET', 'POST'])
root.add_url_rule('/del/file/<file_id>', 'del_file', views.del_file, methods=['GET', 'POST'])
root.add_url_rule('/edit/file/<file_id>', 'edit_file', views.edit_file, methods=['GET', 'POST'])
root.add_url_rule('/find/file', 'find_file', views.find_file, methods=['POST'])
root.add_url_rule('/images', 'images', views.images)
root.add_url_rule('/add/image', 'add_image', views.add_image, methods=['GET', 'POST'])

root.add_url_rule('/login', 'login', views.login, methods=['GET', 'POST'])
root.add_url_rule('/logout', 'logout', views.logout)
root.add_url_rule('/register', 'register', views.register, methods=['GET', 'POST'])
root.add_url_rule('/profile', 'profile', views.profile, methods=['GET', 'POST'])

root.add_url_rule('/add/shortcut/<collection>', 'add_collection_shortcut', views.add_collection_shortcut)
root.add_url_rule('/del/shortcut/<collection>', 'del_collection_shortcut', views.del_collection_shortcut)

root.add_url_rule('/users', 'users', views.users)
root.add_url_rule('/users/<user_id>', 'user_edit', views.user_edit, methods=['GET', 'POST'])

#projects
root.add_url_rule('/projects/add' , 'new_project' , views.add_project , methods=['GET','POST'])
root.add_url_rule('/projects' , 'projects' , views.view_projects)
root.add_url_rule('/projects/edit/<project_id>' , 'edit_project' , views.edit_project , methods=['GET', 'POST'])
root.add_url_rule('/projects/remove/<project_id>' , 'remove_project' , views.delete_project)

#resources
root.add_url_rule('/resources/add' , 'new_resource' , views.add_resources , methods=['GET','POST'])
root.add_url_rule('/resources' , 'resources' , views.show_resources)
root.add_url_rule('/resources/edit/<resource_id>' , 'edit_resource' , views.edit_resource , methods=['GET','POST'])
root.add_url_rule('/resources/delete/<resource_id>', 'remove_resource',views.delete_resource)

#article
root.add_url_rule('/article','articles',views.show_articles)
root.add_url_rule('/article/add','new_article',views.new_articles, methods=['GET','POST'])
root.add_url_rule('/article/edit/<article_id>','edit_article',views.edit_articles, methods=['GET','POST'])
root.add_url_rule('/article/delete/<article_id>','delete_article',views.delete_articles, methods=['GET','POST'])

for rule,endpoint,view,opts in app.config.get('VIEWS', {}).values():
	root.add_url_rule(rule, endpoint, view, **opts)

if 'TEMPLATES' in app.config:
	template_loader = jinja2.ChoiceLoader([
		app.jinja_loader,
		jinja2.FileSystemLoader(app.config['TEMPLATES']),
	])
	app.jinja_loader = template_loader

app.register_blueprint(root)
