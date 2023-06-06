function plotPoints(latitudes, longitudes, siteno, site_names) {
    // Initialize the map
    var map = L.map('map').setView([-38.2, 146.533], 13);
    
    var markers = L.markerClusterGroup();

    // Add the base tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 18,
    }).addTo(map);


    // Plot the markers
    for (var i = 0; i < latitudes.length; i++) {
        var marker = L.marker([latitudes[i], longitudes[i]]).addTo(map);
        marker.bindPopup('<b>Siteno:</b> ' + siteno[i] + '<br><b>Site Name:</b> ' + site_names[i]);
        markers.addLayer(marker);

    }

    map.addLayer(markers);
}

