from flask_uploads import UploadSet, IMAGES, ALL

uploaded_images = UploadSet('images', IMAGES)
uploaded_documents = UploadSet('documents', ALL)