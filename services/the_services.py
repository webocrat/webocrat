__author__ = 'vlad.lego@webocrat.com (Vlad Lego)'
package = 'webocrat'

from protorpc.wsgi import service

#import hub
import hartacainilor
#import wmap_object
#import comment
#import ego



HartaCainilor = service.service_mapping(hartacainilor.HartaCainilorService, '/hc')
#hubService = service.service_mapping(hub.hub_service, '/h-')
#ego = service.service_mapping(ego.ego_service, '/e-')
#comment = service.service_mapping(comment.comment_service, '/comment')

#wmapServices = service.service_mappings(
#    [
#        ('/map', wmap.wMapObjectService),
#        ('/m-', wmap.wMapObjectService)
#    ])