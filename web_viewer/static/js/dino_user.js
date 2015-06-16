/**
 *	Single User
 */
var date_format = d3.time.format("%Y-%m-%d %H:%M:%S");
var scale_x = d3.scale.linear();
scale_x.domain([0, 100]);
scale_x.range([0, 800]);

var scale_y = d3.scale.linear();
scale_y.domain([0, 100]);
scale_y.range([800, 0]);

var colors = colorbrewer.PuBuGn[9];
var time_scale = d3.time.scale();
var time_scale_aux = d3.time.scale();
var open_time = date_format.parse("2014-6-06 08:00:00");
var close_time = date_format.parse("2014-6-06 20:30:00");
time_scale_aux.domain([open_time, close_time]);
time_scale_aux.range([0,colors.length-1]);
var time_domain=d3.range(colors.length).map(function(i){return time_scale_aux.invert(i);});
time_scale.domain(time_domain);
time_scale.range(colors);

var svg = d3.select("#main_svg");
var scatter = svg.append("g");


function draw_guest(array) {
// parse times
	array.forEach(function (e, i, a) {
		e.time = date_format.parse(e.Timestamp);
	});


	function draw_point(above_lim) {
		scatter.selectAll(".dot").data(array.slice(0, above_lim)).enter().append("circle").attr("class", "dot")
				.attr("r", 6)
				.attr("cx", function (d) {
					return scale_x(d.X);
				})
				.attr("cy", function (d) {
					return scale_y(d.Y);
				})
				.attr("fill", function (d) {
					return time_scale(d.time);
				})
				.classed("checkin",function(d){return d.type == "check-in";})
				.append("title").text(function(d){return d.Timestamp});
	}

	var i = 0;
	d3.timer(function () {
		d3.select("#clock").text(array[i].time.toLocaleTimeString());
		draw_point(i);
		i += 1;
		if (i >= array.length) {
			console.log("done");
			d3.select("#show_guest_button").attr("disabled", null);
			return true;
		}
		return false;
	});

}

function read_user() {
	var userId;
	var x=d3.select("#subjects_list").selectAll("input").filter(function(){return this.checked})[0];
    var guests = x.map(function(i){return i.value});
    
    if (guests.length > 0) {
    	userId = guests[0].split('-')[0];
    }
    else{
		userId = document.getElementById('userId').value;
    }

    scatter.selectAll(".dot").remove();
	console.log("reading user: " + userId);
	d3.json("distance?id="+userId, function (e, d) {
		document.getElementById('userDistance').textContent = 'The distance walked by the user was: ' + d.response;
	});
	d3.json("data?id="+userId, function (e, d) {
		draw_guest(d.array);
	});
	
}

d3.select("#show_user_path").on("click", read_user);

/*
	Checkins
*/

function get_checkins(){
	var g_data;

	d3.select("#subjects_list").selectAll("div").remove();
	var checkIns = document.getElementById('checkInNumber').value;
	var url="checkins?num="+checkIns;
	d3.json(url,function(data){
		g_data = [];
		for (var key in data.checkins.number) {
			g_data.push(key + '-' + data.checkins.number[key]);
		}
		
		var labels=d3.select("#subjects_list").selectAll("div").data(g_data).enter()
		.append("div").classed("checkbox",true)
		.append("label");

		labels.append("input").attr("type","checkbox").attr("value", function(d){return d});
		labels.append("spam").text(function(d){return d});

	})
}

d3.select("#show_less_check_in").on("click",get_checkins);