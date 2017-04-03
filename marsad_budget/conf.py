# -*- coding: utf-8 -*-

DEBUG = True

BASE_URL = 'http://budget.marsad.tn'

DB_HOST = 'localhost'
DB_PORT = 24107
DB_NAME = 'marsad_executif'

ADMINS = ['nblxxx@gmail.com']
LANGS = {
	'ar': 'ar_TN',
	'fr': 'fr_FR',	
}

PAGE_MAX = 10
FILES_PAGE_MAX = 8

SECRET_KEY = '\x93\xa8\xfdJ\xa8\xf4tk\xc6\x883\x87\xa3\xab3\xe8Z\x0eO9\x0br\xfa\xdb'

MAX_CONTENT_LENGTH = 1024 * 1024 * 20

UPLOAD_FOLDER = '/home/user0/www/uploads/marsad_budget'

UPLOADED_DOCUMENTS_ALLOW = 'pdf'
UPLOADED_DOCUMENTS_DEST = '/home/user0/www/uploads/marsad_budget/documents'
UPLOADED_DOCUMENTS_URL = '/uploads/documents/'

UPLOADED_IMAGES_DEST = '/home/user0/www/uploads/marsad_budget/images'
UPLOADED_IMAGES_URL = '/uploads/images/'

UPLOADED_THUMBNAILS_DEST = '/home/user0/www/uploads/marsad_budget/thumbnails'
UPLOADED_THUMBNAILS_URL = '/uploads/thumbnails/'

FB_PAGE_URL = 'https://www.facebook.com/AlBawsala'
TWITTER_URL = 'https://twitter.com/AlBawsalaTN'