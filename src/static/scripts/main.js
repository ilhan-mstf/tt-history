var LAST_DAY = 0,
	LAST_WEEK = 1,
	LAST_MONTH = 2,
	DATE = 3,
	WOEID = 4,
	LIMIT = 50;

var history = LAST_DAY,
	woeid = 23424969,
	response;

var datepickerState = 0;

document.ready = function() {
	
	/* 
	 * initialize datepicker 
	 */
	jQuery("#datepicker").datepicker({ 
		dateFormat: "dd.mm.y",
		minDate: new Date(1373576400000), // 12 July 2013 Fri
		maxDate: new Date(),
		onSelect: function(date) {
			setHistory(this, DATE);
		}
	});
	jQuery("#datepicker").datepicker("setDate", new Date());
	
	/*
	 * initialize trends
	 */
	getTrends(history);
}

window.onerror = function() {
	_("trends").innerHTML = "Ooops! Something went wrong!"
}

if( !window.XMLHttpRequest ) 
	XMLHttpRequest = function() {
		try{ return new ActiveXObject("Msxml2.XMLHTTP.6.0") }catch(e){}
		try{ return new ActiveXObject("Msxml2.XMLHTTP.3.0") }catch(e){}
		try{ return new ActiveXObject("Msxml2.XMLHTTP") }catch(e){}
		try{ return new ActiveXObject("Microsoft.XMLHTTP") }catch(e){}
		throw new Error("Could not find an XMLHttpRequest alternative.")
	};

function _(id) {
	return document.getElementById(id);
}

function getTrends(loadingId) {
	
	// create url
	var pathArray = document.URL.split('/');
	var url = pathArray[0] + "//"  + pathArray[2] + "/rpc?woeid=" + woeid;
	
	if (history == DATE) {
		startDate = Math.floor(jQuery("#datepicker").datepicker("getDate").getTime() / 1000);
		endDate = startDate + 86400;
		url += "&timestamp=" + startDate + "&end_timestamp=" + endDate;
	} else {
		url += "&history=" + getHistoryText();
	}
	
	url += "&limit=" + LIMIT;
	
	// make call
	var http_request = new XMLHttpRequest();
	http_request.open("GET", url, true);
	http_request.onreadystatechange = function() {
		if (http_request.readyState == 4 && http_request.status == 200) {
			onSuccess(http_request.responseText);
		} else if (http_request.readyState == 4 && http_request.status != 200) {
			onFailure();
		}
	    // hide loading.gif
		if (http_request.readyState == 4)
			_("l"+loadingId).style.display = 'none';
	}

	http_request.send(null);
	console.log(url);
	
	// display loading.gif
	_("l"+loadingId).style.display = 'inline-block';
}


function onSuccess(responseText) {
	
	// parse responseText
    try {
    	response = JSON.parse(responseText);
    } catch (e) {
    	response = responseText;
    }

    if (response == "") {
    	_("trends").innerHTML = "YOU SHOULD ENTER VALID INPUT!";
    	return;
    }
    
    if (response.trends.length == 0) {
    	_("trends").innerHTML = "NO RECORD! PLEASE SELECT A DATE AFTER JULY, 12.";
    	return;
    }
    
    drawTrends();
}

function onFailure() {
	_("trends").innerHTML = "YOU CRASHED IT!"
}

function drawTrends() {
	
	_("trends").innerHTML = null;
	
	var w = _("trends").offsetWidth,
		h = _("trends").offsetHeight,
		format = d3.format(",d");

	var bubble = d3.layout.pack()
		.sort(null)
		.size([w, h]);

	var vis = d3.select("#trends").append("svg")
		.attr("width", w)
		.attr("height", h)
		.attr("class", "bubble");
	
	var filter = vis.append("svg:defs")
	  .append("svg:filter")
	    .attr("id", "dropshadow")
	    .attr("height", "130%");
	
	filter.append("svg:feGaussianBlur")
      .attr("in", "SourceAlpha")
      .attr("stdDeviation", 2);
	
	filter.append("svg:feOffset")
	  .attr("dx", 0)
	  .attr("dy", 2)
	  .attr("result", "offsetblur");
	
	var merge = filter.append("svg:feMerge");
	merge.append("feMergeNode");
	merge.append("feMergeNode")
	    .attr("in", "SourceGraphic");
	
	var node = vis.selectAll("g.node")
		.data(bubble.nodes({children: response.trends})
		.filter(function(d) { return !d.children; }))
	    .enter().append("g")
	    .attr("class", "node")
	    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
	
	node.append("circle")
	    .attr("r", function(d) { return d.r; })
		.on("mouseover", function(){d3.select(this).style("filter", "url(#dropshadow)");})
	    .on("mouseout", function(){d3.select(this).style("filter", "");});
	
	$('circle').tipsy({ 
	    gravity: 's', 
	    html: true,
	    fade: true, 
	    offset: 30,
	    title: function() {
	    	var d = this.__data__;
	    	return '<div class="tipsy-topic">' + d.name +'</div><span class="tipsy-time">' + d.value + ' min.</span>';
		}
	});
}

function setHistory(node, h) {
	if (history != h || h == DATE) {
		history = h;
		getTrends(history);
		
		// change style
		changeHistoryBtnStyle(node, h);
	}
	return false;
}

function setWoeid(node, r) {
	if (woeid != r) {
		woeid = r;
		getTrends(WOEID);
		
		// change style
		changeRegionBtnStyle(node);
	}
	return false;
}

function setDateText(date) {
	if (date)
		_("dateText").innerHTML = jQuery("#datepicker").datepicker("getDate").toDateString();
	else
		_("dateText").innerHTML = "select a date";
}

function changeRegionBtnStyle(node) {
	$('nav a').removeClass('current');
	$(node).addClass('current');
}

function changeHistoryBtnStyle(node, type) {
	if (type == DATE) {
		setDateText(true);
		toggleDatepicker();
		$('.btn').removeClass('active');
		$('#datepickerBtn').addClass('active');
	} else if (node) {
		datepickerState = true;
		toggleDatepicker();
		setDateText(null);
		$('.btn').removeClass('active');
		$('#datepickerBtn').removeClass('datepicker-open');
		$(node).addClass('active');
	}
}

function toggleDatepicker() {
	if (datepickerState) {
		$('#datepicker').slideUp();
		$('#datepickerBtn').removeClass('datepicker-open');
	} else {
		$('#datepicker').slideDown();
		$('#datepickerBtn').addClass('datepicker-open');
	}
	datepickerState = !datepickerState;
	return false;
}

function getHistoryText() {
	if (history == LAST_DAY) {
		return "ld";
	} else if (history == LAST_WEEK) {
		return "lw";
	} else if (history == LAST_MONTH) {
		return "lm";
	}
}
