

jQuery.event.props.push("dataTransfer");

var ImageUploader = {
    /* interface */
    hasFileReader : false,
    form_div: ".upload-image-form",
    error_file_format: "Poți încărca doar fișiere JPG, PNG sau BMP",
    error_size_too_small:"Dimensiunea minimă a imaginii este de 200x200 pixeli",
    defaultLatLng : false,
    /* data */
    file: null,
    image_file_data: 0,
    image_file_width: 0,
    image_file_height: 0,
    /* location */
    hasEXIFGeoLocation : false,
    EXIFLatitude : 0,
    EXIFLongitude : 0,
    EXIFOrientation : 0,
    EXIFLatLng : false,

    crop_width:300,
    crop_height:300,
    cnvs: null,
    $cnvs : null,
    dragobj: null,
    min_zoom:0.1,
    max_zoom:1.5,
    zoom:1,

    photo_id: false,
    Init: function (default_location) {
        me = ImageUploader;
        me.hasFileReader = typeof window.FileReader !== 'undefined';

        me.defaultLatLng = default_location;

        //events
        $("#fileup").unbind().change(me.fileInputChanged);
        $(document).on("drop", null, me.onDrop);
//        $(document).on("dragover", me.onDragOver);
//        $(document).on("dragend", me.onDragEnd);

        me.$cnvs = $('#cnvs');
        me.cnvs = document.getElementById("cnvs");

        me.dragobj = $("#drag-image");
        me.dragobj.watch("left,top,width,height", me.drawToCanvas, 25, "drag-image");
    },
    ClickUpload: function(e) {
        me = ImageUploader;
        $("#fileup").click();
    },
    onDragOver : function(e) {
//            console.log("drag-enter");
        e.stopPropagation();
        e.preventDefault();
    },
    onDragEnd : function(e) {
//            console.log("drag-leave");
        e.stopPropagation();
        e.preventDefault();
    },
    onDrop: function(e) {
        e.preventDefault();

        me = ImageUploader;
        var dt = e.dataTransfer;
        me.file = dt.files[0];
        me.checkUploadedFile();
    },
    fileInputChanged: function(e) {
        me = ImageUploader;
        me.file = e.target.files[0];
        me.checkUploadedFile()
    },
    checkUploadedFile: function(e) {
        // drag-and-drop & upload image    meet here
        // logic :
        //    invalid image -> show error
        //    valid image -> start client side DataURL reader
        // will call .onDataLoad
        me = ImageUploader;
        if (me.file.type.match(/image\/(png|gif|jpg|jpeg|bmp)/)) {

            if (me.hasFileReader){
                // gif, png, jpg or bmp
                var reader = new FileReader();
                reader.onload = me.onDataLoad;            //image reader
                reader.readAsDataURL(me.file);
            } else {
                //TODO: upload to some server, return data
            }
            // TODO: raise event crop -> show form in event handler
            NewDogForm.goToStepCrop(false);
        } else {
            $("#photo-error-message").html(me.error_file_format).show();
            me.showZoomSlider(false);
            //TODO: raise event error_format
            NewDogForm.goToStepUploadPhoto();
        }
    },
    onDataLoad: function(e) {
        me = ImageUploader;
        // create the image element and setup dragging
        me.image_file_data = e.target.result;

        me.droppedImage = new Image();
        me.droppedImage.onload = me.onImageLoaded;
        me.droppedImage.id = "drag-image";
        me.droppedImage.src = me.image_file_data;
    },
    onImageLoaded: function(e) {
        me = ImageUploader;
//        console.log("w:"+me.droppedImage.width+" h:"+me.droppedImage.height);

        //zoom
        var aspect_ratio = me.droppedImage.width / me.droppedImage.height;
        me.min_zoom = (aspect_ratio > 1) ?
            me.crop_height / me.droppedImage.height :
            me.crop_width / me.droppedImage.width;

        if (me.min_zoom > me.max_zoom) {
            me.min_zoom = me.max_zoom;
            $("#photo-error-message").html(me.error_size_too_small).show();
            me.showZoomSlider(false);
            // TODO: raise event (error -> small image)
            NewDogForm.goToStepUploadPhoto();
            return;
        }

//        me.dragobj = $(me.droppedImage);
        me.dragobj.css('width', me.droppedImage.width).css('height', me.droppedImage.height);
        me.dragobj.draggable({ cursor: 'move' });

        me.InitDragZoom();

        var binaryReader = new FileReader();
        binaryReader.onload = me.onBinaryLoad;
        binaryReader.readAsBinaryString(me.file);
        // will call .onBinaryLoad
    },
    onBinaryLoad: function(e) {
        me = ImageUploader;

        // EXIF DATA LOAD
        // *#$%
        exifData = $("<div></div>");
        var bf = new BinaryFile(e.target.result, 0, 0);
        exifData.exifBinaryLoad(bf);

        me.EXIFOrientation = exifData.exif("Orientation")[0];
        console.log("orientation:"+me.EXIFOrientation);
        //TODO: auto orientation
        if (me.EXIFOrientation=="6") {
            //switch width and height
            //rotate image 90
        }

        var lngArray = exifData.exif("GPSLongitude")[0];
        var latArray = exifData.exif("GPSLatitude")[0];

        if (!latArray && !lngArray)
        {
//            NewDogForm.initLocationMarker(me.default_location);
            ImageUploader.hasEXIFGeoLocation = false;
            ImageUploader.EXIFLatLng = false;
        } else
        {
            me.hasEXIFGeoLocation = true;
            me.EXIFLatitude = me.DMStoDEC(latArray[0],latArray[1],latArray[2]);
            me.EXIFLongitude = me.DMStoDEC(lngArray[0],lngArray[1],lngArray[2]);

//            console.log('EXIF lat='+me.EXIFLatitude+"   lon=" + me.EXIFLongitude);

            me.EXIFLatLng = new google.maps.LatLng(me.EXIFLatitude, me.EXIFLongitude);
            Map.map.panTo(me.EXIFLatLng);
        }
    },
    DMStoDEC : function(deg,min,sec)
    {
        // Converts DMS ( Degrees / minutes / seconds )
        // to decimal format longitude / latitude
        return deg+(((min*60)+sec)/3600);
    },
    InitDragZoom: function() {
        me = ImageUploader;

//      InitZoomHandle;
        if (me.dragdealerZoom == undefined) {
            me.dragdealerZoom = new Dragdealer('zoom-slider', {
                animationCallback: me.dragZoom,
                slide:true,
                speed:45
            });
        }
        me.showZoomSlider(true);

        me.setZoom(me.min_zoom);
        me.dragdealerZoom.setValue(0);

        //center
        me.dragobj.css('top', -(me.dragobj.height() - me.crop_height) * 0.5);
        me.dragobj.css('left', -(me.dragobj.width() - me.crop_width) * 0.5);

        // TODO: raise event crop -> show
        NewDogForm.goToStepCrop(true);
    },
    showZoomSlider: function(show) {
        $("#zoom-slider-bg").css('visibility',show ? 'visible' : 'hidden');
    },
    dragZoom: function(value) {
        me = ImageUploader;
        var zoom = me.min_zoom + (me.max_zoom - me.min_zoom) * value;
        me.setZoom(zoom);
    },
    setZoom: function(zoom) {
        me = ImageUploader;

        //calculate center of cropped photo (0.0 to 1.0)
        var offset = me.dragobj.position();
        var hcw = me.crop_width/2;
        var hch = me.crop_height/2;
        var center_x = (-offset.left + hcw)/me.dragobj.width();
        var center_y = (-offset.top + hch)/me.dragobj.height();

        // zoom
        var w = parseInt(me.droppedImage.width * zoom);
        var h = parseInt(me.droppedImage.height * zoom);
        me.dragobj.width(w);  //set width
        me.dragobj.height(h); //set height
        me.zoom = zoom;

        // reposition to maintain center
        me.dragobj.css('left', hcw - parseInt(w * center_x));
        me.dragobj.css('top', hch- parseInt(h * center_y));


        // recalculate containment
        var container = $("#photo");
        var o = container.offset();
        var x1 = o.left + me.crop_width - w;
        var y1 = o.top + me.crop_height - h;
        var x2 = o.left;
        var y2 = o.top;
        containment = x1+" "+y1+" "+x2+" "+y2;
        me.dragobj.draggable("option", "containment", [x1, y1, x2, y2]); //x1 y1 x2 y2

        //force containment
        //TODO: remove jquery.ui.draggable
        var pos = me.dragobj.position();
        var x = pos.left;
        var y = pos.top;

        if (x > 0) me.dragobj.css('left', 0);  //over left bound
        if ((a = x+w-me.crop_width) < 0) me.dragobj.css('left', x-a); // over right bound
        if (y > 0) me.dragobj.css('top', 0);
        if ((a = y+h-me.crop_height) < 0) me.dragobj.css('top', y-a); // over right bound

        me.drawToCanvas();
    },
    drawToCanvas: function() {
        me = ImageUploader;
        ctx = me.cnvs.getContext('2d');
        ctx.clearRect(0,0,me.crop_width, me.crop_height);
//      this is working with img element
//        var img = document.getElementById("drag-image");
//        var pos = me.dragobj.position();
//        ctx.drawImage(img, pos.left, pos.top, img.width, img.height);
        // with no img element
        var pos = me.dragobj.position();
        ctx.drawImage(me.droppedImage, pos.left, pos.top, me.dragobj.width(), me.dragobj.height());
    },
    postCanvasToServer: function(callback) {
        if (callback && typeof(callback) === "function") {
            ImageUploader.postCanvastToServerCallback = callback;
        } else {
            ImageUploader.postCanvastToServerCallback = function() {};
        }
        var canvas = document.getElementById("cnvs");
        canvas = me.cnvs;

        $.ajax({ type:'POST',
            url: '/image.upload',
            data: {
                img : canvas.toDataURL('image/jpeg')
            },
            success:
                function(data) {
                    ImageUploader.photo_id = data.id;
                    ImageUploader.postCanvastToServerCallback();
                },
            dataType: 'json'
        });
    }

};