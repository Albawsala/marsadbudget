# -*- coding: utf-8 -*-

from flask import render_template, request, url_for, redirect, g, abort, jsonify
from flask_babel import gettext, get_locale, format_date
from flask_login import login_required, current_user
from common.users import editor_required
from datetime import datetime
import json
from re import compile , IGNORECASE


def login():
	return redirect('/admin/login?next=%s' % request.args.get('next') or '/')



#def index():
#	return render_template('index.html',
#		page = g.db.find_one('pages', {'nom':'home'}),
#	)
def index():
	budgets 		= g.db.find('budgets',)
	resourcs		= g.db.find('resources',)
	list_resrcs		= [ resource for resource in resourcs ]
	list_buds 		= [ budget for budget in budgets ]
	list_years_bud 	= []
	list_years_rsc 	= []
	bud_links 		= []
	rsc_links		= []
	for budget in list_buds:
		list_years_bud.append(budget['annee'])

	for resource in list_resrcs:
		list_years_rsc.append(resource['year'])

	list_years_bud = reversed(sorted(list(set(list_years_bud))))
	list_years_rsc = reversed(sorted(list(set(list_years_rsc))))

	for year in list_years_bud:
		bud_links.append({'year' : year , 'btype' : list(set([budget['type'] for budget in list_buds if
budget['annee'] == year])) })

	for year in list_years_rsc:
		rsc_links.append({'year' : year ,'btype' : list(set([resource['type'] for resource in list_resrcs if
resource['year'] == year]))})

	return render_template('index.html',
		page = g.db.find_one('pages', {'nom':'home'}),
		bud_links = bud_links,
		rsc_links = rsc_links

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

def resources_raw_view(year , resource_type , lang):
	try:
		anee = int(year)
	except ValueError:
		return "bad year"

	if lang not in ["fr" , "ar"]:
		return "bad lang"

	resourcex = {}
	resourcex['label'] 		= str(year)
	resourcex['children'] 	= []
	resourcex['amount']		= 0

	resources = g.db.find_one('resources' , {'year' : str(anee) , 'type' : resource_type}) or abort(404)
	for past_titre in resources['data'].values():
		for resource in past_titre['children']:
			titre = {}
			titre['amount'] = resource['total']
			titre['label']  = resource['name'][lang]
			titre['children'] = []
			if resource['children'].__len__() > 1:
				for child in resource['children']:
					partie = {}
					partie['label'] = child['name'][lang]
					partie['amount'] = child['total']
					partie['children'] = []
					if child['children'].__len__() > 1:
						for child_2 in child['children']:
							sect = {}
							sect['label'] = child_2['name'][lang]
							sect['amount']= child_2['total']
							sect['children'] = []
							if child_2['children'].__len__() > 1:
								for child_3 in child_2['children']:
									sect_2 = {}
									sect_2['label'] = child_3['name'][lang]
									sect_2['amount']= child_3['total']
									sect_2['children']= []
									if child_3['children'].__len__() > 1:
										for child_4 in child_3['children']:
											sect_3 = {}
											sect_3['label'] = child_4['name'][lang]
											sect_3['amount']= child_4['total']
											sect_3['children'] = []
											sect_2['children'].append(sect_3)
									sect['children'].append(sect_2)
							partie['children'].append(sect)
					titre['children'].append(partie)
			resourcex['children'].append(titre)
	for child in resourcex['children']:
		resourcex['amount'] += child['amount']

	return jsonify(resourcex)

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

#faq fonction
def faq():
	faqs = g.db.find('faq',sort=[('num_question',1)])
	return render_template('faq.html', faqs = faqs)

#def widgets_visual_editor():
#	return render_template('visual_editor.html')


# map functions
def govs(lang):
	govs = g.db.find('gov',)
	gov_list = []
	for gov in govs:
		gov_list.append(gov["nom"][lang])
	return jsonify( { 'govs' : gov_list } )

def ministeres(lang):
	minis = g.db.find('ministeres',)
	minis_list = []
	for mini in minis:
		minis_list.append(mini["nom"][lang])
	return jsonify( { 'ministeres' : minis_list} )

def secteurs(lang):
	sect = g.db.find('secteurs',)
	secteurs_list = []
	for secteur in sect:
		secteurs_list.append(secteur["nom"][lang])
	return jsonify( { 'secteurs' : secteurs_list} )

def projects():
	projects = g.db.find('projects',)
	projets  = []
	for project in projects:
		project["_id"] = ''
		projets.append(project)
	return jsonify(  { 'projects' : [ project for project in projets ] } )

def map_view():
	return render_template("map.html")


#******blog section******
#page d'acueill de blog (/blog)
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
#	return "page des blog is under construction"

#page /article
def article(article_id):
	post = g.db.find_one('article',{'_id':article_id}) or abort(404)
	try:
		vue = int(post['vue'])
	except:
		vue = int(0)
	vue= vue+1
#       return str("'_id':'ObjectId('"+article_id+"')'")
	g.db.update_article('article',{'_id':article_id},{'$set':{'vue':vue}})
	image_article = g.db.find_one('files',{'_id':post['image'].id})
        return render_template('article.html', post = post, image_article = image_article)
#	return "page article is under construction"

#fonction general pour la pagination
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

def search():
	text = request.args.get("q")
	if text == None:
		return redirect(url_for("root.home"))
	chars = '"()[]{}:;,'
	for char in chars:
		text = text.replace(char , "")
	if text.__len__() < 3 or text.__len__() > 100:
		return redirect(url_for("root.home"))
	results = {
	'pages' 	 : [],
	'ministeres' 	 : [],
	'wiki' 		 : [],
	'articles'	 : [],
	}
	if g.lang_code == "fr":
		text_p = text.replace(u"é","&eacute;")
		text_p = text_p.replace(u"à" , "&aacute;")
		text_p = text_p.replace(u"í" , "&iacute;")
		text_p = text_p.replace(u"â" , "&acirc;")
		text_p = text_p.replace(u"ê" , "&ecirc;")
		text_p = text_p.replace(u"è" , "&egrave;")
		text_p = text_p.replace(u"à" , "&agrave;")
		text_p = text_p.replace("'" , "&rsquo;")
	else:
		text_p = text
	query = compile(r'%s' % text , IGNORECASE)
	query_p = compile(r'%s' % text_p , IGNORECASE)
	pages = g.db.find("pages" , { "$or" : [{"texte.%s" %g.lang_code : query_p} , {"titre.%s" % g.lang_code : query_p}]})
	ministeres = g.db.find("ministeres" , {"nom.%s" % g.lang_code : query})
	wiki = g.db.find("wiki" , {"texte" : query_p})
	articles = g.db.find("article", {"$or" : [{"titre.%s"%g.lang_code: query_p },{"contenu.%s" % g.lang_code : query_p}]})
	results['pages'] = pages
	results['ministeres'] = ministeres
	results['wiki'] = wiki
	results['articles'] = articles
	return render_template("search.html",results=results,keyword=text)
