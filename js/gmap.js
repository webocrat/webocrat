
//http://gmaps-samples-v3.googlecode.com/svn/trunk/styledmaps/wizard/index.html

var Map = {
    browserSupportFlag :  new Boolean(),
    map: false,
    geocoder : false,
    infowindow: new google.maps.InfoWindow(),
    theMarker: false,
    marker_image: false,
    options : {
        minZoom: 3,
        maxZoom: 20,
        zoom: 1,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        scrollwheel: false
    },
    Init: function (start_location, zoom) {
        Map.options.zoom = zoom;
        Map.map = new google.maps.Map(document.getElementById("map_canvas"), Map.options);
        Map.geocoder = new google.maps.Geocoder();
        Map.map.setCenter(start_location);
    },
//    Initialize: function (div_id) {
//        Map.map_div = div_id;
//        Map.map = new google.maps.Map(document.getElementById(Map.map_div), Map.options);
//        Map.geocoder = new google.maps.Geocoder();
//
////        marker_image = '/css/map/map_hub.png';
////        hubMarker = new google.maps.Marker({
////            position: default_location,
////            map: MapView.map,
////            icon: marker_image,
////            title: 'HQ',
////            draggable: true
////        });
//    },
    autolocate: function() {
        Map.setMapMessage("Detecting ...");

        // Try W3C Geolocation method (Preferred)
        if(navigator.geolocation) {
            browserSupportFlag = true;
            navigator.geolocation.getCurrentPosition(
                function(position) {
                    myLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
                    Map.setYourPosition(myLocation);
                    $("#autolocation-box").html("<h2>Location found.</h2>");
                    Map.clearMapMessage();
                },
                function() {
                    Map.geoNot(browserSupportFlag);
                }
            );
        } else {
            // Browser doesn't support Geolocation
            browserSupportFlag = false;
            Map.geoNot(browserSupportFlag);
        }
    },
    clearMapMessage: function() {
        $("#mmsg").animate({opacity:0},200,
          function() {
            $("#mmsg").detach();
          });
    },
    setMapMessage: function(msg) {
        $("#mmsg").detach();
        $('<div id="mmsg" class="map_message">'+msg+'</div>').insertBefore($(Map.map_div));
        var newMsg = $("#mmsg");
        var mb = 0 - (newMsg.innerHeight(true) + parseInt(newMsg.css('margin-top')));   //margin-bottom = 0-(margin-top + height)
        newMsg.css('margin-bottom',mb+"px");
    },
    geoNot: function(support) {
        if (support) {
            $("#autolocation-box").html("<p>To use the autolocation feature, you must allow the website to access your location. <u>Try again</u></p>");
        } else {
            $("#autolocation-box").html("<p>Your browser doesn't support autolocation.</p>");
        }
        Map.setMapMessage("Autolocation didn't work.<br />Use the search box.");
        setTimeout('Map.clearMapMessage()', 2000);
    },
    initAutocomplete : function (input_id) {
        var input = document.getElementById(input_id);
        Map.autocomplete = new google.maps.places.Autocomplete(input);
        Map.autocomplete.bindTo('bounds', Map.map);
        google.maps.event.addListener(Map.autocomplete, 'place_changed', Map.autocompletePlaceChanged);
    },
    autocompletePlaceChanged : function () {
        var place = Map.autocomplete.getPlace();
        Map.showPlace(place);
    },
    findAddress: function(address) {
        Map.geocoder.geocode( { 'address': address,
                                'latLng' : Map.map.getCenter(),
                                'region': 'RO'}, Map.addressFound);
    },
    addressFound: function(results, status) {
        if (status == google.maps.GeocoderStatus.OK)
        {
            var place = results[0];
            Map.showPlace(place);
            $("#location-search-box-message").html(place.formatted_address);
        } else {
            $("#location-search-box-message").html("Nu am gasit nimic.");
        }
    },
    showPlace : function(place) {
        if (place.geometry.viewport) {
            Map.map.fitBounds(place.geometry.viewport);
            Map.setYourPosition(place.geometry.location);
        } else {
            Map.map.setCenter(place.geometry.location);
            Map.map.setZoom(18);
        }
    },
    setYourPosition : function (myLocation)
    {
//        Map.theMarker.position = myLocation;
        Map.map.setCenter(myLocation);
//        Map.theMarker.setMap(null);
//        Map.theMarker.setMap(Map.map);
    }
};


//Used in NewHubForm
var MapSelectLocation = {
    marker_image: '',
    InitMarker: function() {
        ms = MapSelectLocation;
        ms.marker_image = '/css/map/map_hub.png';
        ms.hubMarker = new google.maps.Marker({
            position: default_location,
            map: Map.map,
            icon: ms.marker_image,
            title: 'HQ',
            draggable: true
        });
    },
    SetPosition: function(myLocation) {
        MapSelectLocation.hubMarker.position = myLocation;
        MapSelectLocation.hubMarker.setMap(null);
        MapSelectLocation.hubMarker.setMap(Map.map);
        Map.map.setCenter(myLocation);
    },
    FoundAddress : function(position) {
        MapSelectLocation.hubMarker.position = position;
        MapSelectLocation.hubMarker.setMap(null);
        MapSelectLocation.hubMarker.setMap(Map.map);
    }
};

