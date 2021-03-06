	var map;
	var point_location=0;
	var point_location_result_id = "";

	//Setting on/off mode for pointing locations on map
	function map_pointer_switch(id){
     	    if (point_location==0){
		point_location=1;
		point_location_result_id=id;
	    } else {
		point_location=0;
		point_location_result_id="";
	    }
	}

	$(function() {
		$( "#slide" ).slider();
	});

	$(function() {
		$( "#key" ).draggable();
		});
        $(function() {
			$( "#start_date" ).datepicker();
		});
	$(function() {
			$( "#end_date" ).datepicker();
		});

	$(function() {
			$( "#trip_date" ).datepicker();
		});

	function from_me(coords, id){
	    if(coords != "null"){
		var s= document.getElementById(id);
		s.value = coords;
            } else {
		var s= document.getElementById(id);
		s.value = lon+","+lat;
            }
	}

        //Vector visibility toggle
        $(document).ready(function(){
		function walkingPoints()  
		        {if (walking.getVisibility() == true) 
		         {walking.setVisibility(false);}  
		         else  
		          {walking.setVisibility(true);}}
		function stillPoints()  
		        {if (still.getVisibility() == true) 
		         {still.setVisibility(false);}  
		         else  
		          {still.setVisibility(true);}}
		function unknownPoints()  
		        {if (unknown.getVisibility() == true) 
		         {unknown.setVisibility(false);}  
		         else  
		          {unknown.setVisibility(true);}}
		function bikePoints()  
		        {if (bike.getVisibility() == true) 
		         {bike.setVisibility(false);}  
		         else  
		          {bike.setVisibility(true);}}
		function vehiclePoints()  
		        {if (vehicle.getVisibility() == true) 
		         {vehicle.setVisibility(false);}  
		         else  
		          {vehicle.setVisibility(true);}}
		function locationPoints()  
		        {if (locations.getVisibility() == true) 
		         {locations.setVisibility(false);}  
		         else  
		          {locations.setVisibility(true);}}
		function tripPoints()  
		        {if (trip_feature.getVisibility() == true) 
		         {trip_feature.setVisibility(false);}  
		         else  
		          {trip_feature.setVisibility(true);}}
		$("#still").on("change", stillPoints);
		$("#locations").on("change", locationPoints);
		$("#walk").on("change", walkingPoints);
		$("#unknown").on("change", unknownPoints);
		$("#vehicle").on("change", vehiclePoints);
		$("#trip").on("change", tripPoints);
		$("#bike").on("change", bikePoints);
		  $("button").click(function(){
		    $.ajax({url:"demo_test.txt",success:function(result){
		      $("#div1").html(result);
		    }});
		  });
		
		});
        
        //Options for locator
        var options = {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0
        };

        function error(err) {
          console.warn('ERROR(' + err.code + '): ' + err.message);
          init();
        };

        //Styles for different kind of vectors
        var vehicleLine = {
                strokeColor: "blue",
                strokeWidth: 8,
                strokeOpacity: 0.4,
            };
        var bikeLine = {
                strokeColor: "coral",
                strokeWidth: 6,
                strokeOpacity: 0.6
            };
        
	var styleLine = {
                strokeColor: "red",
                strokeWidth: 8,
                strokeOpacity: 0.4
            };
            
        var styleWalk = {
                strokeColor: "green",
                strokeWidth: 5,
                strokeOpacity: 0.4
            };
        var styleStill = {
                strokeColor: "yellow",
                strokeWidth: 3,
                strokeOpacity: 0.4
            };

	function get_location_icon(type){
	    var icon = null;
	    if(type == "UN") {
		icon = known_place_icon + "unknown.png";
	    } else {
		icon = known_place_icon + type + ".png";
	    }
            var styleLocation = {
		externalGraphic: icon,
		cursor: 'pointer',
		graphicWidth: 32,
		graphicHeight: 32,
		fillOpacity: 1
            };
	    return styleLocation;
	}

	var colors = {
            bike: "rgb(0, 0, 255)", 
            vehicle: "rgb(255, 0, 0)", 
            walk: "rgb(0, 255, 0)",
            still: "rgb(128, 128, 128)",
            unknown: "rgb(0, 128, 255)"
        };

// Define three rules to style the cluster features.
        var bikeRule = new OpenLayers.Rule({
            filter: new OpenLayers.Filter.Comparison({
        	type: OpenLayers.Filter.Comparison.EQUAL_TO,
        	property: "activity",
        	value: "on-bicycle"
            }),
            symbolizer: {
		fillColor: colors.bike,
                fillOpacity: 0.7, 
		strokeOpacity: 0.6,
                strokeColor: colors.bike,
		strokeWidth: 5
	    }
	});
        var vehicleRule = new OpenLayers.Rule({
            filter: new OpenLayers.Filter.Comparison({
        	type: OpenLayers.Filter.Comparison.EQUAL_TO,
        	property: "activity",
		value: "in-vehicle"
            }),
            symbolizer: {
		fillColor: colors.vehicle,
                fillOpacity: 0.7, 
		strokeOpacity: 0.6,
                strokeColor: colors.vehicle,
		strokeWidth: 5,
		label: "${transport}"
	    } 
	});
        var walkRule = new OpenLayers.Rule({
            filter: new OpenLayers.Filter.Comparison({
        	type: OpenLayers.Filter.Comparison.EQUAL_TO,
        	property: "activity",
        	value: "on-foot"
            }),
            symbolizer: {
		fillColor: colors.walk,
                fillOpacity: 0.7, 
		strokeOpacity: 0.6,
                strokeColor: colors.walk,
		strokeWidth: 5
	    }
	});
	var unknownRule = new OpenLayers.Rule({
            filter: new OpenLayers.Filter.Comparison({
        	type: OpenLayers.Filter.Comparison.EQUAL_TO,
        	property: "activity",
        	value: "unknown"
            }),
            symbolizer: {
		fillColor: colors.unknown,
                fillOpacity: 0.7, 
		strokeOpacity: 0.6,
                strokeColor: colors.unknown,
		strokeWidth: 5
	    }
	});
        var stillRule = new OpenLayers.Rule({
            filter: new OpenLayers.Filter.Comparison({
		type: OpenLayers.Filter.Comparison.EQUAL_TO,
		property: "activity",
		value: "still"
            }),
	    symbolizer: {
		fillColor: colors.still,
                fillOpacity: 0.7,
		strokeOpacity: 0.6,
                strokeColor: colors.still,
		strokeWidth: 5
	    }
	});

      	// Create a Style that uses the three previous rules
	var style = new OpenLayers.Style(null, {
	   rules: [bikeRule, vehicleRule, walkRule, unknownRule, stillRule]
	});

	var locations = "";
	var trip_feature = "";
	
	var vehicle = new OpenLayers.Layer.Vector("Vehicle", {style: vehicleLine});
	var unknown = new OpenLayers.Layer.Vector("Unknown", {style: styleLine});
	var walking = new OpenLayers.Layer.Vector("Walking", {style: styleWalk});
	var still = new OpenLayers.Layer.Vector("Still", {style: styleStill}); 
	var bike = new OpenLayers.Layer.Vector("Bike", {style: bikeLine}); 

        var lon = 24.9375,
            lat = 60.1708,
            zoom = 13,
            epsg4326 = new OpenLayers.Projection('EPSG:4326'),
            epsg900913 = new OpenLayers.Projection('EPSG:900913');

        function getLocation()
        {
          if (navigator.geolocation)
            {
            navigator.geolocation.getCurrentPosition(showPosition,error,options);
            }
          else{
                console.log("Geolocation is not supported by this browser.");
            }
        }
        
        function showPosition(position)
        {
            lat = position.coords.latitude;
            lon = position.coords.longitude;
	    	init();
        }

        function getMarker(lon, lat)
        {
		var markers = new OpenLayers.Layer.Markers( "Markers" );
		map.addLayer(markers);

		var size = new OpenLayers.Size(21,25);
		var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
		var icon = new OpenLayers.Icon('http://www.openlayers.org/dev/img/marker.png', size, offset);
		markers.addMarker(new OpenLayers.Marker(new OpenLayers.LonLat(lon,lat),icon));
		markers.addMarker(new OpenLayers.Marker(new OpenLayers.LonLat(lon,lat),icon.clone()));

		return markers;
        }

	//Init popups for places
	function getFeaturesForPopup(to){
	    var toMercator = OpenLayers.Projection.transforms['EPSG:4326'][to];
	    var features = []; 
	    var size = places.length;   
	    for(var i = 0; i < size; i++) {
		place = places[i].split(";");
		var coords = place[0]+","+place[1]
		features[i] = new OpenLayers.Feature.Vector(
		        toMercator(new OpenLayers.Geometry.Point(
		            place[0], place[1])), 
		        {
		            Address : place[3],
		            Coordinates : coords,
		            type : place[4],
		        }, get_location_icon(place[4]));
	    }
	    return features;
	}

	//getTripFeaturesForPopup
	function getTripFeaturesForPopup(to){
	    var toMercator = OpenLayers.Projection.transforms['EPSG:4326'][to];
	    var features = []; 
	    var size = trips.length;   
	    for(var i = 0; i < size; i++) {
		place = places[i].split(";");
		var coords = place[0]+","+place[1]
		features[i] = new OpenLayers.Feature.Vector(
		        toMercator(new OpenLayers.Geometry.Point(
		            place[0], place[1])), 
		        {
		            Address : place[3],
		            Coordinates : coords,
		            type : place[4],
		        }, get_location_icon(place[4]));
	    }
	    return features;
	}


	function getCoordinates(e) {
		 // this should work
		 var lonlat = map.getLonLatFromViewPortPx(e.xy);
		 //alert("You clicked near " + lonlat.lat + " N, " +
			//	                          + lonlat.lon + " E");
	}

	function get_location_on_map(e){
	    var lonlat = map.getLonLatFromPixel(e.xy);
	    brit = new OpenLayers.Projection("EPSG:900913");
	    google = new OpenLayers.Projection("EPSG:4326");

	    lonlatclone = lonlat.clone()
	    lonlatclone.transform(brit, google)
                    
	    return lonlatclone;
	}


        function init(){
		var options_select = {
		    onSelect: getCoordinates,
		};

		OpenLayers.Control.Click = OpenLayers.Class(OpenLayers.Control, {                
                defaultHandlerOptions: {
                    'single': true,
                    'double': false,
                    'pixelTolerance': 0,
                    'stopSingle': false,
                    'stopDouble': false
                },

                initialize: function(options) {
                    this.handlerOptions = OpenLayers.Util.extend(
                        {}, this.defaultHandlerOptions
                    );
                    OpenLayers.Control.prototype.initialize.apply(
                        this, arguments
                    ); 
                    this.handler = new OpenLayers.Handler.Click(
                        this, {
                            'click': this.trigger
                        }, this.handlerOptions
                    );
                }, 

                trigger: function(e) {
		    var lonlat = map.getLonLatFromPixel(e.xy);
		    brit = new OpenLayers.Projection("EPSG:900913");
		    google = new OpenLayers.Projection("EPSG:4326");

		    lonlatclone = lonlat.clone()
		    lonlatclone.transform(brit, google)
                    
                    console.log("You clicked near " + lonlatclone.lat + " N, " +
                                              + lonlatclone.lon + " E");

		    if (point_location==1){
			var s = document.getElementById(point_location_result_id);
			s.value = lonlatclone.lon+","+lonlatclone.lat;
			point_location=0;
			//TODO Add markers on click
		    }
                }

            	});

                map = new OpenLayers.Map ("map", {
                    controls: [
                        new OpenLayers.Control.Navigation({
				            dragPanOptions: {
				                enableKinetic: true
				            }
				        }),
                        new OpenLayers.Control.Attribution(),
                        new OpenLayers.Control.Zoom()
                    ],
                    maxExtent: new OpenLayers.Bounds(-20037508.34,-20037508.34,20037508.34,20037508.34),
                    maxResolution: 156543.0399,
                    numZoomLevels: 19,
                    units: 'm',
                    projection: new OpenLayers.Projection("EPSG:900913"),
                    displayProjection: new OpenLayers.Projection("EPSG:4326")
                });
                map.addControl(new OpenLayers.Control.LayerSwitcher());
                var osm = new OpenLayers.Layer.OSM.Mapnik('OSM');
		//var selectEt = new OpenLayers.Control.SelectFeature(osm, options_select);
		//map.addControl(selectEt);
                map.addLayer(osm);
                var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
		console.log("lonlat: "+lon+":"+lat);

		var markers = new OpenLayers.Layer.Markers( "Markers" );
		map.addLayer(markers);
		markers.addMarker(new OpenLayers.Marker(lonLat));

		var element = document.getElementById("my_place");
		if (typeof(element) != 'undefined' && element != null){
			element.value = lon+","+lat;
		}
		
                map.setCenter (lonLat, zoom);

		//Activate click event to point a location from the map
		var click = new OpenLayers.Control.Click();
                map.addControl(click);
                click.activate();
                
		var geojson_format = new OpenLayers.Format.GeoJSON({
                    'internalProjection': new OpenLayers.Projection("EPSG:900913"),
                    'externalProjection': new OpenLayers.Projection("EPSG:4326")
                });

		var features = getFeaturesForPopup(map.getProjectionObject())
		var tripfeatures = "";//getTripFeaturesForPopup(map.getProjectionObject())

		//Popup for trips
		if(trips.length > 0){
			trip_feature = new OpenLayers.Layer.Vector("Trips", 
			{
			  styleMap:  new OpenLayers.StyleMap(style),
			  rendererOptions: { zIndexing: true },
			  eventListeners:{
			    'featureselected':function(evt){
				var feature = evt.feature;
				var popup = new OpenLayers.Popup.FramedCloud("popup",
				    //feature.geometry.getBounds().getCenterLonLat(),
                                    OpenLayers.LonLat.fromString(feature.geometry.getVertices()[0].toShortString()),
				    null,
				    getTripSegmentTemplate(feature),//get_template_trip(feature),
				    null,
				    true, onPopupCloseTrip
				);
				feature.popup = popup;
				map.addPopup(popup);
			    },
			    'featureunselected':function(evt){
				var feature = evt.feature;
				map.removePopup(feature.popup);
				feature.popup.destroy();
				feature.popup = null;
			    }
			  }
			});
			//trip_feature.addFeatures(tripfeatures);
		}

		//Popups for places
		if(features.length > 0){
			locations = new OpenLayers.Layer.Vector("Places",{ rendererOptions: { zIndexing: true },
			  eventListeners:{
			    'featureselected':function(evt){
				var feature = evt.feature;
				var popup = new OpenLayers.Popup.FramedCloud("popup",
				    OpenLayers.LonLat.fromString(feature.geometry.toShortString()),
				    null,
				    get_template(feature),
				    null,
				    true, onPopupClose
				);
				feature.popup = popup;
				map.addPopup(popup);
			    },
			    'featureunselected':function(evt){
				var feature = evt.feature;
				map.removePopup(feature.popup);
				feature.popup.destroy();
				feature.popup = null;
			    }
			  }
			});

			locations.addFeatures(features);

			// create the select feature control
			var selector = new OpenLayers.Control.SelectFeature(locations,{
				//hover:true,
				autoActivate:true
			}); 

			function onPopupClose(event) {
			    selector.unselectAll();
			}

			map.addControl(selector);	
		}


                for (var i = 0; i < trips.length; i++) {
                
		    //Layers for travel mode segments and locations
	       	    map.addLayer(vehicle);
	       	    map.addLayer(bike);
	       	    map.addLayer(unknown);
	            map.addLayer(walking);
	            map.addLayer(still);

		    //Trip layer for one trip
	       	    map.addLayer(trip_feature);
		    var trip_selector = new OpenLayers.Control.SelectFeature(trip_feature,{
			autoActivate:true
		    }); 

		    function onPopupCloseTrip(event) {
			trip_selector.unselectAll();
		    }
	       	    map.addControl(trip_selector);

		    var vecLyr = map.getLayersByName('Trips')[0];
		    //map.raiseLayer(vecLyr, map.layers.length);
		    map.setLayerIndex(vecLyr, 0);
	        	    
		    var featureCollection = trips[i];

		    var geojson = geojson_format.read(featureCollection)
		    trip_feature.addFeatures(geojson);

                    var features = featureCollection.features;

		    if (features.length > 0) {
	                for (var j = 0; j < features.length; j++) {
	                	var feature = features[j];
	                	var activity = feature.properties.activity;

				if(activity == "on-foot"){
					walking.addFeatures(geojson_format.read(feature));
				} else if(activity == "still"){
					still.addFeatures(geojson_format.read(feature));
				} else if(activity == "in-vehicle"){
					vehicle.addFeatures(geojson_format.read(feature));
				} else if(activity == "on-bicycle"){
					bike.addFeatures(geojson_format.read(feature));
				} else {
					unknown.addFeatures(geojson_format.read(feature));
				}
			}
		    } else {
				//console.log("Fucked up: " + features.length);
				//console.log(featureCollection);
		    }
		}
		//Adding places on top
		if(locations) {
		    map.addLayer(locations);
		}
		
            }
            //$('#key').draggable();
		
	        var signInCallback = function (result) {
                if(result['g-oauth-window']) {
		            $('#code').attr('value', result['code']);
		            $('#at').attr('value', result['access_token']);
		            $('#google-plus').submit();
                }
		    };

            (function() {
                var po = document.createElement('script');
                po.type = 'text/javascript'; po.async = true;
                po.src = 'https://apis.google.com/js/client:plusone.js?onload=start';
                var s = document.getElementsByTagName('script')[0];
                s.parentNode.insertBefore(po, s);
            })();
            
            function get_csrf_token(){
		        return $("input[name='csrfmiddlewaretoken']").val();
		    }
