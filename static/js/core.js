Scuba   = Scuba || {}
Scuba.core = Scuba.core || {}

var Class = (function() {
        function extend(base, definition) {
            var c = function() { this.initialize.apply(this, arguments); };
            $.extend(c.prototype, base.prototype);
            if (! c.prototype.initialize) c.prototype.initialize = function() {};
            c.prototype.constructor = c;
            c.prototype.parent = base.prototype;
            $.extend(c.prototype, definition);
            return c;
        }

        return {
            create: function(definition) { return extend({}, definition); },
            extend: extend
        };
})();

(function() {
    Scuba.core.defineClass = function(base, definition) {
        var c = function() { this.initialize.apply(this, arguments); };
        $.extend(c.prototype, base.prototype);
        if (! c.prototype.initialize) c.prototype.initialize = function() {};
        c.prototype.constructor = c;
        c.prototype.parent = base.prototype;
        $.extend(c.prototype, definition);
        return c;
    };
})();

var Scuba = Scuba || {};
var SM = { 'logbook': { 'headers': {} }};


