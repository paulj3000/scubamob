SM.DiveSites_New = 
{
    userloc: {},     // center on San Diego for now
    markerArray:[],
    diveSiteArray:[],
    currentInfoWindow: null,
    initUserLocation: function()
    {
        this.userloc = { 'lat': 32, 'lng': -117 };     // center on San Diego for now
    },
    initMap: function()
    {
        userloc = this.userloc;
        self = this;
        var latlng = new google.maps.LatLng(userloc.lat, userloc.lng);  // focus on San Diego for now

        currentZoom = $.sessionGet('divesites', 'zoomLevel', 2);

        var myOptions = {
            zoom: currentZoom,
            //minZoom: 3,
            center:  latlng,
            //mapTypeControl: false,
            //panControl: false,
            //streetViewControl: false,
            mapTypeId:  google.maps.MapTypeId.HYBRID
        };

        map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

        // and add some listeners 
        google.maps.event.addListener(map, "click", function(event)
        {
            // display the lat/lng in your form's lat/lng fields
            latLng  = event.latLng;
            $('#id_latitude').val(latLng.lat());
            $('#id_longitude').val(latLng.lng());

            // clear out all markers
            markerArray = self.markerArray;
            $.each(markerArray, function(i, m) {
                self.markerArray[i].setMap(null);
            });

            var flagImage = new google.maps.MarkerImage(divemarker,
                                                    new google.maps.Size(20, 33),
                                                    new google.maps.Point(0, 0),
                                                    new google.maps.Point(10, 40));

            marker = new google.maps.Marker({
                             position: latLng,
                             map: self.map,
                             icon: flagImage
           });

            self.markerArray.push(marker);

        });

        // and of course, set our map object into the object itself
        this.map = map;
    },
    initScreenSize: function()
    {
        // get our offset for the window to make it look good
        var OFFSET_HEIGHT   = 70;
        var OFFSET_WIDTH    = 565;
        screenHeight   = $(window).height() - OFFSET_HEIGHT;
        screenWidth   = ($(window).width()) - OFFSET_WIDTH;
        
        // ...and change the canvas size / width for Google Map
       // $('#map_canvas').css('height', screenHeight + 'px');
        //$('#map_canvas').css('width', screenWidth + 'px');
    },
    displayMap: function()
    {
        var script = document.createElement("script");
        script.type = "text/javascript";
        script.src = "http://maps.google.com/maps/api/js?sensor=false&callback=SM.DiveSites_New.initMap";
        document.body.appendChild(script);
    },
}
