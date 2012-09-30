#!/usr/bin/env python

from google.appengine.ext import db
from geo.geomodel import GeoModel

# data models - USERS

"""
    Use cases:
    1. Activist online
    2. Problem solver
       Designer
       Copyrighter
    3. Founding member
    4. Jurnalist, Leader, Om politic
    5. Partid Politic, ONG, Asociatie
    6. Primarie, Consiliu Local

- - - - - - - - - - - - - - -


"""






class BaseEntity(GeoModel):
    #location - inherited from GeoModel
    name = db.StringProperty()                  # display name
    photo = db.ReferenceProperty()              # key for photo
    url = db.StringProperty()                   # custom url hug-fu.com/vlad.lego

class Ego(BaseEntity):
    #location, name, photo, url
    birthday = db.DateTimeProperty(auto_now_add=True)
    trust_level = db.IntegerProperty(default=0)  # trust level

    #trustors  - people that trust this ego
    #trustees  - people that this ego trusts
    #hostiles - people that blacklisted this ego




class HC_Dog(Ego):
    #location, name, photo, url
    uploader = db.ReferenceProperty(Ego, collection_name="dogs")
    place = db.StringProperty()


class WebocratUser(db.Model):
    # invitations_out
    # groups
    # photo_ratings

    ego = db.ReferenceProperty(Ego, required=True, collection_name="users")
    current_ego = db.ReferenceProperty(Ego, collection_name="active_users")

    uniqueID = db.StringProperty()              # url / identity provider
    provider = db.StringProperty()              # identity provider
    email = db.EmailProperty()
    email_is_verified = db.BooleanProperty(default=False)

    token = db.StringProperty(default=None)


class Trust(db.Model):
    #trustor = owner = PARENT entity
    #trustee = target
    #owner = db.ReferenceProperty(Ego, required=True, collection_name="trustees")   #giver of trust
    target = db.ReferenceProperty(Ego, required=True, collection_name="trustors")   #receiver of trust
    when = db.DateTimeProperty(auto_now_add=True)

class BlackBall(db.Model):
    #parent = Ego
    #owner = db.ReferenceProperty(Ego, required=True, collection_name="blacklist")   #
    target = db.ReferenceProperty(Ego, required=True, collection_name="hostiles")   #
    when = db.DateTimeProperty(auto_now_add=True)





class Hub(BaseEntity):
    #location, name, photo, url
    members = db.ListProperty(db.Key)
    ego = db.ReferenceProperty(Ego, required=True, collection_name="hubs")
    description = db.StringProperty()           # goal description

    creationDate = db.DateTimeProperty(auto_now_add=True)
    active = db.BooleanProperty(default=True)   #group is active True/False
    published = db.BooleanProperty(default=True)

    invitationOnly = db.BooleanProperty()       #if True can't become a member without an invitation

    type = db.StringProperty(choices=("community", "association","organisation", "federation"))



class Badge(db.Model):
    # parent : Ego | Channel
    # owner = db.ReferenceProperty(Ego, collection_name="badges")   #
    award_function = db.StringProperty()
    award_parameters = db.StringProperty()
    icon = db.ReferenceProperty() # image file
    name = db.StringProperty()
    type = db.StringProperty(choices=("access","award","function"))

#TODO : move egobadge to Ego as ListProperty
class EgoBadge(db.Model):
    """
    This object records the relationship between an Ego and a Badge
    When a new EgoBadge is created, the trust_level for that badge is evaluated.
        For each user that owns this badge 
    """
    #parent = owner
    badge = db.ReferenceProperty(Badge, required = True)
    trust_level = db.IntegerProperty(default=0)


class Group(db.Model):
    # parent - ego
    # owner = db.ReferenceProperty(Ego, collection_name="a")
    ego = db.ReferenceProperty(Ego, required=True, collection_name="groups")

    area = db.StringProperty(choices=("global","local"))


    # members
    # invitations_to

#invitations with high share power are pointing to users that share well
class Invitation(db.Model):
    invitation_code = db.StringProperty()
    sender = db.ReferenceProperty(WebocratUser, required=True, collection_name="invitations_out")
    group = db.ReferenceProperty(Group, required=True, collection_name="invitations_to")
    sharePower = db.IntegerProperty(default=0)  #increment at join group confirmation

    @property
    def get_invitation_with_code(invitation_code=False):
        inv = False
        if invitation_code:
            inv = Invitation.gql("WHERE invitation_code = :1 LIMIT 1", invitation_code).get()
        return inv



class Channel(db.Model):
    #parent => owner
    #owner = db.ReferenceProperty(Ego, required=False, collection_name="channels")
    name = db.StringProperty()

class Message(db.Model):
    #parent => channel
    content = db.TextProperty()
    creationDate = db.DateTimeProperty(auto_now_add=True)
    writer = db.ReferenceProperty(Ego, collection_name="messages")





class ImageFile(db.Model):
    width = db.IntegerProperty()
    height = db.IntegerProperty()
    format = db.IntegerProperty()
    data = db.BlobProperty()

    owner = db.ReferenceProperty(Ego, collection_name = "image_files")
    private = db.BooleanProperty(default=True)      #public photos can be used by anyone
    approved = db.BooleanProperty(default=False)



class PhotoRating(db.Model):
    user = db.ReferenceProperty(WebocratUser, required=True, collection_name="photo_ratings")
    photo = db.ReferenceProperty(ImageFile, required=True, collection_name="ratings")
    positive = db.BooleanProperty(default=False)    #photos with total negative feedback more than 10 will be removed, users karma down
    date = db.DateTimeProperty(auto_now=True)





#class Tag(db.Model):
#    name = db.StringProperty()

#class Cluster(db.Model):
#  name = db.StringProperty()
#  location = db.GeoPtProperty()
#  active = db.BooleanProperty()
  
#class Message(db.Model):
#  subject = db.StringProperty()
#  body = db.StringProperty()
#  cluster = db.KeyProperty()
#  user = db.KeyProperty()

#class Heart(db.Model):
#    owner = db.ReferenceProperty(HugUser)

#class UserLinks(db.Model):
#  object = db.KeyProperty() #can be a message or a cluster
#  userID = db.KeyProperty()



