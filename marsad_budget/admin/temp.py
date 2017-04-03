# -*- coding: utf-8 -*-

from base import *



def save_uploads():
	DIRPATH = '/home/user0/www/uploads/marsad_budget/documents'
	for filename in os.listdir(DIRPATH):
		filepath = '%s/%s' % (DIRPATH, filename)
		filesize = os.path.getsize(filepath)
		db_budget['files'].insert({
			'type': 'DOC',
			'lang': 'fr',
			'filename': filename,
			'filesize': filesize,
			'title': filename.rsplit('.',1)[0]
		})



def budget_to_collection():
	db_budget['budgets'].remove()
	for ministere in db_budget['ministeres'].find():
		if not ministere.get('budget'):
			continue
		budgets = sorted([(k,v) for k,v in ministere['budget'].items()], key=lambda (k,v):k)
		for k,v in budgets:
			del v['type']
			del v['year']
			dbref = DBRef('ministeres', ministere['_id'])
			db_budget['budgets'].save({
				'ministere': dbref,
				'annee': int(k[:4]),
				'type': k[5:],
				'budget': v,
				'_meta': {
					'draft': False,
					'mtime': datetime.now(),
					'raw': {'budget': yaml.safe_dump(v, default_flow_style=False, allow_unicode=True)}
				}
			})



def gbo_to_collection():
	for ministere in db_budget['ministeres'].find():
		if not ministere.get('programmes'):
			continue
		if 'children' not in ministere['programmes'] or 'total' not in ministere['programmes']:
			print "%s : programmes invalid" % ministere['abbr']
			continue
		budget = db_budget['budgets'].find_one({'annee': 2014, 'type':'LF', 'ministere.$id': ministere['_id']})
		if not budget:
			print "%s : budget not found" % ministere['abbr']
			continue
		budget['budget']['children_gbo'] = ministere['programmes']['children']
		budget['budget']['total_gbo'] = ministere['programmes']['total']
		budget['_meta']['raw']['budget'] = yaml.safe_dump(budget['budget'], default_flow_style=False, allow_unicode=True)
		db_budget['budgets'].save(budget)



def budget_extract(year):
	db_budget['budgets'].remove({'annee': year})
	doc = ezodf.opendoc('%s/raw/budget 2016.ods' % FILEROOT)
	sheet = doc.sheets[u'budgets total LF16']
	for r in xrange(sheet.nrows()):
		row = sheet.row(r)
		if not row[0].value: continue
		print row[0].value
		
		total = row[4].value / 1000
		developpement = (row[10].value or 0) / 1000
		fonds_speciaux = (row[15].value or 0) / 1000000
		gestion = total - (developpement + fonds_speciaux)
		obj = {
			'annee': year,
			'type': 'LF',
			'budget': {
				'total': total,
				'evolution': row[6].value,
				'children': {
					'gestion': {'montant': gestion},
				},
			}
		}
		if row[0].value == 'dette_publique':
			obj['budget']['titre'] = {'fr': u'Dette publique', 'ar': u'دين عمومي'}
			obj['budget']['icon'] = 'icon_dette.png'
		elif row[0].value == 'depenses_imprevues':
			obj['budget']['titre'] = {'fr': u'Dépenses imprévues', 'ar': u'نفقات غير متوقعة'}

		if developpement:
			obj['budget']['children']['developpement'] = {'montant': developpement}
		if fonds_speciaux:
			obj['budget']['children']['fonds_speciaux'] = {'montant': fonds_speciaux}

		ministere = db_budget['ministeres'].find_one({'abbr':row[0].value})
		if ministere:
			obj['ministere'] = DBRef('ministeres', ministere['_id'])
			ministere['active'] = True
			db_budget['ministeres'].save(ministere)
		else:
			obj['budget']['id'] = row[0].value
		obj['_meta'] = {
			'draft': False,
			'mtime': datetime.now(),
			'raw': {'budget': yaml.safe_dump(obj['budget'], default_flow_style=False, allow_unicode=True)},
		}
		db_budget['budgets'].save(obj)



if __name__ == '__main__':
	# budget_to_collection()
	# gbo_to_collection()
	budget_extract(2016)