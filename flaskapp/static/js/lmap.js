function displayTrailsLMAP(trail_points, map)
{

  function plotTrails(tp){
    const line_colors = ['#fc8d59','#e34a33','#b30000','#969696','#636363','#252525'];
    for (var i = 0; i < tp.length; i++){
        var polyline = L.polyline(tp[i]);
        polyline.setStyle( {'color' : "#000000",
                            'dashArray' :'5,5,1,5',
                            'weight':2 });
        polyline.addTo(map);
    }
  }

  if (trail_points.length == 0){
    function getTrails() {
      return new Promise(function(resolve,reject) {
        $.ajax(
          {
            type : 'POST',
            url : "/button/display_trails",
            contentType: "application/json;charset=UTF-8",
            dataType:'json',
            data    : JSON.stringify( { "val" : 0 } ),
            success : function(data)
            {
              if (data !=null)
              {
                resolve(data);
              }
            }, /*success : function() {}*/
            error : function(err){
              reject(err);
            } /* error */
          });/*$.ajax*/
       });
     } /* get Trails */

     getTrails().then(function(data) {
       trail_points = data;
       plotTrails(trail_points);
       console.log("PLOT TP AFTER AJAX:");
     }).catch(function(err) {
       console.log("ERROR IN GET TRAILS", err);
     })

  } else {
    console.log("Skipping AJAX call in get trails");
    plotTrails(trail_points);
  }


}
