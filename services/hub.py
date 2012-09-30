__author__ = 'vlad.lego@webocrat.com (Vlad Lego)'

from protorpc import remote, messages
import datamodels

# + HUB
class new_hub_request(messages.Message):
    name = messages.StringField(1, required=True)   #eg.
    location = messages.StringField(2, required=True)
    domain = messages.StringField(3, default="hug-fu.com") #eg.  iself.com
class new_hub_response(messages.Message):
    id = messages.StringField(1, required=True)
    error = messages.StringField(2)


class edit_hub_request(messages.Message):
    type = messages.StringField(1)          # organisation, squad
    description = messages.StringField(2)
    join_rule = messages.IntegerField(3)    # trust level, open, etc.
    picture_id = messages.StringField(4)    #


class hub_request(messages.Message):
    id = messages.StringField(1, required=True)
class hub_response(messages.Message):
    name = messages.StringField(1, required=True)   #eg.
    domain = messages.StringField(2, required=True) #eg.  iself.com
    location = messages.StringField(3, required=True)
    members = messages.IntegerField(4, required=True)


class hubs_request(messages.Message):
    #access_token
    limit = messages.IntegerField(1, default=30)
    rectangle = messages.StringField(2, required=True)
    only_joined = messages.BooleanField(3, default=False)
#    class Order(messages.Enum):
#        SIZE = 1
#         = 2
#    order = messages.EnumField(Order, 4, default=Order.WHEN)
class hubs_response(messages.Message):
    hubs = messages.MessageField(hub_response, 1, repeated=True)


# Create the RPC service to exchange messages
class hub_service(remote.Service):

    # /h-new
    @remote.method(new_hub_request, new_hub_response)
    def new(self, request):
        newHub = datamodels.Hub()
        newHub.name = request.name
        newHub.location = request.location
        newHub.put()

        response = new_hub_response(id = unicode(newHub.key().id()))
        return response
