sm = {};

sm.slickgrid   = function(elem, url, columns)  
{
    this.grid   = null;
    this.url    = url;

    var loader  = null;
    var options = {};
    var loadingIndicator = null;

    this.getPageSize    = function(p)
    {
        loader.getPageSize();
    };
    
    this.setPageSize    = function(p)
    {
        loader.setPageSize(p);
    };
    
    this.addUrlParam    = function(k, v)
    {
        loader.addUrlParam(k, v);
    };
    
    this.removeUrlParam    = function(k)
    {
        loader.removeUrlParam(k);
    };

    this.init   = function()
    {
        loader   = this.RemoteModel(url);
    }

    this.run = function()
    {
        grid = new Slick.Grid(elem, loader.data, columns, options);
	
        grid.onViewportChanged.subscribe(function(e,args) 
        {
            var vp = grid.getViewport();
            loader.ensureData(vp.top, vp.bottom);
        });
			
        grid.onSort.subscribe(function(e,args) {
            loader.setSort(args.sortCol.field, args.sortAsc ? 1 : -1);
            var vp = grid.getViewport();
            loader.ensureData(vp.top, vp.bottom);
        });

        loader.onDataLoading.subscribe(function() {
            if (!loadingIndicator)
            {
                loadingIndicator = $("<span class='loading-indicator'><label>Buffering...</label></span>").appendTo(document.body);
                var $g = $(elem);

                loadingIndicator
                    .css("position", "absolute")
                    .css("top", $g.position().top + $g.height()/2 - loadingIndicator.height()/2)
                    .css("left", $g.position().left + $g.width()/2 - loadingIndicator.width()/2)
            }

            loadingIndicator.show();
        });

        loader.onDataLoaded.subscribe(function(e,args) {
            for (var i = args.from; i <= args.to; i++) {
                grid.invalidateRow(i);
            }

            grid.updateRowCount();
            grid.render();

            loadingIndicator.fadeOut();
        });

        // load the first page
        grid.onViewportChanged.notify();
    };

    this.RemoteModel = function(baseUrl)
    {
        var data = {length: 0};
        var h_request   = null;
        var PAGESIZE    = 50;
        var sortcol     = null;
        var baseUrl     = baseUrl;

        var urlParams   = { 'start': 0, 
                            'end': 0, 
                            'limit': 0
                          };

        setPageSize = function(pg)
        {
            PAGESIZE = pg;
        }

        getPageSize = function()
        {
            console.log(PAGESIZE);
        }

        addUrlParam = function(k, v)
        {
            urlParams[k]    = v;
        }

        var req = null; // ajax request
        // events

        var onDataLoading = new Slick.Event();
        var onDataLoaded = new Slick.Event();

        isDataLoaded   = function(from, to) 
        {
          for (var i = from; i <= to; i++) {
            if (data[i] == undefined || data[i] == null) {
              return false;
            }
          }

          return true;
        }


        ensureData  = function(from, to) 
        {
            if (!baseUrl)
                throw "url not defined";

          if (req) {
            req.abort();
            for (var i = req.fromPage; i <= req.toPage; i++)
              data[i * PAGESIZE] = undefined;
          }

          if (from < 0) {
            from = 0;
          }

          if (data.length > 0) {
            to = Math.min(to, data.length - 1);
          }

          var fromPage = Math.floor(from / PAGESIZE);
          var toPage = Math.floor(to / PAGESIZE);

          while (data[fromPage * PAGESIZE] !== undefined && fromPage < toPage)
            fromPage++;

          while (data[toPage * PAGESIZE] !== undefined && fromPage < toPage)
            toPage--;

          if (fromPage > toPage || ((fromPage == toPage) && data[fromPage * PAGESIZE] !== undefined)) {
            // TODO:  look-ahead
            onDataLoaded.notify({from: from, to: to});
            return;
          }

          urlParams['start']    = (fromPage * PAGESIZE);
          urlParams['limit']    = (((toPage - fromPage) * PAGESIZE) + PAGESIZE);

          if (sortcol != null) 
              urlParams["sortby"]   = sortcol + ((sortdir > 0) ? "+asc" : "+desc");

          var url = baseUrl + "?";
         
          $.each(urlParams, function(i,e)
          {
              url += i + '=' + e + '&';
          });

          if (h_request != null) {
            clearTimeout(h_request);
          }

          h_request = setTimeout(function () {
            for (var i = fromPage; i <= toPage; i++)
              data[i * PAGESIZE] = null; // null indicates a 'requested but not available yet'

            onDataLoading.notify({from: from, to: to});

            req = $.jsonp({
              url: url,
              callbackParameter: "callback",
              cache: true,
              success: onSuccess,
              error: function () 
              {
                console.log("error loading pages " + fromPage + " to " + toPage);
              }
            });
            req.fromPage = fromPage;
            req.toPage = toPage;
          }, 50);
        }

        reloadData  = function(from, to) 
        {
            for (var i = from; i <= to; i++)
            delete data[i];

            ensureData(from, to);
        }
    
        setSort = function(column, dir) 
        {
            sortcol = column;
            sortdir = dir;
            clear();
        }

        clear  = function()
        {
          for (var key in data) {
            delete data[key];
          }
          data.length = 0;
        }

        function onSuccess(resp) 
        {
          var from = resp.request.start, to = from + resp.results.length;

          from  = parseInt(from);
          to  = parseInt(to);

          data.length = Math.min(parseInt(resp.hits),1000); // limitation of the API

          for (var i = 0; i < resp.results.length; i++) 
          {
            var item = resp.results[i].item;

            //item.create_ts = new Date(item.created);
            data[from + i] = item;
            data[from + i].index = from + i;
          }

          req = null;
          onDataLoaded.notify({from: from, to: to});
        }




        return {
            "data": data,
            "clear": clear,
      
            "ensureData": ensureData,
            "reloadData": reloadData,
            "setSort": setSort,
            "isDataLoaded": isDataLoaded,
      
            // events
            "onDataLoading": onDataLoading,
            "onDataLoaded": onDataLoaded,
            "addUrlParam": addUrlParam,
            
            // 
            "getPageSize": getPageSize,
            "setPageSize": setPageSize,
        };
    };

    this.init();
}
// Slick.Data.RemoteModel
//$.extend(true, window, { Slick: { Data: { RemoteModel: RemoteModel }}});
