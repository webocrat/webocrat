
var geoTimeout;

var NewDogForm = {
    markerImage : {
        dog : new google.maps.MarkerImage(
            '/css/map/icon_dog1.png',
            new google.maps.Size(41,40),
            new google.maps.Point(0,0),
            new google.maps.Point(20,34))
    },
    marker : {
        location : false
    },
    Init: function () {

        $("#nr-caini").numeric({ decimal: false, negative: false },
            function() {
                this.value = "1";
                this.focus();
            });

        $("#nr-caini").focusout(function() {
            var nrc = $("#nr-caini");
            if (nrc.val()==0) {
                nrc.val(1);
            }
        });

        /* Location */
//                Map.initAutocomplete('location-search-box');
//                $("#location-search-box").unbind();
        $("#location-search-box").keyup(NewDogForm.findLocation);

        NewDogForm.goToStepAddButton();
    },
    initLocationMarker: function () {

        alert("init");
        if (NewDogForm.marker.location) {
            // remove from map
            NewDogForm.marker.location.setMap(null);
        }

        var EXIF_location = ImageUploader.EXIFLatLng;
        var location = EXIF_location || ImageUploader.defaultLatLng;

        NewDogForm.marker.location = new google.maps.Marker({
            position: location,
            map: Map.map,
            icon: NewDogForm.markerImage.dog,
            title: 'adauga un catel',
            draggable: true
        });

        Map.map.setCenter(location);

        if (EXIF_location) Map.map.setZoom(18);
    },
    initLocation: function () {
        var EXIF_location = ImageUploader.EXIFLatLng;
        var location = EXIF_location || ImageUploader.defaultLatLng;

        if (EXIF_location) {
           Map.map.setCenter(location);
           Map.map.setZoom(18);
        }
        else
        {
            //no exif location
        }

        NewDogForm.geoReverseRequest();
    },
    findStringInArray : function (stringArray, theString) {
        for (var j=0; j<stringArray.length; j++) {
            if (stringArray[j].match (theString)) return j;
        }
        return -1;
    },
    setGeoReverse : function(enable) {
        if (enable) {
            //add listener
            google.maps.event.addListener(Map.map, 'center_changed',
                function() {
                    if (geoTimeout) clearTimeout(geoTimeout);
                    geoTimeout = setTimeout(NewDogForm.geoReverseRequest, 1500);
                    NewDogForm.locationButton(false);
                });
        } else {
            //remove listener
            google.maps.event.clearListeners(Map.map, 'center_changed');
        }
    },
    geoReverseRequest : function() {
        Map.geocoder.geocode({ 'latLng' : Map.map.getCenter(),
                'region' : 'ro'},
            NewDogForm.geoReverseResponse);
    },
    geoReverseResponse : function(results, status) {
        //TODO: move to map object
        if (status == google.maps.GeocoderStatus.OK)
        {
            var place = results[0];

            //extract address components
            var comp = {
                'route' : '',   // strada
                'locality' : false, // localitate
                'sublocality' : false, // sector
                'administrative_area_level_1': false,   // judet
                'country' : false
            };

            for (index in comp) {
                comp_key = index;

                for (i=0; i<place.address_components.length; i++) {
                    var c = place.address_components[i];

                    var it = NewDogForm.findStringInArray(c.types, comp_key);
                    if (it != -1) comp[comp_key] = c.long_name;
                }
            }

            NewDogForm.addressComponents = comp;
            var strada = comp.route;
            var localitate = comp.locality ? comp.locality : comp.administrative_area_level_1;
            localitate = localitate.replace("Bucharest", "București");

            $("#zona").html("@" + strada + "</br>" + localitate );
//                console.log(comp,place);
            NewDogForm.locationButton(true);
        }
    },
    goToStepAddButton : function() {
        // hide dog-add div
        // resize map
        $("#dog-add").hide();
        $(".step").hide();
        $("#map_canvas").removeClass("narrow");
        google.maps.event.trigger(Map.map, "resize");

        // show interface
        $("#adauga-un-caine-button").unbind().click(NewDogForm.goToStepUploadPhoto);
        $("#adauga-un-caine-button").show();
    },
    goToStepUploadPhoto : function() {
        /* transition */
        // resize map
        // display DogForm

        /* show interface */
        $("#dog-add").show();
        $(".step").hide();
        $("#map_canvas").addClass("narrow");
        google.maps.event.trigger(Map.map, "resize");

        $("#upload-photo").show();
        $("#upload-image-button").unbind().click(ImageUploader.ClickUpload);                 //upload button
        $('#dog-add').css("visibility", "visible");
        $("#goback-button").html("ÎNCHIDE").unbind().click(NewDogForm.goToStepAddButton);
    },
    goToStepCrop : function(visible) {
        $(".step").hide();
        $("#crop-photo").show();
        $("#map_canvas").addClass("narrow");
        google.maps.event.trigger(Map.map, "resize");


        $("#upload-photo-button").unbind().click(NewDogForm.sendPhoto);
        $("#dog-add").show();
        $("#dog-add").css("visibility", visible ? "visible" : "hidden");
        $("#goback-button").html("&lt;&lt; ÎNAPOI").unbind().click(NewDogForm.goToStepUploadPhoto);

        NewDogForm.setGeoReverse(false);
    },
    sendPhoto: function() {
        $("#upload-photo-button").unbind();
        ImageUploader.drawToCanvas();
        ImageUploader.postCanvasToServer(NewDogForm.goToStepLocation);
        // will call NewDogForm.goToStepLocation
    },
    goToStepLocation : function() {
        NewDogForm.setGeoReverse(true);

        $(".step").hide();
//            NewDogForm.initLocationMarker();
        NewDogForm.initLocation();
        if (ImageUploader.hasEXIFGeoLocation) {
            $("#confirm-location").show();
            /* EXIF Location */
        } else {
            $("#select-location").show();
        }
        NewDogForm.locationButton(true);
        $("#goback-button").html("&lt;&lt; ÎNAPOI").unbind().click(NewDogForm.goToStepCrop);
    },
    locationButton : function(enabled) {
        $("#confirm-location-button").unbind();
        $("#set-location-button").unbind();
        if (enabled) {
            $("#confirm-location-button").click(NewDogForm.sendNewDog);
            $("#set-location-button").click(NewDogForm.sendNewDog);
            $(".location-wait").hide();
        } else {
            $(".location-wait").show();
        }
    },
    findLocation : function(event) {
        if (event.keyCode == 13) {
            var addr = $("#location-search-box").val();
            Map.theMarker = NewDogForm.marker.location;
            Map.findAddress(addr);
        }
    },
    sendNewDog: function() {
        NewDogForm.setGeoReverse(false);

        // gather info
        // - location
        // - photo
        // - nr caini

//            var position = NewDogForm.marker.location.position;
        var position = Map.map.getCenter();
        var lat = position.lat() % 180;
        var lng = position.lng() % 180;

        var theData = {
//                nr_caini: $("#nr-caini").val(),
            name : $("#dog-name").val(),
            place : JSON.stringify(NewDogForm.addressComponents),
            location: lat+","+lng,
            latitude : lat,
            longitude : lng,
            photo_id: ImageUploader.photo_id,
            token : user_access_token
        };

        console.log(theData);

        $.ajax({
            url: "/hc.adddog",
            data: JSON.stringify(theData),
            success: function(data) {
                if (data.code == "1") {
                    console.log("ADDED:" + data.id);
                    NewDogForm.goToStepAddButton();
                    MOM.loadMarkers();
                }
//                    window.location.href = "/"+data.id+".hub";
            },
            error: function(jqXHR, textStatus) {
                console.log( "Request failed: " + textStatus );
            },
            type: "POST",
            dataType: 'json',
            contentType: 'application/json'
        });



    }
};
