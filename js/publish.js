var lp = new locationPicker('map', {
    setCurrentPosition: true, // You can omit this, defaults to true
  }, {
    zoom: 15 // You can set any google map options here, zoom defaults to 15
  });

google.maps.event.addListener(lp.map, 'idle', function (event) {
// Get current location and show it in HTML
var location = lp.getMarkerPosition();
onIdlePositionView.innerHTML = 'The chosen location is ' + location.lat + ',' + location.lng;
document.getElementById('location').value = location;
});