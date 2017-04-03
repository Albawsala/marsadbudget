# -*- coding: utf-8 -*-

from flask import render_template, request, url_for, redirect, g, abort, jsonify
from flask_babel import gettext, get_locale, format_date
from flask_login import login_required, current_user
from common.users import editor_required
from datetime import datetime
import json



def login():
	return redirect('/admin/login?next=%s' % request.args.get('next') or '/')



def index():
	return render_template('index.html',
		page = g.db.find_one('pages', {'nom':'home'}),
	)



def budget_raw_view(year, budget_type):
	try:
		annee = int(year)
	except ValueError:
		return jsonify({'error': 'bad year format'}), 404

	def mapper():
		for elt in g.db.find('budgets', {'annee': annee, 'type':budget_type}, sort=[('budget.total',-1)]):
			obj = {}
			for k in set(['total','compensation','id','titre','icon']).intersection(elt['budget'].keys()):
				obj[k] = elt['budget'][k]
			if elt.get('ministere'):
				ministere = g.db.dereference(elt['ministere'])
				obj['id'] = ministere['abbr']
				obj['titre'] = ministere['nom_court']
			yield obj
	
	return jsonify({'budgets': [x for x in mapper()]})



def budget_etat_view():
	lf_2014 = g.db.find_one('data', {'nom':'LF_2014'}) or abort(404)
	lfc_2014 = g.db.find_one('data', {'nom':'LFC_2014'}) or abort(404)
	return render_template('budget_etat.html',
		lf_2014 = lf_2014['data'],
		lfc_2014 = lfc_2014['data'],
	)



def acces_information_view():
	return render_template('acces_information.html',
		ministeres = g.db.find('ministeres', sort=[('evaluation.total',-1)]),
		page = g.db.find_one('pages', {'nom':'classement'}),
	)



def ministere_view(ministere_id):
	ministere = g.db.find_one('ministeres', {'abbr': ministere_id}) or abort(404)
	budgets = g.db.find('budgets', {'ministere.$id': ministere['_id']}, sort=[('annee',1),('type',1)])
	mapper = lambda x: {
		'budget': x['budget'],
		'annee': x['annee'],
		'type': x['type'],
	}
	return render_template('ministere.html',
		ministere = ministere,
		budget_labels = g.db.find_one('data', {'nom':'budget_labels'}),
		budgets = map(mapper, budgets),
	)



def wiki_view():
	if g.lang_code == 'ar':
		alphabet = u'ابتثجحخدذرزسشصضطظعغفقكلمنهوي'
	else:
		alphabet = u'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

	return render_template('wiki.html',
		lettres = g.db.find('wiki', {'lang':g.lang_code}).distinct('lettre'),
		wiki = g.db.find('wiki', {'lang':g.lang_code}, sort=[('lettre',1)]),
		alphabet = alphabet,
	)



def processus_budgetaire_view():
	today = datetime.now().replace(day=1)
	return render_template('processus_budgetaire.html',
		etapes = g.db.find('processus', sort=[('order',1)]),
		months = [today.replace(month=x) for x in xrange(1,13)],
		page = g.db.find_one('pages', {'nom':'processus_budgetaire_intro'}),
	)



def focus_view(focus_id):
	if focus_id == 'LF2016':
		return render_template('focus_LF2016.html')
	return render_template('focus.html', focus_id = focus_id)



def page_view(page_id):
	page = g.db.find_one('pages', {'nom':page_id}) or abort(404)
	return render_template('page.html', page = page)

def faq():
	faqs = g.db.find('faq',sort=[('num_question',1)])
	return render_template('faq.html',faqs = faqs)


#les actualitées
def actualite(page):
	try:
                page=int(page)
        except:
                page = 0
	posts =[]
	nbr_par_page = 4
	posts_actualite = g.db.find('article',sort=[('date',-1)])
	posts_total =posts_actualite.count()
	nbr_page_max = posts_total // nbr_par_page
	if(posts_total%nbr_par_page > 0 ):
		nbr_page_max+=1
	debut, fin = pagination(posts_total,nbr_page_max,nbr_par_page,int(page))

	for post in posts_actualite[debut:fin]:
		image = g.db.find_one('files',{'_id':post['image'].id})
		post['image']=image['filename']
		post['contenu']['ar']=post['contenu']['ar'][0:200]
                post['contenu']['fr']=post['contenu']['fr'][0:200]
		posts.append(post)
	return render_template('actualite.html', posts = posts, page = page, nbrPage = nbr_page_max )


#def actlte(pagen=0):
#	try:
#		pagen = int(pagen)
#	except ValueError:
#		return abort(404)
#	max_posts = 2
#	post_list = []
#	posts = g.db.find('article',sort=[('date',-1)])
#	post_list = [ post for post in posts ]
#	nposts = post_list.__len__()
#	if pagen*max_posts >= nposts or pagen <0:
#		return abort(404)
#	else:
#		post_list =  post_list[pagen*max_posts:pagen*max_posts + max_posts]
#		for post in post_list:
#			image = g.db.find_one('files',{'_id':post['image'].id})
#			post['image']=image['filename']
#			post['contenu']['ar']=post['contenu']['ar'][0:200]
 #               	post['contenu']['fr']=post['contenu']['fr'][0:200]
#	return render_template("actualite.html" , posts = post_list, page = pagen, nbrPage = nposts/max_posts if float(nposts)%max_posts == 0 else (nposts/max_posts)+1 )

def article(article_id):
	post = g.db.find_one('article',{'_id':article_id})
	image_article = g.db.find_one('files',{'_id':post['image'].id})
	return render_template('article.html', post = post, image_article = image_article)


def test(page):
	#return "salut2"
	ch= "chaine envoyée count=10 page_max=4 nbr_par_page=3 et page="+str(page)
	debut , fin = pagination(10,4,3,int(page))
	#return "test"
	return ch+"***********debut="+str(debut)+" fin="+str(fin)

def pagination(count, page_max, nbr_par_page, page):	
	if page>(page_max-1) or page<0:
		debut = 0
		fin = nbr_par_page+debut
	else:
		if page==page_max-1 :
			fin = count
			debut = page*nbr_par_page
		else:
			debut= page*nbr_par_page
			fin = debut + nbr_par_page
	return ( debut ,fin )
	
	
#def widgets_visual_editor():
#	return render_template('visual_editor.html')
