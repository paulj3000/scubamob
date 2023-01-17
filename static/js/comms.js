if (!window.console) {
    window.console = { log: function() {} };
}

var SM = SM || {}

if (typeof(console) == undefined) {
    console = { log: function(data) {} };
}

// add some stuff to the '$' variable
(function()
{
    $.doAjaxDelete =      function(url, data, success)
    {
        $.doAjax('DELETE', url, data, success);
    },

    $.doAjaxPut =      function(url, data, success)
    {
        $.doAjax('PUT', url, data, success);
    },


    $.doAjaxPost =      function(url, data, success)
    {
        $.doAjax('POST', url, data, success);
    },

    $.doAjaxGet =      function(url, data, success)
    {
        $.doAjax('GET', url, data, success);
    },

    $.doAjax =         function(type, url, data, success)
    {
        data    = JSON.stringify(data);
        console.log(data);
        $.ajax({
                url: url,
                type: type,
                data: data,
                contentType:"application/json; charset=utf-8",
                dataType: 'json',
                success: success,
       });
    },

    $.escapeHTML = function(string)
    {
        if (! string) return string;
        return $(document.createElement('div')).text(string).html();
    };

    $.capitalize = function(string)
    {
        return string.charAt(0).toUpperCase() + string.substr(1);
    };

    // how about some object stuff
    $.getObjectKeys = function(obj)
    {
        var keys = [];
        for (var k in obj)  keys.push(k);

        return keys;
    };

    // do some local storage settings
    $.sessionSet = function(domain, key, value)
    {
        data    = {};
        if (localStorage[domain])
        {
            // we have some data.  Let's get it from local storage and
            // turn it into a json object
            data    = jQuery.parseJSON(localStorage[domain]);
        }

        // now, store the key
        data[key] = value;

        // and convert and store it back into localstorage
        localStorage[domain]    = JSON.stringify(data);
    }

    // do some local storage settings
    $.sessionGet = function(domain, key, def)
    {
        data    = {};
        if (localStorage[domain])
        {
            // we have some data.  Let's get it from local storage and
            // turn it into a json object
            data    = jQuery.parseJSON(localStorage[domain]);
        }

        if (key)
        {
            if (data[key])  return data[key];
            else if (def)   return def;
            return null;
        }
        else                  return data;
    }
})();
