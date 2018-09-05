//
Scuba.Slickgrid = Scuba.core.defineClass(Object, {
    grid: null,
    json_url: null,
    columns: [],
    
    initialize: function(container_id, json_url)
    {
    	this.container_id   = container_id;
        this.json_url       = json_url;
    },

    setup: function()
    {
        $.getJSON(window.location.protocol + '//' + window.location.host + this.json_url, this.json_request_data, function(response)
        {
        	this.columns = [];
        	this.columns = this.columns.concat(response.columns);
        	//this.grid = new Slick.Grid('#myGrid', this.dataView, this.columns, this.options);
        });
    }
});
