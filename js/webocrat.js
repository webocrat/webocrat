//map javascript
var webocrat = webocrat || {
    //default values
    user : {
        logged_in:false,
        registered : false,
        theToken : false
    },
    token : function() {
        return webocrat.theToken;
    },
    service : function(endpoint, data, template, target) {
        $.ajax({
            url: endpoint,
            data: JSON.stringify(data),
            success: function(data) {
                if (webocrat)
//                console.log("OK:" + data.id);
                window.location.href = "/"+data.id+".hub";
            },
            error: function(jqXHR, textStatus) {
//                console.log( "Request failed: " + textStatus );
            },
            type: "POST",
            dataType: 'json',
            contentType: 'application/json'
        });
    },
    load : function(endpoint) {

    }

};


/*

    service example:
        request :
            protorpc:
            media-type : text | html | json | image | video
            message : byte64
            message_over : url | out



    */