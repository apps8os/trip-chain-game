var new_places = null;

function do_place_data_analysis(){
    console.log("do_place_data_analysi");
    var csrf = get_csrf_token();
    var par_uid = $('#uid').val();

    $('#get_places').attr("disabled", true);
    $.ajax({
	type: "POST",
	url: "places/",
	data: { csrfmiddlewaretoken:csrf, uid:par_uid }
    })
    .done(function( ret ) {
   	console.log("Saved "+ret);
	new_places = ret;
	//console.log(new_places);
	$('#get_places').attr("disabled", false);
    });
}

function do_save_location_type(address){
    console.log("fuck");
    var par_uid = $('#uid').val();
    var par_address = address;
    var par_type = $('#location_type').val();
    var csrf = get_csrf_token();

    console.log("uid: "+par_uid);

    if(par_uid != "undefined"){
	$('#location_type').attr("disabled", true);
        $.ajax({
	   type: "POST",
	   url: "save_location/",
	   data: { csrfmiddlewaretoken:csrf, uid:par_uid, address:par_address, type:par_type }
	   //data: { uid: par_uid, address: par_address, type: par_type }
        })
        .done(function( ret ) {
	    if(ret == 1){
   	    console.log("Saved");
	    } else {
		console.log("Not saved");
	    }
        });
        $('#location_type').attr("disabled", false);
    } else {
	console.log("Couldn't find uid: "+par_uid);
    }
}

