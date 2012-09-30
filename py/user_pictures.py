__author__ = 'vlad.lego@webocrat.com (Vlad Lego)'

from globals import *
import webapp2

class UserImage (webocrat_Request):
    def get(self,img_id):
        img_id = img_id.replace(".png","")
        memcacheKey = "img"+str(img_id)
        data = memcache.get(memcacheKey)
        if data:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(data)
            return

        try:
            theImageFile = ImageFile.get_by_id(int(img_id))
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(theImageFile.data)
            memcache.set(memcacheKey,theImageFile.data)
            return
        except Exception:
            self.error(404)
            self.response.out.write()
            return


import base64
import re
from google.appengine.api import images

class ImageUpload(webocrat_Request):

    dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')

    def post(self):
        #extract post info
        post_img = self.request.get('img')

        imgb64 = self.dataUrlPattern.match(post_img).group(2)
        if imgb64 is not None and len(imgb64) > 0:
            theImageFile = ImageFile()
            theImageFile.data = db.Blob(base64.b64decode(imgb64))

            img = images.Image(theImageFile.data)
            theImageFile.width = img.width
            theImageFile.height = img.height
            theImageFile.format = img.format
            theImageFile.put()

            self.response.out.write('{ "id": "%d"}' % int(theImageFile.key().id()))
        else:
            self.response.out.write('{ "error": "0"}')


app = webapp2.WSGIApplication([
    ('/img/(.*)', UserImage),
    ('/image.upload', ImageUpload)
])
