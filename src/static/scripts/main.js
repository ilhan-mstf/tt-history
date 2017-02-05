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
    activeTooltip = null;

  // Google Analytics events
  $('a, .btn').on('click', function() {
    // TODO id yerine datatype mı kullansam.
    ga('send', 'event', 'link', 'click', $(this).attr('id') || $(this).attr('class'));
  });

  $(document).ready(function() {
    var trends = $('#trends');
    if ($(window).width() < $(window).height()) {
      trends.height($(window).height() - 200);
    } else {
      trends.height($(window).height() - 60);
    }

    responsiveUtils();
  });

  $(window).on('load', function() {

    // TODO datapicker initialization.

    // coming soon tooltip for new features
    $('[data-toggle="tooltip"]').tooltip();

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
  });

  $(window).on('error', function() {
    $('#trends').html('Ooops! Something went wrong!');
  });

  // TODO update visualization
  $(window).on('resize', responsiveUtils);

  function responsiveUtils() {
    if ($(window).width() < 992) {
      $('#controls').removeClass('pull-right text-right').addClass('list-inline');
    } else {
      $('#controls').removeClass('list-inline').addClass('pull-right text-right');
    }
  }

  function getTrends() {

    // create url
    var pathArray = document.URL.split('/');
    var url = pathArray[0] + '//' + pathArray[2] + '/rpc?woeid=' + woeid;

    if (history == DATE) {
      startDate = Math.floor($('#datepicker').datepicker('getDate')
        .getTime() / 1000);
      endDate = startDate + 86400;
      url += '&timestamp=' + startDate + '&end_timestamp=' + endDate;
    } else {
      url += '&history=' + getHistoryText();
    }

    url += '&limit=' + LIMIT;

    // make call
    var http_request = new XMLHttpRequest();
    http_request.open('GET', url, true);
    http_request.onreadystatechange = function() {
      if (http_request.readyState == 4) {
        hideLoading();

        if (http_request.status == 200) {
          onSuccess(http_request.responseText);
        } else if (http_request.status == 503) {
          onFailure('Request limit exceeded. Try tomorrow! Or get in touch with me via <a href="https://twitter.com/#!/mustilica">@mustilica</a>.');
          /* Hide controls */
          $('#controls').hide();
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

    if (response == '') {
      $('#trends').html('You should enter a valid input!');
      return;
    }

    if (response.trends.length == 0) {
      $('#trends').html('No record! Please pick a date after July, 12 2013.');
      return;
    }

    drawTrends();
    setCurrentChartExplanation();
    stopInitialAnimation = 0;
    setTimeout(startInitialAnimation, 3000);
  }

  function onFailure(msg) {
    $('#trends').html(msg || 'Ooops! Something went wrong!');
  }

  function displayLoading() {
    $('#trends').empty().append('<span>Loading...</span><div id="loading-area"><div class="spinner"></div></div>');
  }

  function hideLoading() {
    $('#trends').empty()
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
      if (typeof index == 'undefined') {
        index = 0;
      }
      if (list[index]) {
        activeTooltip = $(list[index]).mouseover();
        setTimeout(function() {
          $(list[index]).mouseout();
          activeTooltip = null;
          startInitialAnimation(list, index + 1);
        }, 5000);
      }
    } catch (e) {
      // TODO handle exception
    }
  }

  function pauseInitialAnimation() {
    if (activeTooltip) {
      activeTooltip.mouseout();
      stopInitialAnimation = 1;
      activeTooltip = null;
    }
  }

  /**
   * Set current chart explanation
   */
  function setCurrentChartExplanation(message) {
    var message = 'Trending topics';

    if (history == LAST_DAY) {
      message += ' within last 24 hours';
    } else if (history == LAST_WEEK) {
      message += ' within last week';
    } else if (history == LAST_MONTH) {
      message += ' within last month';
    } else {
      message += ' on ' + $('#datepicker')
        .datepicker('getDate')
        .toDateString()
        .substring(4);
    }

    if (woeid == 1) {
      message += ' in Worldwide';
    } else {
      message += ' in Turkey';
    }

    $('#trends').prepend('<span>' + message + '</span>');
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
      $('#dateText').html($('#datepicker'))
        .datepicker('getDate')
        .toDateString()
        .substring(4);
    } else {
      $('#dateText').html('pick a date');
    }
  }

  function changeRegionBtnStyle(node) {
    $('.country ').removeClass('current');
    node.parent().addClass('current');
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
      return 'ld';
    } else if (history == LAST_WEEK) {
      return 'lw';
    } else if (history == LAST_MONTH) {
      return 'lm';
    }
  }

  /**
   * Charts
   */
  var charts = {
    bubbleChart: function() {

      var area = $('#trends'),
        force,
        node,
        svg;

      return {
        draw: function() {
          // Clear draw area.
          area.html('');

          var w = area.outerWidth(),
            h = area.outerHeight();

          var nodes = response.trends,
            maxNodeValue = nodes[0].duration,
            //fill = d3.scale.category10(),
            fill = d3.scale.ordinal().range(['#fdea6f', '#f3b355', '#e97e3b', '#cf4f29', '#723c2c']),
            radiusCoefficient = (1000 / w) * (maxNodeValue / 50);

          force = d3.layout.force()
            .gravity(0.03)
            .charge(charge)
            .nodes(nodes)
            .size([w, h])
            .on('tick', tick).start();

          // TODO use different settings for mobile.
          svg = d3.select('#trends').append('svg')
            .attr('width', w)
            .attr('height', h);

          node = svg.selectAll('.node').data(nodes)
            .enter().append('circle')
            .attr('class', 'node')
            .attr('cx', function(d) {
              return d.x;
            }).attr('cy', function(d) {
              return d.y;
            }).attr('r', 0).style('fill', function(d) {
              return assignColor(d);
            }).style('stroke', function(d, i) {
              return d3.rgb(d.color).darker(2);
            }).call(force.drag);

          node.transition()
            .duration(1000)
            .attr('r', function(d) {
              return d.duration / radiusCoefficient;
            });

          svg.style('opacity', 1e-6)
            .transition()
            .duration(1000)
            .style('opacity', 1);

          $('circle').tooltip({
            container: 'body',
            animation: false,
            html: true,
            title: function() {
              var d = d3.select(this);
              // Tooltip html
              return '<div class="tooltip-topic">' + d[0][0].__data__.name + '</div><div class="tooltip-time">' + pretifyDuration(d[0][0].__data__.duration) + '</div>';
            }
          });

          $('circle').on('hide.bs.tooltip', function() {
            d3.select(this).transition()
              .duration(200)
              .style('opacity', 1)
              .attr('r', function(d) {
                return d.duration / radiusCoefficient;
              });
          });

          $('circle').on('shown.bs.tooltip', function() {
            // Update tooltip y position if it is scrolled.
            var scrollTop = $(document).scrollTop();
            if (scrollTop > 0) {
              var tooltip = $('.tooltip');
              tooltip.css({
                top: tooltip.position().top + scrollTop
              });
            }

            // Control for initial animation
            pauseInitialAnimation();

            // Bring to front
            d3.select(this).moveToFront()
              .transition()
              .duration(200)
              .style('opacity', .9)
              .attr('r', function(d) {
                return d.duration / radiusCoefficient + 10;
              });
          });

          function tick(e) {
            var k = -0.1 * e.alpha;
            nodes.forEach(function(o, i) {
              o.y += k;
              o.x += k;
            });

            node.attr('cx', function(d) {
              return d.x;
            }).attr('cy', function(d) {
              return d.y;
            });
          }

          function charge(d) {
            return -Math.pow(d.duration / (radiusCoefficient * 2), 2.0) / 8;
          }

          function assignColor(d) {
            //console.log(d.duration, maxNodeValue, Math.floor(d.duration / (maxNodeValue / 5)));
            d.color = fill(Math.floor(d.duration / (maxNodeValue / 5)));
            return d.color;
          }

          function pretifyDuration(value) {
            if (value == 0) {
              return '';
            } else if (value > 59) {
              return Math.floor(value / 60) + ' h. ' + pretifyDuration(value % 60);
            } else {
              return value + ' min.'
            }
          }

        },
        remove: function(callback) {
          force.gravity(0.001).resume();

          node.transition()
            .duration(1000)
            .attr('r', 0)
            .remove();

          svg.style('opacity', 1)
            .transition()
            .duration(1000)
            .style('opacity', 1e-6)
            .remove()
            .each('end', callback);
        }
      }
    }
  }

  var currentChart = charts.bubbleChart();

  /**
   * UI element bindings
   */
  $('.region').click(function() {
    var woeid = $(this).attr('data-woeid');
    if (woeid != '') {
      setWoeid($(this), $(this).attr('data-woeid'));
    }
  });

  $('#datepickerBtn').click(function() {
    toggleDatepicker();
  });

})();
