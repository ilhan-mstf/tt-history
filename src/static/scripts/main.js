/*! Copyright (c) 2013 Mustafa İlhan released under the MIT license */
(function() {

  var LAST_DAY = 0,
    LAST_WEEK = 1,
    LAST_MONTH = 2,
    DATE = 3,
    WOEID = 4,
    LIMIT = 50;

  var history = LAST_DAY,
    woeid = 1,
    response;

  var datepickerState = 0,
    stopInitialAnimation = 0,
    activeTipsy = null;

  // Google Analytics events
  $('a, .btn').on('click', function() {
    ga('send', 'event', 'link', 'click', $(this).attr('id') || $(this).attr('class'));
  });

  window.onload = function() {

    /*
     * initialize date picker
     */
    $("#datepicker").datepicker({
      dateFormat: "dd.mm.y",
      minDate: new Date(1373576400000), // 12 July 2013 Fri
      maxDate: new Date(),
      onSelect: function(date) {
        setHistory(this, DATE);
      }
    });
    $("#datepicker").datepicker("setDate", new Date());

    /*
     * initialize trends
     */
    displayLoading();
    getTrends();

    /*
     * add moveToFront function to d3.js
     */
    d3.selection.prototype.moveToFront = function() {
      return this.each(function() {
        this.parentNode.appendChild(this);
      });
    };
  }

  window.onerror = function() {
    _("trends").innerHTML = "Ooops! Something went wrong!"
  }

  if (!window.XMLHttpRequest)
    XMLHttpRequest = function() {
      try {
        return new ActiveXObject("Msxml2.XMLHTTP.6.0")
      } catch (e) {}
      try {
        return new ActiveXObject("Msxml2.XMLHTTP.3.0")
      } catch (e) {}
      try {
        return new ActiveXObject("Msxml2.XMLHTTP")
      } catch (e) {}
      try {
        return new ActiveXObject("Microsoft.XMLHTTP")
      } catch (e) {}
      throw new Error("Could not find an XMLHttpRequest alternative.")
    };

  function _(id) {
    return document.getElementById(id);
  }

  function getTrends() {

    // create url
    var pathArray = document.URL.split('/');
    var url = pathArray[0] + "//" + pathArray[2] + "/rpc?woeid=" + woeid;

    if (history == DATE) {
      startDate = Math.floor(jQuery("#datepicker").datepicker("getDate")
        .getTime() / 1000);
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
      if (http_request.readyState == 4) {
        hideLoading();

        if (http_request.status == 200) {
          onSuccess(http_request.responseText);
        } else if (http_request.status == 503) {
          onFailure("Request limit exceeded. Try tomorrow! Or get in touch with me via @mustilica.");
          /* Show donation button */
          //$(".donation").show();
        } else {
          onFailure();
        }
      }
    }

    http_request.send(null);

    pauseInitialAnimation();
    displayLoading();
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
      _("trends").innerHTML = "NO RECORD! PLEASE PICK A DATE AFTER JULY, 12 2013.";
      return;
    }

    drawTrends();
    setCurrentChartExplanation();
    stopInitialAnimation = 0;
    setTimeout(startInitialAnimation, 3000);
  }

  function onFailure(msg) {
    _("trends").innerHTML = msg || "YOU CRASHED IT!"
  }

  function displayLoading() {
    $("#trends").empty().append('<span>Loading...</span><div id="loading-area"><div class="spinner"></div></div>');
  }

  function hideLoading() {
    $("#trends").empty()
  }

  /**
   * Draws chart
   */
  function drawTrends(callback) {
    currentChart.draw(callback);
  }

  /**
   * Removes chart
   */
  function removeTrends(callback) {
    currentChart.remove(callback);
  }

  /**
   * Initial animation.
   * Fired when site launched (after chart are drawn)
   */
  function startInitialAnimation(list, index) {
    try {
      if (stopInitialAnimation) {
        return;
      }
      if (!list) {
        list = $('circle');
      }
      if (typeof index == "undefined") {
        index = 0;
      }
      if (list[index]) {
        activeTipsy = $(list[index]).mouseover();
        setTimeout(function() {
          $(list[index]).mouseout();
          activeTipsy = null;
          startInitialAnimation(list, index + 1);
        }, 5000);
      }
    } catch (e) {
      // TODO: handle exception
    }
  }

  function pauseInitialAnimation() {
    if (activeTipsy) {
      activeTipsy.mouseout();
      stopInitialAnimation = 1;
      activeTipsy = null;
    }
  }

  /**
   * Set current chart explanation
   */
  function setCurrentChartExplanation(message) {
    var message = "Trending topics";

    if (history == LAST_DAY) {
      message += " within last 24 hours";
    } else if (history == LAST_WEEK) {
      message += " within last week";
    } else if (history == LAST_MONTH) {
      message += " within last month";
    } else {
      message += " on " + jQuery("#datepicker")
        .datepicker("getDate")
        .toDateString()
        .substring(4);
    }

    if (woeid == 1) {
      message += " in World";
    } else {
      message += " in Turkey";
    }

    $('#trends').prepend("<span>" + message + "</span>");
  }

  function setHistory(node, h) {
    if (history != h || h == DATE) {
      history = h;
      removeTrends(getTrends);

      // change style
      changeHistoryBtnStyle(node, h);
    }
    return false;
  }

  function setWoeid(node, r) {
    if (woeid != r) {
      woeid = r;
      removeTrends(getTrends);

      // change style
      changeRegionBtnStyle(node);
    }
    return false;
  }

  function setDateText(date) {
    if (date) {
      _("dateText").innerHTML = jQuery("#datepicker")
        .datepicker("getDate")
        .toDateString()
        .substring(4);
    } else {
      _("dateText").innerHTML = "pick a date";
    }
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

  /**
   * Charts
   */
  var charts = {
    bubbleChart: function() {

      var area = _("trends"),
        force,
        node,
        svg;

      return {
        draw: function() {
          // Clear draw area.
          area.innerHTML = null;

          var w = area.offsetWidth,
            h = area.offsetHeight;

          var nodes = response.trends,
            maxNodeValue = nodes[0].value,
            //fill = d3.scale.category10(),
            fill = d3.scale.ordinal().range(Math.random() >= 0.5 ? ['#bd0026', '#f03b20', '#fd8d3c', '#fecc5c', '#ffffb2'] : ['#253494', '#2c7fb8', '#41b6c4', '#a1dab4', '#ffffcc']),
            radiusCoefficient = (1000 / w) * (maxNodeValue / 50);

          force = d3.layout.force()
            .gravity(0.03)
            .charge(charge)
            .nodes(nodes)
            .size([w, h])
            .on("tick", tick).start();

          svg = d3.select("#trends").append("svg")
            .attr("width", w)
            .attr("height", h);

          node = svg.selectAll(".node").data(nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("cx", function(d) {
              return d.x;
            }).attr("cy", function(d) {
              return d.y;
            }).attr("r", 0).style("fill", function(d) {
              return assignColor(d);
            }).style("stroke", function(d, i) {
              return d3.rgb(d.color).darker(2);
            }).call(force.drag);

          node.transition()
            .duration(1000)
            .attr("r", function(d) {
              return d.value / radiusCoefficient;
            });

          svg.style("opacity", 1e-6)
            .transition()
            .duration(1000)
            .style("opacity", 1);

          // Tooltip for circles
          $('circle').tipsy({
            gravity: 's',
            html: true,
            fade: false,
            offset: 0,
            fadeAnimationDuration: 200,
            title: function() {

              // Control for initial animation
              pauseInitialAnimation();

              // Bring to front
              var sel = d3.select(this);
              sel.moveToFront();

              var d = this.__data__;
              return '<div class="tipsy-topic">' + d.name + '</div><span class="tipsy-time">' + pretifyDuration(d.value) + '</span>';
            }
          });

          function tick(e) {
            var k = -0.1 * e.alpha;
            nodes.forEach(function(o, i) {
              o.y += k;
              o.x += k;
            });

            node.attr("cx", function(d) {
              return d.x;
            }).attr("cy", function(d) {
              return d.y;
            });
          }

          function charge(d) {
            return -Math.pow(d.value / (radiusCoefficient * 2), 2.0) / 8;
          }

          function assignColor(d) {
            //console.log(d.value, maxNodeValue, Math.floor(d.value / (maxNodeValue / 5)));
            d.color = fill(Math.floor(d.value / (maxNodeValue / 5)));
            return d.color;
          }

          function pretifyDuration(value) {
            if (value == 0) {
              return "";
            } else if (value > 59) {
              return Math.floor(value / 60) + " h. " + pretifyDuration(value % 60);
            } else {
              return value + " min."
            }
          }

        },
        remove: function(callback) {
          force.gravity(0.001).resume();

          node.transition()
            .duration(1000)
            .attr("r", 0)
            .remove();

          svg.style("opacity", 1)
            .transition()
            .duration(1000)
            .style("opacity", 1e-6)
            .remove()
            .each("end", callback);
        }
      }
    }
  }

  var currentChart = charts.bubbleChart();

  /**
   * UI element bindings
   */
  jQuery("#trRegionBtn").click(function() {
    setWoeid(this, 23424969);
  });

  jQuery("#worldRegionBtn").click(function() {
    setWoeid(this, 1);
  });

  jQuery("#lastDayBtn").click(function() {
    setHistory(this, LAST_DAY);
  });

  jQuery("#lastWeekBtn").click(function() {
    setHistory(this, LAST_WEEK);
  });

  jQuery("#lastMonthBtn").click(function() {
    setHistory(this, LAST_MONTH);
  });

  jQuery("#datepickerBtn").click(function() {
    toggleDatepicker();
  });

})();

// TODO onresize
