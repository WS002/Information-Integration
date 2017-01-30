var heatMapController = function() {
	var heatMap = {};
	heatMap.kernelSize = 3;
	heatMap.sigma = 1.0;
	heatMap.data = {};
	heatMap.leafletMap;
	heatMap.canvasOverlay = L.canvasOverlay();	

	// Private variables
	var width;
	var height;
	var size;	
	var venuesDistribution = {};
	var venuesLocation = {};
	var maxValue;
	var minValue;
	var canvasContext;

	heatMap.setLeafletMap = function(_) {
		heatMap.leafletMap = _;
		heatMap.canvasOverlay.addTo(heatMap.leafletMap);
		heatMap.leafletMap.on('click', onClickVenue);
		return heatMap;
	}

	heatMap.setKernelSize = function(_) {	
		heatMap.kernelSize = _;
		return heatMap;
	}

	heatMap.setSigma = function(_) {	
		heatMap.sigma = _;
		return heatMap;
	}

	heatMap.setData = function(_) {
		heatMap.data = _;
		return heatMap;
	}



	function drawingOnCanvas(canvasOverlay, params) {
		canvasContext = params.canvas.getContext('2d');
		canvasContext.clearRect(0, 0, params.canvas.width, params.canvas.height);

		width = params.canvas.width;
		height = params.canvas.height;
		size = width * height * 4;	    

		var venueData = params.options.data;
		var count = 0;
		venuesLocation = {}; 

		for (var i = 0; i < venueData.length; i++) {			
			// canvas drawing goes here
			var lat = parseFloat(venueData[i]['location']['lat']);
			var lng = parseFloat(venueData[i]['location']['lng']);			

			if (params.bounds.contains([lat, lng])) {
			    dot = canvasOverlay._map.latLngToContainerPoint([lat, lng]);
			    count += 1;
			    var dotAsPixel = 4 * dot.x +  dot.y * width * 4;
			    // Save to venuesLocation
			    venuesLocation[dotAsPixel] = {'venueData':venueData[i], 'coordinates': [lat,lng] };
			  		
			   }

		}

		
			var heatmapObject = calculateHeatMap();
			venuesDistribution = heatmapObject['venuesDistribution'];
			maxValue = heatmapObject['maxValue'];
			minValue = heatmapObject['minValue'];
		
			
			drawHeatMap();

			
			
	};

	function onClickVenue(e) {
		    //console.log("X " + e.containerPoint.x);
		    //console.log("Y " + e.containerPoint.y);	
		    var dotAsPixel = 4 * e.containerPoint.x +  e.containerPoint.y * width * 4;
		    //Scan all directions to retrieve venues in the vicinity
		    var foundVenues = [];
	        
		    var movePositions = Math.floor(heatMap.kernelSize / 2);	
		    if( !( dotAsPixel < width * 4 * movePositions) && 
			!(dotAsPixel > size - (width * 4 * movePositions)) &&  
			!(dotAsPixel % (4*width) < 4 + (4 * (movePositions-1) ) ) && 
			!( dotAsPixel % (4*width) >= (4*width - 1) - 4*(movePositions-1))  
		       )
		      {	
			var kernelStart = dotAsPixel - (movePositions*4) - (movePositions * width * 4);
			for (var kX = kernelStart, xCounter = 0; xCounter < heatMap.kernelSize; kX+=4, xCounter++) {
				for(var kY = kX, yCounter = 0; yCounter < heatMap.kernelSize; kY+=width*4, yCounter++) {
					var venue = venueAtLocation(kY);
					if(venue['hereNow']['count'] > -1)
					{	
						foundVenues.push(venue);						
					}

					//////////////////////////// Scanning part //////////////////////////////

					var direction = [0,0];
					// Top border
					if (yCounter == 0) 
					{

						// Scan Top pixels
						direction = [0, -1];						
						foundVenues.push.apply(foundVenues, scanPixels(kY, direction, heatMap.kernelSize-1)['venues']);

						// Top left corner
						if (xCounter == 0) 
						{
							// Scan diagonal
							direction = [-1, -1];
							foundVenues.push.apply(foundVenues, scanPixels(kY, direction, heatMap.kernelSize-1)['venues']);
						}
						// Top right corner
						if (xCounter == heatMap.kernelSize - 1)
						{
							// Scan diagonal
							direction = [1, -1];
							foundVenues.push.apply(foundVenues, scanPixels(kY, direction, heatMap.kernelSize-1)['venues']);
					
			
						}

				
					}

					// Bottom border
					if (yCounter == heatMap.kernelSize -1) 
					{
						// Scan bottom pixels 
						direction = [0, 1];
						foundVenues.push.apply(foundVenues, scanPixels(kY, direction, heatMap.kernelSize-1)['venues']);
						// Bottom left corner
						if (xCounter == 0) 
						{
							// Scan diagonal
							direction = [-1, 1];
							foundVenues.push.apply(foundVenues, scanPixels(kY, direction, heatMap.kernelSize-1)['venues']);
						}
						// Bottom right corner
						if (xCounter == heatMap.kernelSize - 1)
						{
							// Scan diagonal
							direction = [1, 1];
							foundVenues.push.apply(foundVenues, scanPixels(kY, direction, heatMap.kernelSize-1)['venues']);
					
			
						}
			
				
					}

			
			
					// Right border
					if (xCounter == heatMap.kernelSize -1) 
					{							

						// Scan pixels to the right
						direction = [1, 0];
						foundVenues.push.apply(foundVenues, scanPixels(kY, direction, heatMap.kernelSize-1)['venues']);
					
					}
	
					// Left border
					if (xCounter == 0) 
					{
			
						// Scan pixels to the left
						direction = [-1, 0];
						foundVenues.push.apply(foundVenues, scanPixels(kY, direction, heatMap.kernelSize-1)['venues']);
					}

		
				
		//////////////////////////// END OF Scanning part //////////////////////////////	
					
			}//End first for
				}//End second for

		      }//End if				
	
		    $('#mapMenu').empty();
		   
		    for(var i = 0; i < foundVenues.length; i++)
		    {
			 var infoString = '';
			var currentVenue = foundVenues[i];
			infoString = currentVenue['name'] + " with category " + currentVenue['category'] + " has overall " + currentVenue['hereNow']['count'] + " people checked in.";
				
				
			 $('#mapMenu').append($('<div>', {				
				id: 'info',
				venue: currentVenue['id']				
			    }));

			 $('div[venue='+currentVenue['id']+']').append('<h2>'+infoString+'</h2>');

			 if(currentVenue['description'] != '' && currentVenue['description'] != null) {
				$('div[venue='+currentVenue['id']+']').append('<h2>Description</h2>');
				$('div[venue='+currentVenue['id']+']').append($('<div>', {
					text: currentVenue['description']
				}));
			}

		    }
		   
	}



	function calculateGaussianKernel(x, y)
	{
		normalizationFactor = 1.0/2.0*heatMap.sigma*heatMap.sigma*Math.PI;
		gaussian = Math.exp(-(x*x + y*y)/(2.0*heatMap.sigma*heatMap.sigma));
		return normalizationFactor * gaussian;
	}


	function venueAtLocation(key)
	{
		if (!(key.toString() in venuesLocation)) {
			return {'hereNow': {'count':-1}};
		}else {
			return venuesLocation[key]['venueData'];
			//return {'hereNow': {'count':1}};
																																																																																																							 //
		}
	}


	heatMap.draw = function() {
		heatMap.canvasOverlay.params({data: heatMap.data}).drawing(drawingOnCanvas).redraw();

		return heatMap;

	}
	
	
	function scanPixels(currentPixel, direction, count)
	{
		
		var xScan = direction[0] * 4;
		var yScan = direction[1] * width * 4;
		var countSum = 0;
		var venues = [];
		
		for(var k = 0; k < count; k++)
		{
			currentPixel += xScan + yScan;							
			
			venue = venueAtLocation(currentPixel);
			if(venue['hereNow']['count'] > -1) 
			{
				countSum += venue['hereNow']['count'];
				venues.push(venue);
			}
			

			if( Math.abs(direction[0]) + Math.abs(direction[1]) > 1 )
			{
				// Diagonal scan => scan pixels around the diagonal pixel					
															

				// Scan vertical pixels
				elements = scanPixels(currentPixel, [0, direction[1]], count - k - 1);
				countSum += elements['countSum'];
				venues.push.apply(venues, elements['venues']);
				// Scan horizontal pixels
				elements = scanPixels(currentPixel, [direction[0], 0], count - k - 1);
				countSum += elements['countSum'];
				venues.push.apply(venues, elements['venues']);				
				
			}

			
			
		}

		return {'venues':venues, 'countSum': countSum};
	}




function calculateHeatMap() {		
	var movePositions = Math.floor(heatMap.kernelSize / 2);		
	maxValue = 0.0;
	minValue = Infinity;
	venuesDistribution = {}
	for (var i in venuesLocation) {
		
		//console.log(i);
		var venueCoordinates = venuesLocation[i]['coordinates'];
		
		i = parseInt(i, "10");
		// if i not part of bottom border row(s) ( based on kernel size, if kernelSize > 3, border rows > 1)
		// if i not part of top border row(s)
		// if i not part of left column(s)
		// if i not part of right column(s)
		if( !( i < width * 4 * movePositions) && 
		    !(i > size - (width * 4 * movePositions)) &&  
		    !(i % (4*width) < 4 + (4 * (movePositions-1) ) ) && 
		    !( i % (4*width) >= (4*width - 1) - 4*(movePositions-1))  
		   )
		{			
			//var red = data[i];
			//var green = data[i + 1];
			//var blue = data[i + 2];
			//var alpha = data[i + 3];
		

			var gaussianSum = 0.0;	
	
			// Iterate through the Gaussian kernel
			var kernelStart = i - (movePositions*4) - (movePositions * width * 4);
			for (var kX = kernelStart, xCounter = 0; xCounter < heatMap.kernelSize; kX+=4, xCounter++) {
				for(var kY = kX, yCounter = 0; yCounter < heatMap.kernelSize; kY+=width*4, yCounter++) {

				
					gaussian = calculateGaussianKernel(xCounter - movePositions, yCounter - movePositions);
					
					var venue = venueAtLocation(kY);
					if(venue['hereNow']['count'] > -1)
					{	
						gaussianSum += gaussian * venue['hereNow']['count'];					
					}
					
				
				
		//////////////////////////// Scanning part //////////////////////////////

					var direction = [0,0];
					// Top border
					if (yCounter == 0) 
					{

						// Scan Top pixels
						direction = [0, -1];
						gaussianSum += gaussian * scanPixels(kY, direction, heatMap.kernelSize-1)['countSum'];
					
	
						// Top left corner
						if (xCounter == 0) 
						{
							// Scan diagonal
							direction = [-1, -1];
							gaussianSum += gaussian * scanPixels(kY, direction, heatMap.kernelSize-1)['countSum'];
						}
						// Top right corner
						if (xCounter == heatMap.kernelSize - 1)
						{
							// Scan diagonal
							direction = [1, -1];
							gaussianSum += gaussian * scanPixels(kY, direction, heatMap.kernelSize-1)['countSum'];
						
				
						}

					
					}

					// Bottom border
					if (yCounter == heatMap.kernelSize -1) 
					{
						// Scan bottom pixels 
						direction = [0, 1];
						gaussianSum += gaussian * scanPixels(kY, direction, heatMap.kernelSize-1)['countSum'];
						// Bottom left corner
						if (xCounter == 0) 
						{
							// Scan diagonal
							direction = [-1, 1];
							gaussianSum += gaussian * scanPixels(kY, direction, heatMap.kernelSize-1)['countSum'];
						}
						// Bottom right corner
						if (xCounter == heatMap.kernelSize - 1)
						{
							// Scan diagonal
							direction = [1, 1];
							gaussianSum += gaussian * scanPixels(kY, direction, heatMap.kernelSize-1)['countSum'];
						
				
						}
				
					
					}

				
				
					// Right border
					if (xCounter == heatMap.kernelSize -1) 
					{							

						// Scan pixels to the right
						direction = [1, 0];
						gaussianSum += gaussian * scanPixels(kY, direction, heatMap.kernelSize-1)['countSum'];
						
					}
		
					// Left border
					if (xCounter == 0) 
					{
				
						// Scan pixels to the left
						direction = [-1, 0];
						gaussianSum += gaussian * scanPixels(kY, direction, heatMap.kernelSize-1)['countSum'];
					}

			
					
		//////////////////////////// END OF Scanning part //////////////////////////////	
				
				}//End of vertical kernel index
			
			}// //End of horizontal kernel index
		
			if(gaussianSum > maxValue)
			 	maxValue = gaussianSum;
			if(gaussianSum < minValue)
				minValue = gaussianSum;

			
			venuesDistribution[venueCoordinates[0]+':'+venueCoordinates[1]] = gaussianSum;

		}// End of canvas border checking
		//break;
	}// End of i for loop

	console.log("Heat map ready");
	console.log("Max value = " + maxValue);
	console.log("Min value = " + minValue);

	return {'venuesDistribution' : venuesDistribution, 'maxValue': maxValue, 'minValue': minValue };
}

	function drawHeatMap() {

		//var colorScheme = ['rgba(229,245,249,0.5)','rgba(153,216,201,0.5)','rgba(44,162,95,0.5)','rgba(254,230,206,0.5)','rgba(253,174,107,0.5)','rgba(230,85,13,0.5)'];
		var colorScheme = ['rgba(228,84,47,0.3)','rgba(226,172,48,0.3)','rgba(192,224,50,0.5)','rgba(108,223,52,0.3)','rgba(55,220,163,0.3)','rgba(64,52,223,0.3)']
		
    		canvasContext.clearRect(0, 0, width, height);
		for (var venue in venuesDistribution) {
			
			coordinates = venue.split(":");
			var lat = parseFloat(coordinates[0]);
			var lng = parseFloat(coordinates[1]);
			if (heatMap.leafletMap.getBounds().contains([lat, lng])) {
				
				// Linear interpolation, map minValue to 0, maxValue to colorScheme.length - 1
				var x0 = minValue;
				var x1 = maxValue; 
				var y0 = 0;
				var y1 = colorScheme.length - 1;
				var x = venuesDistribution[venue];
				if(x == maxValue)
					console.log(venue);					
				colorIndex = y0 + ( (x - x0) * ( (y1 - y0) / (x1 - x0)  ) );

				if(isNaN(colorIndex))
					colorIndex = 0;
				var currentColor = colorScheme[colorScheme.length-1-Math.floor(colorIndex)];

				var dot = heatMap.canvasOverlay._map.latLngToContainerPoint([lat, lng]);
				canvasContext.fillStyle = currentColor;
				canvasContext.beginPath();			
				canvasContext.arc(dot.x, dot.y, heatMap.kernelSize, 0, Math.PI * 2);
				//canvasContext.rect(dot.x, dot.y, kernelSize, kernelSize)
				canvasContext.fill();
				canvasContext.closePath();	
				
			}
		 }


	}	


	return heatMap;
		

}
