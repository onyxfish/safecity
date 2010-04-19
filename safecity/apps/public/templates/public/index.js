var map;

function make_marker(point, html) {
    var marker = new GMarker(point);
    
    GEvent.addListener(marker, "click", function() {
        marker.openInfoWindowHtml(html);
    });
    
    return marker;    
}

$(document).ready(function() {
    if (GBrowserIsCompatible()) {
        map = new GMap2(document.getElementById("report_map"));
        map.setCenter(new GLatLng({{ map_center.0 }}, {{ map_center.1 }}), 14);
        map.setUIToDefault();
        
        {# Create a list of marker locations #}
        var reports = {{ reports_json|safe }};
        
        for (i = 0; i < reports.length; i++) {
            var pt = new GLatLng(reports[i]['lat'], reports[i]['lon']);
            var html = reports[i]["desc"];
            var marker = make_marker(pt, html);
            
            map.addOverlay(marker);
        }
    }
})