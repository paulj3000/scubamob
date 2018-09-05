SM.DiveSites = 
{
    userloc: {},     // center on San Diego for now
    markerArray:[],
    diveSiteArray:[],
    currentInfoWindow: null,
//    map: null,
    initUserLocation: function()
    {
        this.userloc = { 'lat': 32, 'lng': -117 };     // center on San Diego for now
        tmpCoords   = jQuery.parseJSON($.sessionGet('divesites', 'mapcoords'));
        
        if (tmpCoords && $.getObjectKeys(tmpCoords))
        {

            // make sure we have valud latitude and longitude
            if (tmpCoords['lat'] && tmpCoords['lng'])
            {
                this.userloc    = tmpCoords;
                return;
            }
        }

        if (navigator.geolocation)
        {
            // attempt to get the location from the user
            navigator.geolocation.getCurrentPosition(SM.DiveSites.initUserLocationPost);
        }
    },
    initUserLocationPost: function(position)
    {
        // here are the latitudes and longitudes from the user's site
        this.userloc['lat'] = position.coords.latitude;
        this.userloc['lng'] = position.coords.longitude;
        $.sessionSet('divesites', 'mapcoords',  JSON.stringify(this.userloc)); 
    },
    initMap: function()
    {
        userloc = this.userloc;
        self = this;
        var latlng = new google.maps.LatLng(userloc.lat, userloc.lng);  // focus on San Diego for now

        currentZoom = $.sessionGet('divesites', 'zoomLevel', 2);

        var myOptions = {
            zoom: currentZoom,
            minZoom: 3,
          //  maxZoom: 12,
            center:  latlng,
            mapTypeControl: false,
            panControl: false,
            streetViewControl: false,
            mapTypeId:  google.maps.MapTypeId.HYBRID
        };

        map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

        // and add some listeners 
/*
        google.maps.event.addListener(map, 'zoom_changed', function() 
        {
            var latlng = new google.maps.LatLng(self.userloc.lat, self.userloc.lng); 
            map.setCenter(latlng);
            $.sessionSet('divesites', 'zoomLevel', map.getZoom()); 
        });

        google.maps.event.addListener(map, 'center_changed', function() {
            latlng  = map.getCenter();
            tmpLatLng   = { 'lat': latlng['jb'], 'lng': latlng['kb'] };
            self.userloc = tmpLatLng;
            $.sessionSet('divesites', 'mapcoords', JSON.stringify(tmpLatLng));
        });
*/
        // make sure we have this bounded properly
        this.latLngBounds = new google.maps.LatLngBounds();
        
        // and of course, set our map object into the object itself
        this.map = map;
       
        $.get("/divesites/json/locations", function(data)
        {
            self.addMarkers(data);
        });
    },
    initMapResize: function()
    {
        google.maps.event.trigger(this.map, 'resize');
        map.setZoom(this.map.getZoom());
    },
    initScreenSize: function()
    {
        // get our offset for the window to make it look good
        var OFFSET_HEIGHT   = 70;
        var OFFSET_WIDTH    = 565;
        screenHeight   = $(window).height() - OFFSET_HEIGHT;
        screenWidth   = ($(window).width()) - OFFSET_WIDTH;
        
        // ...and change the canvas size / width for Google Map
      //  $('#map_canvas').css('height', screenHeight + 'px');
       // $('#map_canvas').css('width', screenWidth + 'px');
    },
    displayMap: function()
    {
        var script = document.createElement("script");
        script.type = "text/javascript";
        script.src = "http://maps.google.com/maps/api/js?sensor=false&callback=SM.DiveSites.initMap";
        document.body.appendChild(script);
    },

    addMarkers: function(siteData)
    {
        // set up the flag object
        markerArray     = this.markerArray;
        diveSiteArray   = this.diveSiteArray;
        var flag = new google.maps.MarkerImage(divemarker,
                                               new google.maps.Size(20, 33),
                                               new google.maps.Point(0, 0),
                                               new google.maps.Point(0, 33));

        // now take the parse data and create an object out of it
        //var siteData = jQuery.parseJSON(data);
        var self 	= this;

        for (i=0; i < siteData.sites.length; ++i)
        {
            try
            {
                site    = siteData.sites[i];
                latlng  = site.latlng;

                // let's create a marker 
                var markerLatLng = new google.maps.LatLng(latlng['latitude'], latlng['longitude']);
                var marker = new google.maps.Marker({   position: markerLatLng, icon:flag   });

                // now set the marker onto the map
                marker.setMap(this.map);
                markerArray.push(marker);
                diveSiteArray.push(site);
        
                // ...add an event handler for a mouseover event.... 
                google.maps.event.addListener(marker, 'mouseover', (function(markerArg, i)
                {
                    return function()
                    {
                        self._openInfoWindow(i);
                    };
                })(marker, i));        

                // ...add an event handler for a mouseover event.... 
                google.maps.event.addListener(marker, 'click', (function(markerArg, id)
                {
                    return function()
                    {
                    	$.get('/divesites/json/getdivesiteinfo/' + id, function(data)
                    	{
                            try
                            {
                                data    = data['data']['items'][0];
                                self._showInfoPane(data);
                            }
                            catch(err)
                            {
                            }
                    	});
                    };
                })(marker, site.id)); 
            }
            catch (err)
            {
                console.log("error parsing item:  " + i + ":  " + err);
            }
            
        }
    },
    _openInfoWindow: function(id)
    {
        map         = this.map;
        marker      = markerArray[id];
        diveSite    = diveSiteArray[id];

        var infoWindow = new google.maps.InfoWindow({
                            content: this._generateInfoWindowData(id)
                            });

        self    = this;
        google.maps.event.addListener(marker,'mouseout', function() 
        {
            infoWindow.close();
//            setTimeout(function () { console.log(self); }, 5000);
        });

        infoWindow.open(map,marker);

        if (! this.currentInfoWindow)
            this.currentInfoWindow  = new Object;

        this.currentInfoWindow.infoWindow   = infoWindow;
        this.currentInfoWindow.id   = id;
    },

    _showInfoPane: function(data)
    {
        $('#divshop-address2').show("slide", { direction: "right" });

        html    = $('#infopane_wrapper').html();
        var res = Mustache.render(html, data);
        $('#divsite-detail').html(res);

        $(".favorite").click(function() 
        {
            var $this   = $(this)
            var divesiteid  = $this.val();
            var favorite    = false;
            if ($this.is(":checked"))
                favorite    = true;
        
            $.post("/account/json/setfavorite", { 'divesite': divesiteid, 'favorite': favorite }, function(data)
            {
                console.log(divesiteid + " value " + favorite + " is now set");
            });
        })

    },

    _generateInfoWindowData: function(id)
    {
        // get the hop number index.  Because the hop starts by 1, we need to start
        // our indexing from 0
        //
        // get the data
        site    = this.diveSiteArray[id];

        addressObj	= site.address;
        address = "";

        if (addressObj)
        {
            address	= addressObj.address + "<br/>";
            if (addressObj.address2)
                address += addressObj.address2 + "<br/>";
            address	+= addressObj.city + ", " + addressObj.state + "  " + addressObj.zip;
        }

        rating  = 'Easy';
        
        // ok, generate an info window
        retval = '<div>' + site.title + '</div>' + 
                 '<div><ul><li>' + address + '</li></ul></div>' +
                 '<div><ul><li>Difficulty:  ' + rating + '</li></ul></div>';

        return retval;
    }


}
