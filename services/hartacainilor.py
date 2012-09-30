# + webocrat custom map service
#
#

from protorpc import messages
from protorpc import message_types
from protorpc import remote

import logging
import datamodels

from globals import *

#
# use this to create a new collective map object
#

class new_map_Request(messages.Message):
    name = messages.StringField(1, required=True)
    photo_id = messages.StringField(2)
    icon_id = messages.StringField(3)
    access_token = messages.StringField(4, required=True)

class new_map_Response(messages.Message):
    id = messages.StringField(1, required=True)



#
# interaction with the map
#
#  add object
#  get object
#  delete object
#  request objects in rectangle
#



class update_map_object_Request(messages.Message):
    class Action(messages.Enum):
        NEW = 1
        CONFIRMED = 2
        SPAM = 3       # only by owner
    action = messages.EnumField(Action,1, required=True)

class update_map_object_Response(messages.Message):
    response = messages.StringField(1,required=True)


#


# browse objects

class mo_Request(messages.Message):
    id = messages.StringField(1, required=True)
    access_token = messages.StringField(2, required=True)

class mo_Response(messages.Message):
    name = messages.StringField(1, required=True)
    location = messages.StringField(2, required=True)
    photo_id = messages.IntegerField(3)
    class State(messages.Enum):
        NEW = 1
        APPROVED = 2
        CLOSED = 3
    state = messages.EnumField(State, 6)
    dog_id = messages.IntegerField(7)




class get_map_region_Request(messages.Message):
    #access_token
    limit = messages.IntegerField(1, default=30)
    rectangle = messages.StringField(2, required=True)
#    class Order(messages.Enum):
#        SIZE = 1
#         = 2
#    order = messages.EnumField(Order, 4, default=Order.WHEN)

class get_map_region_Response(messages.Message):
    objects = messages.MessageField(mo_Response, 1, repeated=True)




#done
class add_map_object_Request(messages.Message):
    photo_id = messages.StringField(1, required=True)
    latitude = messages.FloatField(2, required=True)
    longitude = messages.FloatField(3, required=True)

    name = messages.StringField(4)
    place = messages.StringField(5)
    location = messages.StringField(6)
    token = messages.StringField(7, required=True)
#done
class add_map_object_Response(messages.Message):
    id = messages.IntegerField(1, required=True)
    code = messages.IntegerField(2, required=True)









# Create the RPC service to exchange messages
class HartaCainilorService(remote.Service):

#    def __init__(self, configuration, state):
#        self.configuration = configuration
#        self.state = state

#    @need_registered_user
    @remote.method(add_map_object_Request, add_map_object_Response)
    def adddog(self, request):
        logging.info("%s " % request.photo_id)
        logging.info("%s " % request.location)
        logging.info("%s " % request.name)
        logging.info("%s " % request.place)
        logging.info("%s " % request.token)

        theUserQuery = WebocratUser.gql("WHERE token = :1 LIMIT 1", request.token)
        user = theUserQuery.get()

        response = add_map_object_Response()

#        if not user:
#            response.id = -99   #adica nu avem user
#            response.code = 300
#            return response
#        else:
        dog = datamodels.HC_Dog()
        if user:
            dog.uploader = user.ego
        dog.name = request.name
        dog.location = request.location
        #TODO: process place
        dog.place = request.place
        dog.photo = ImageFile.get_by_id(int(request.photo_id))
        dog.put()

        response.id = dog.key().id()
        response.code = 1
        return response

    @remote.method(mo_Request, mo_Response)
    def dog(self, request):
        return mo_Response()


    @remote.method(get_map_region_Request, get_map_region_Response)
    def get(self, request):
        query = datamodels.HC_Dog.all()

        dogs = []
        for dog in query.fetch(request.limit):
            theDog = mo_Response()
            theDog.location = str(dog.location)
            theDog.name = dog.name
            theDog.photo_id = dog.photo.key().id()
            theDog.dog_id = dog.key().id()

            dogs.append(theDog)

        return get_map_region_Response(objects=dogs)

#    @remote.method(TestRequest, TestResponse)
#    def test(self, request):
#        response = TestResponse(reply="yes")
#        return response


#TODO: service factory
#configuration = MyServiceConfiguration()
#global_state = MyServiceState()
#
#HartaCainilorService_factory = HartaCainilorService.new_factory(configuration,
#                                                                state=global_state)