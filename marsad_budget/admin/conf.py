# -*- coding: utf-8 -*-

SITE_TITLE = 'budget.marsad.tn'

REMEMBER_COOKIE_NAME = 'remember_token_marsad_budget'

from marsad_budget.conf import *

from marsad_budget.admin.callbacks import CALLBACKS

WIDGETS = {
	'ministeres': [
		'http://maps.googleapis.com/maps/api/js?sensor=false&libraries=drawing',
		'/static/widgets/geoedit.js',
	],
}