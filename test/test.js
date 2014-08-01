function _(id) {
	return document.getElementById(id);
}

var response = JSON.parse('{"trends": [{"name": "#EvetUyumuyorum\u00c7\u00fcnk\u00fc", "value": 980}, {"name": "GazzedeSoyk\u0131r\u0131m Yap\u0131l\u0131yor", "value": 940}, {"name": "#Gelecekten\u0130ste\u011fim", "value": 870}, {"name": "ZilletinVekili Hakan\u015e\u00fck\u00fcr", "value": 790}, {"name": "\u00d6mr\u00fcn\u00fczRamazan AhiretinizBayramOlsun", "value": 780}, {"name": "#BuGeceYine", "value": 780}, {"name": "#\u00c7a\u011flayandaZul\u00fcmVar", "value": 680}, {"name": "#direnkahkaha", "value": 590}, {"name": "G\u00fcn\u00fc MilliBirli\u011feY\u00fcr\u00fc", "value": 480}, {"name": "B\u00fclent Ar\u0131n\u00e7", "value": 450}, {"name": "#BayramdaBuTagKazand\u0131r\u0131r", "value": 440}, {"name": "AliSamiYen SonsuzaKadarKalbimizde", "value": 440}, {"name": "Sar\u0131LaciAileyiz Fenerbah\u00e7eEvimiz", "value": 370}, {"name": "FENERBAH\u00c7EliOlmayan NeBilsinSevday\u0131", "value": 330}, {"name": "#ErdoganaCByolundaBa\u015far\u0131lar", "value": 280}, {"name": "T\u00fcrkmenEline BayramGelmedi", "value": 270}, {"name": "T\u00fcrkmeneline BayramGelmedi", "value": 270}, {"name": "Soyk\u0131r\u0131mVar Aya\u011faKalk\u00dcmmet", "value": 270}, {"name": "#BayramdaMutluEdenTAG", "value": 230}, {"name": "Jet Fad\u0131l", "value": 210}, {"name": "#SendeBuBayramBirHuzurEviniZiyaretET", "value": 200}, {"name": "#Ke\u015fkeUyuyunca", "value": 190}, {"name": "#AhsarComYenilendi", "value": 190}, {"name": "#7yirmi5Bayram\u0131n\u0131z\u0131Kutlar", "value": 180}, {"name": "Atat\u00fcrk\u00e7\u00fcler Bayramla\u015f\u0131yor", "value": 180}, {"name": "Hayat SeninleG\u00fczel FENERBAH\u00c7EM", "value": 170}, {"name": "BJKd\u00fc\u015fman\u0131HadsizMilliyet \u00d6z\u00fcrDileULAN", "value": 170}, {"name": "#SeviyorumSeniKelAdam", "value": 160}, {"name": "#OyumuKullanacagimYSKengelOlma", "value": 160}, {"name": "MaviMarmara Gazzeye", "value": 160}, {"name": "Hakan \u015e\u00fck\u00fcr", "value": 150}, {"name": "#UgurKartalKazandirir", "value": 140}, {"name": "\u00c7e\u00e7enM\u00fclteciler Yaln\u0131zDe\u011fildir", "value": 140}, {"name": "The Hobbit", "value": 140}, {"name": "#UgurKartalveEmrePolatKazandirir", "value": 140}, {"name": "Yi\u011fithan Kaptan", "value": 130}, {"name": "T\u00fcm \u0130slam", "value": 120}, {"name": "#EmrePolatSiqer", "value": 120}, {"name": "#UgurKartalBuTagdaKazandirir", "value": 110}, {"name": "#xlargeclubdaebrupolat", "value": 100}, {"name": "#TaksimGoldClub", "value": 90}, {"name": "FENERBAH\u00c7ElilerRamazan Bayram\u0131n\u0131z\u0131Kutlar", "value": 80}, {"name": "#MaviGiyenAdamlaUyanT\u00fcrkiye", "value": 80}, {"name": "#CagdasDundar", "value": 80}, {"name": "#iibfmezunlarina40binkadro", "value": 70}, {"name": "#KimBuUgurKartal", "value": 70}, {"name": "#erdoganaoyvermeyin", "value": 60}, {"name": "#SametECEMveUgurKartalileKazaniyoruz", "value": 60}, {"name": "T\u00fcrkmenEline Bayramgelmedi", "value": 50}, {"name": "\u00dclk\u00fcc\u00fcHareket Hay\u0131rl\u0131BayramlarDiler", "value": 40}]}');

_("trends").innerHTML = null;

var flatColors = ["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#1abc9c", "#3498db", "#9b59b6"],
	flatdDarkerColors = ["#c0392b", "#d35400", "#f39c12", "#27ae60", "#16a085", "#2980b9", "#9b59b6"],
	colors = ["#b70908", "#bc6307", "#cab005", "#2f7626", "#449296", "#064771", "#bd2450"],
	colors2 = ["#004358", "#1F8A70", "#BEDB39", "#FFE11A", "#FD7400"];

var fill = d3.scale.category10();

var w = _("trends").offsetWidth,
	h = _("trends").offsetHeight;

var nodes = response.trends,
	maxNodeValue = nodes[0].value,
	radiusCoefficient = (1000 / w) * (maxNodeValue / 100);

console.log("radiusCoefficient: " + radiusCoefficient);

var force = d3.layout.force()
	.gravity(0.03)
	.charge(charge)
    .nodes(nodes)
    .size([w, h])
    .on("tick", tick)
    .start();

var svg = d3.select("#trends").append("svg")
	.attr("width", w)
	.attr("height", h);

var node = svg.selectAll(".node")
    .data(nodes)
  .enter().append("circle")
    .attr("class", "node")
    .attr("cx", function(d) { return d.x; })
	.attr("cy", function(d) { return d.y; })
	.attr("r", 0)
	.style("fill", function(d, i) { return assignColor(d, i); })
	.style("stroke", function(d) { return d3.rgb(d.color).darker(2); })
    .call(force.drag);

node.transition()
	.duration(1000)
	.attr("r", function(d) {
 		return d.value / radiusCoefficient;
	});

svg.style("opacity", 1e-6)
	.transition()
		.duration(1000)
		.style("opacity", 1);

$('circle').tipsy({ 
    gravity: 's', 
    html: true,
    fade: true, 
    fadeAnimationDuration: 200,
    offset: 30,
    title: function() {
    	var d = this.__data__;
    	return '<div class="tipsy-topic">' + d.name +'</div><span class="tipsy-time">' + d.value + ' min.</span>';
	}
});

function tick(e) {
	var k = -0.1 * e.alpha;
	nodes.forEach(function(o, i) {
		o.y += k;
	    o.x += k;
	});

	node.attr("cx", function(d) { return d.x; })
	    .attr("cy", function(d) { return d.y; });
}

function charge(d) {
	return -Math.pow(d.value / (radiusCoefficient * 2), 2.0) / 8;
}

function assignColor(d, i) {
	//d.color = colors2[4 - Math.floor(d.value / (maxNodeValue / 4))];
	d.color = fill(Math.floor(d.value / (maxNodeValue / 3)));
	return d.color;
}

function remove() {
	force.gravity(0.001).resume();

	node.transition()
		.duration(1000)
		.attr("r", 0)
	    .remove();

	svg.style("opacity", 1)
		.transition()
			.duration(1000)
			.style("opacity", 1e-6)
			.remove();
}

    function displayLoading() {
	jQuery("#trends").append('<div id="loading-area"><div class="spinner"></div></div>');
    }
    
    function hideLoading() {
	jQuery("#loading-area").remove();
    }
    