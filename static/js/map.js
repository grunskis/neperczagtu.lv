var map;
var marker;

function initialize() {
    var location;

    var options = {
        zoom: 15,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        options: {
            mapTypeControlOptions: {
                style: google.maps.MapTypeControlStyle.DROPDOWN_MENU
            }
        }
    };
    
    map = new google.maps.Map(document.getElementById("map"), options);

    var latitude = $('#lat').val() || $('#lat').text();
    var longitude = $('#lng').val() || $('#lng').text();
    var viewonly = $('#viewonly') && $('#viewonly').text() == "yes";

    if (latitude && longitude) {
        location  = new google.maps.LatLng(latitude, longitude);

        placeMarker(location);
    } else {
        var address = $('#location').val();

        var geocoder = new google.maps.Geocoder();
        geocoder.geocode({'address': address}, function(results, status) {
            if (status == google.maps.GeocoderStatus.OK) {
                location = results[0].geometry.location;

                placeMarker(location);
            }
        });
    }

    if (!viewonly) {
        google.maps.event.addListener(map, 'click', function(event) {
            placeMarker(event.latLng);
        });
    }
}
    
function placeMarker(location) {
    if (marker != null) {
        // clear old marker
        marker.setMap(null);
        marker = null;
    }
    
    marker = new google.maps.Marker({
        position: location, 
        map: map
    });

    map.setCenter(location);

    document.getElementById('lat').value = location.lat();
    document.getElementById('lng').value = location.lng();
}

$(document).ready(function() {
    initialize();
});
