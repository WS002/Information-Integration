var mainController = function() {
	var controller = {};
	controller.data = {};
	controller.leafletMap = null;
	controller.heatMapController = heatMapController();	


	controller.initMap = function() {
		var leafletMap = L.map('map', {
			center: [48.7758459, 9.182932100000016],
			zoom: 12
		});
		L.tileLayer('http://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
			attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
			subdomains: 'abcd',
			maxZoom: 22
		}).addTo(leafletMap);

		$('.leaflet-container').css('cursor','default');

		controller.leafletMap = leafletMap;
		controller.heatMapController.setLeafletMap(controller.leafletMap);
		return controller;
	}
	
       

	controller.getData = function()
	{			
		
			$.ajax({
			    url: "BackEnd/index.php?func=getVenues",
			    dataType: 'json',
			    success: function(data){ 
				console.log(data);				
				controller.data = data;
				controller.updateHeatMap();										
			    },
			    error: function(e){
				console.log(e);
			    }
			   
			});
		

	}	


	controller.updateHeatMap = function() {
		controller.heatMapController.setData(controller.data).setSigma(0.1).setKernelSize(3).draw();
	
	}

	

	

	return controller;
}
