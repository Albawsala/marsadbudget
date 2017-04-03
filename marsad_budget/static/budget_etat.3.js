var budget_etat = {
	'recettes': [
		{
			'titre': 'Recettes',
			'montant': 28025000000,
			'children': [
				{
					'titre': 'Recettes ordinaires',
					'montant': 19020200000,
					'children': [
						{
							'titre': 'Recettes fiscales',
							'montant': 17081700000,
							'children': [
								{'titre': 'Impot direct', 'montant': 7743000000},
								{'titre': 'Impot et taxes indirect', 'montant': 9338700000},
							]
						},
						{
							'titre': 'Recettes non fiscales',
							'montant': 1938500000,
							'children': [
								{'titre': 'Revenus financiers ordinaires','montant':746500000},
								{'titre': 'Revenus du domaine de l\'Etat','montant':1192000000},
							]
						}
					]
				},
				{
					'titre': 'Recettes non ordinaires + ressources d\'emprunt',
					'montant': 8052000000,
					'children': [
						{
							'titre': 'Ressources d\'emprunts',
							'montant': 7738000000,
							'children': [
								{'titre': 'Ressources d\'Emprunts Extérieurs', 'montant':4711565000},
								{'titre': 'Ressources d\'Emprunts Intérieurs', 'montant':2500000000},
								{'titre': 'Ressources d\'Emprunts Extérieurs Affectés', 'montant':526435000},
							]
						},
						{
							'titre': 'Recettes Non Ordinaires',
							'montant': 314000000,
							'children': [
								{'titre': 'Recouvrement du principal des emprunts', 'montant':100000000},
								{'titre': 'Autres Recettes Non Ordinaires', 'montant':214000000},
							]
						},
					]
				},
				{
					'titre': 'Fonds spéciaux du Trésor',
					'montant': 952800000,
				}
			]
		},
	],
	'depenses': [
		{
			'titre': {'fr': 'Dépenses', 'ar':'النفقات'},
			'montant': 28025000000,
			'children': [
				{
					'titre': {'fr': 'Ministères', 'ar':'الوزارات'},
					'montant': 22378427000,
					'children': [
						{'titre':{'fr':'Ministère de l\'Éducation', 'ar':'وزارة التربية'}, 'montant':3658713000, 'icon':'/static/images/ministere_education_white.png'},
						{'titre':{'fr':'Ministère de l\'Industrie', 'ar':'وزارة الصناعة'}, 'montant':3000289000, 'icon':'/static/images/ministere_industrie_white.png'},
						{'titre':{'fr':'Ministère de l\'Intérieur', 'ar':'وزارة الداخلية'}, 'montant':2279824000, 'icon':'/static/images/ministere_interieur_white.png'},
						{'titre':{'fr':'Ministère de la Défense', 'ar':'وزارة الدفاع'}, 'montant':1538879000, 'icon':'/static/images/ministere_defense_white.png'},
						{'titre':{'fr':'Ministère de la Santé', 'ar':'وزارة الصحة'}, 'montant':1512170000},
						{'titre':{'fr':'Ministère de l\'Enseignement Supérieur et recherche scientifique', 'ar':''}, 'montant':1405280000},
						{'titre':{'fr':'Ministère des Technologies de l\'Information et de la Communication', 'ar':''}, 'montant':123558000},
						{'titre':{'fr':'Ministère du Commerce et de l\'Artisanat', 'ar':''}, 'montant':1501845000},
						{'titre':{'fr':'Ministère des Finances', 'ar':''}, 'montant':934021000},
						{'titre':{'fr':'Ministère de l\'Investissement et de la Coopération Internationale', 'ar':''}, 'montant':474338000},
						{'titre':{'fr':'Ministère de l\'Equipement et de l\'Environnement', 'ar':''}, 'montant':1298041000},
						{'titre':{'fr':'Ministère de l\'Agriculture', 'ar':''}, 'montant':1041456000},
						{'titre':{'fr':'Ministère des Affaires Sociales', 'ar':''}, 'montant':782656000},
						{'titre':{'fr':'Ministère de l\'Emploi et de la Formation professionnelle', 'ar':''}, 'montant':670365000},
						{'titre':{'fr':'Ministère du Transport', 'ar':''}, 'montant':583466000},
						{'titre':{'fr':'Ministère des Affaires de la femme et de la famille', 'ar':''}, 'montant':86059000},
						{'titre':{'fr':'Ministère de la Jeunesse et des Sports', 'ar':''}, 'montant':457025000},
						{'titre':{'fr':'Ministère de la Justice', 'ar':''}, 'montant':396904000},
						{'titre':{'fr':'Ministère et des droits de l\'Homme et de la Justice Transitionnelle', 'ar':''}, 'montant':5917000},
						{'titre':{'fr':'Ministère des Affaires étrangères', 'ar':''}, 'montant':190453000},
						{'titre':{'fr':'Ministère de la Culture', 'ar':''}, 'montant':177809000},
						{'titre':{'fr':'Ministère du Tourisme', 'ar':''}, 'montant':117461000},
						{'titre':{'fr':'Ministère des Affaires religieuses', 'ar':''}, 'montant':88259000},
						{'titre':{'fr':'Ministère des Domaines de l\'État et des Affaires Foncières', 'ar':''}, 'montant':53639000},
					]
				},
				{'titre': {'fr':'Dette publique', 'ar':'دين عمومي'}, 'montant': 4675000000, 'icon': '/static/images/icon_dette.png'},
				{'titre': {'fr':'Dépenses imprévues', 'ar':'نفقات إستثنائية'}, 'montant': 712428000},
				{'titre': {'fr':'ANC + Gouvernement + Présidence de la république', 'ar':'المجلس التأسيسي + رئاسة الحكومة + رئاسة الجمهورية'}, 'montant': 259145000},
			]
		}
	]
}

/*
var depenses_etat_variations = {
	'depenses': {
		'titre': 'Dépenses',
		'montant': 28025000000,
		'montant_1': 19058000000,
		'max_children': 5,
		'children': [
			{
				'children': [
					{'titre':'Éducation', 'montant':3658713000, 'icon':'/static/images/ministere_education_white.png', 'color':'#b8ccbc'},
					{'titre':'Industrie', 'montant':3000289000, 'montant_1':500289000, 'icon':'/static/images/ministere_industrie_white.png', 'color':'#80c0ce'},
					{'titre':'Intérieur', 'montant':2279824000, 'icon':'/static/images/ministere_interieur_white.png', 'color':'#d3d2a0'},
					{'titre':'Défense', 'montant':1538879000, 'icon':'/static/images/ministere_defense_white.png', 'color':'#d1dee1'},
					{'titre':'Enseignement Supérieur et recherche scientifique', 'montant':1405280000},
					{'titre':'Ministère des Technologies de l\'Information et de la Communication', 'montant':123558000},
					{'titre':'Ministère de la Santé', 'montant':1512170000},
					{'titre':'Ministère du Commerce et de l\'Artisanat', 'montant':1501845000},
					{'titre':'Ministère des Finances', 'montant':934021000},
					{'titre':'Ministère de l\'Investissement et de la Coopération Internationale', 'montant':474338000},
					{'titre':'Ministère de l\'Equipement et de l\'Environnement', 'montant':1298041000},
					{'titre':'Ministère de l\'Agriculture', 'montant':1041456000},
					{'titre':'Ministère des Affaires Sociales', 'montant':782656000},
					{'titre':'Ministère de l\'Emploi et de la Formation professionnelle', 'montant':670365000},
					{'titre':'Ministère du Transport', 'montant':583466000},
					{'titre':'Ministère des Affaires de la femme et de la famille', 'montant':86059000},
					{'titre':'Ministère de la Jeunesse et des Sports', 'montant':457025000},
					{'titre':'Ministère de la Justice', 'montant':396904000},
					{'titre':'Ministère et des droits de l\'Homme et de la Justice Transitionnelle', 'montant':5917000},
					{'titre':'Ministère des Affaires étrangères', 'montant':190453000},
					{'titre':'Ministère de la Culture', 'montant':177809000},
					{'titre':'Ministère du Tourisme', 'montant':117461000},
					{'titre':'Ministère des Affaires religieuses', 'montant':88259000},
					{'titre':'Ministère des Domaines de l\'État et des Affaires Foncières', 'montant':53639000},
				]
			},
			{'titre': 'Dette publique', 'montant': 4675000000, 'icon': '/static/images/icon_dette.png', 'color':'#faa'},
			{'titre': 'Dépenses imprévues', 'montant': 712428000},
			{'titre': 'ANC + Gouvernement + Présidence de la république', 'montant': 259145000},
		]
	},

	'sans_compensation': {
		'titre': 'Dépenses',
		'montant': 19058000000,
		'max_children': 6,
		'children': [
			{
				'children': [
					{'titre':'Éducation', 'montant':3658713000, 'icon':'/static/images/ministere_education_white.png', 'color':'#b8ccbc'},
					{'titre':'Industrie', 'montant':500289000, 'icon':'/static/images/ministere_industrie_white.png', 'color':'#80c0ce'},
					{'titre':'Intérieur', 'montant':2279824000, 'icon':'/static/images/ministere_interieur_white.png', 'color':'#d3d2a0'},
					{'titre':'Défense', 'montant':1538879000, 'icon':'/static/images/ministere_defense_white.png', 'color':'#d1dee1'},
					{'titre':'Enseignement Supérieur et recherche scientifique', 'icon': '/static/images/ministere_enseignement_superieur_white.png', 'montant':1405280000},
					{'titre':'Ministère des Technologies de l\'Information et de la Communication', 'montant':123558000},
					{'titre':'Ministère de la Santé', 'montant':1512170000},
					{'titre':'Commerce et Artisanat', 'montant':94845000},
					{'titre':'Ministère des Finances', 'montant':934021000},
					{'titre':'Ministère de l\'Investissement et de la Coopération Internationale', 'montant':474338000},
					{'titre':'Ministère de l\'Equipement et de l\'Environnement', 'montant':1298041000},
					{'titre':'Ministère de l\'Agriculture', 'montant':1041456000},
					{'titre':'Ministère des Affaires Sociales', 'montant':782656000},
					{'titre':'Ministère de l\'Emploi et de la Formation professionnelle', 'montant':670365000},
					{'titre':'Ministère du Transport', 'montant':198466000},
					{'titre':'Ministère des Affaires de la femme et de la famille', 'montant':86059000},
					{'titre':'Ministère de la Jeunesse et des Sports', 'montant':457025000},
					{'titre':'Ministère de la Justice', 'montant':396904000},
					{'titre':'Ministère et des droits de l\'Homme et de la Justice Transitionnelle', 'montant':5917000},
					{'titre':'Ministère des Affaires étrangères', 'montant':190453000},
					{'titre':'Ministère de la Culture', 'montant':177809000},
					{'titre':'Ministère du Tourisme', 'montant':117461000},
					{'titre':'Ministère des Affaires religieuses', 'montant':88259000},
					{'titre':'Ministère des Domaines de l\'État et des Affaires Foncières', 'montant':53639000},
				]
			},
			//{'titre': 'Dette publique', 'montant': 4675000000, 'icon': '/static/images/icon_dette.png', 'color':'#faa'},
			//{'titre': 'Compensation', 'montant': 4292000000},
			{'titre': 'Dépenses imprévues', 'montant': 712428000},
			{'titre': 'ANC + Gouvernement + Présidence de la république', 'montant': 259145000},
		]
	}
}
*/

var depenses_etat = {
	'montant': 28025000000,
	'montant_1': 19058000000,
	'children': [
		{
			'titre':{'fr':'Autres ministères', 'ar':'وزارات أخرى'},
			'icon':'/static/images/icon_autres.png',
			'montant':9858280000, 'montant_1':9473280000,
		},
		{
			'titre':{'fr':'Dette publique', 'ar':'دين عمومي'},
			'montant': 4675000000, 'montant_1':0,
			'icon': '/static/images/icon_dette.png',
			'color':'#faa',
			'id':'dette_publique',
			'type':'focus',
		},
		{
			'titre':{'fr':'Éducation', 'ar':'وزارة التربية'},
			'montant':3658713000,
			'icon':'/static/images/ministere_education_white.png',
			'color':'#b8ccbc',
			'id':'education',
		},
		{
			'titre':{'fr':'Industrie', 'ar':'وزارة الصناعة'},
			'montant':3000289000, 'montant_1':500289000,
			'icon':'/static/images/ministere_industrie_white.png',
			'color':'#80c0ce',
			'id':'industrie'
		},
		{
			'titre':{'fr':'Intérieur', 'ar':'وزارة الداخلية'},
			'montant':2279824000,
			'icon':'/static/images/ministere_interieur_white.png',
			'color':'#C6C5B7',
			'id':'interieur',
		},
		{
			'titre':{'fr':'Défense', 'ar':'وزارة الدفاع'},
			'montant':1538879000,
			'icon':'/static/images/ministere_defense_white.png',
			'color':'#d1dee1',
			'id':'defense'
		},
		{
			'titre':{'fr':'Santé publique', 'ar':'وزارة الصحة'},
			'montant':1512170000,
			'icon':'/static/images/ministere_sante_white.png',
			'color':'#FFA9C7',
			'id':'sante'
		},
		{
			'titre':{'fr':'Commerce et Artisanat', 'ar':'وزارة التجارة و الصناعات التقليدية'},
			'montant':1501845000, 'montant_1':94845000,
			'icon':'/static/images/ministere_commerce_white.png',
			'color':'#C8EEB1',
			'id':'commerce_artisanat'
		},
		//{'titre':{'fr':'Autres<br>(20 ministères)', 'icon':'/static/images/icon_autres.png', 'montant': 11900722000, 'montant_1':10108722000},
		//{'titre':{'fr':'Dépenses imprévues', 'montant': 712428000},
		//{'titre':{'fr':'ANC + Gouvernement + Présidence de la république', 'montant': 259145000},
	],
	'satellites': [
		{
			'titre':{'fr':'Compensation', 'ar':'الدعم'},
			'montant':0, 'montant_1':4292000000,
			'cx':420, 'cy':70,
			'color': '#E2CB91',
			'icon': '/static/images/icon_compensation.png',
			'type':'focus',
			'id':'compensation'
		},
		{
			'titre':{'fr':'Dette publique', 'ar':'دين عمومي'},
			'montant':0, 'montant_1':4675000000,
			'icon': '/static/images/icon_dette.png',
			'color':'#faa',
			'cx': 80, 'cy':70,
			'type':'focus',
			'id':'dette_publique'
		},
	]
}