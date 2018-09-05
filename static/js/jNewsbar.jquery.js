/**
*
* jNewsbar Plugin
* URL: http://www.codecanyon.net/user/phpbits
* Version: 1.0
* Author: phpbits
* Author URL: http://www.codecanyon.net/user/phpbits
*
*/

// Utility
if ( typeof Object.create !== 'function' ) {
	Object.create = function( obj ) {
		function F() {};
		F.prototype = obj;
		return new F();
	};
}

(function( $, window, document, undefined ) {
	var Newsbar = {
		init: function( options, elem ) {
			var self = this;

			self.elem = elem;
			self.$elem = $( elem );
			self.options = $.extend( { onHover:function(){} }, $.fn.jNewsbar.options, options );
			self.options.pauseTime = self.options.pauseTime + self.options.animSpeed;

			self.buildFrag(); self.display();
		},
		buildFrag: function() {
			var self = this;

			self.$elem.addClass('jnewsbar jnews-' + self.options.theme + ' jnews-' + self.options.position + ' jnews-' + self.options.effect).css(self.options.position,0).show();

			self.$elem.find("h2").wrap('<div class="jnewsbar-title"></div>').css({
				"font-size": self.options.height - 5 + "px",
				"height": self.options.height + "px",
				"line-height": self.options.height + "px"
			});

			self.$elem.find("ul").wrap('<div></div>').addClass('jnewsbar-items');
			self.$elem.css({
				"height": self.options.height + "px",
				"line-height": self.options.height + "px"
			});

			self.$elem.find("li").css({
				"height": self.options.height + "px",
				"line-height": self.options.height + "px",
				"overflow": "hidden"
			});

			//build pagination
			self.$elem.append( self.buildControls() );
		},
		buildControls: function(){
			var self = this;
			return '<div class="jnewsbar-navigate"><a href="#" class="prev" alt="Previous">&laquo;</a> <a href="#" class="next" alt="Next">&raquo;</a></div><div class="jnews-toggle"><a href="#" class="toggle"  style="height:'+ self.options.height +'px; line-height:'+ self.options.height +'px;" >Toggle</a></div>';
		},
		display: function() {
			var self = this;

			//reverse order on slideDown
			self.reverseOrder();

			//pause on hover
			self.pauseOnhover();
			
			//next
			self.$elem.find('.jnewsbar-navigate .next').on('click',function(e){
				switch(self.options.effect){
					case "slideDown":
						self.prev();
					break;

					default:
						self.next();
					break;
				}
				
				self.removeInterval(); self.setInterval();
				e.preventDefault();
				
			});

			//prev
			self.$elem.find('.jnewsbar-navigate .prev').on('click',function(e){
				switch(self.options.effect){
					case "slideDown":
						self.next();
					break;

					default:
						self.prev();
					break;
				}
				self.removeInterval(); self.setInterval();
				e.preventDefault();
			});
			
			//toggle
			self.$elem.find('.jnews-toggle .toggle').on('click',function(e){
				var h = self.options.height * self.options.toggleItems;
				if( self.$elem.hasClass('opened') ){
					self.$elem.removeClass('opened'); $(this).removeClass('open');
					self.$elem.animate({height: self.options.height + 'px'},self.options.animSpeed).find('.jnewsbar-title h2, .jnewsbar-navigate').animate({ 'height' : self.options.height  + 'px', 'line-height' : self.options.height  + 'px' }, self.options.animSpeed);
				}else{
					self.$elem.addClass('opened'); $(this).addClass('open');
					self.$elem.animate({height: h + 'px'},self.options.animSpeed).find('.jnewsbar-title h2, .jnewsbar-navigate').animate({ 'height' : h + 'px', 'line-height' : h + 'px' }, self.options.animSpeed);
				}
			});

			self.setInterval();
		},
		tick: function(){
			var self = this;
			switch(self.options.effect){
				case "slideDown":
					self.prev();
				break;

				case "fade":
					self.$elem.find('li:first').animate({'opacity':0}, self.options.animSpeed, function(){ $(this).appendTo(self.$elem.find('ul.jnewsbar-items')).css('opacity', 1); });
				break;

				default:
					self.next();
				break;
			}
		},
		setInterval: function(){
			var self = this;
			$setInterval = setInterval(function(){ self.tick(); }, self.options.pauseTime);
			self.$elem.attr( "data-id",$setInterval );
		},
		removeInterval:function(){
			var self = this;
			window.clearInterval( self.$elem.attr( "data-id" ) );
		},
		pauseOnhover:function(){
			var self = this;
			var count = 0;
			if(self.options.pauseOnHover){
				self.$elem.find('li').on('hover mouseover mouseup',function(){
					self.removeInterval();
					if( count == 0 ){
						$(this).addClass('hovered');
						self.options.onHover.call(self);
					}
					count++;
				}).on('mouseout mousedown',function(){
					self.setInterval();
					self.$elem.find('li').removeClass('hovered');
					count = 0;
				});
			}
		},
		prev: function(){
			var self = this;
			self.$elem.find('.jnewsbar-items').css('margin-top', -self.options.height + 'px');
			self.$elem.find('.jnewsbar-items li:last').prependTo(self.$elem.find('.jnewsbar-items'));
			self.$elem.find('.jnewsbar-items').animate({
				marginTop: 0 + 'px'
			}, self.options.animSpeed, 'linear' ,function(){  });

		},
		next: function(){
			var self = this;
			self.$elem.find('.jnewsbar-items').animate({
				marginTop: -self.options.height + 'px'
			}, self.options.animSpeed, 'linear' ,function(){ $(this).find('li:first').appendTo(this).hide().fadeIn(300); $(this).css('margin-top',0); });
		},
		reverseOrder: function(){
			var self = this;
			//reverse list item when slideDown effect
			if(self.options.effect == "slideDown"){
				var list = self.$elem.find('.jnewsbar-items');
				var listItems = list.children('li');
				list.append(listItems.get().reverse());

				//fix the first item
				$( self.$elem.find('.jnewsbar-items li:last')).prependTo(list);
			}
		}
	};
	$.fn.jNewsbar = function( options ) {
		return this.each(function() {
			var jnewsbar = Object.create( Newsbar );
			
			jnewsbar.init( options, this );

			$.data( this, 'jNewsbar', jnewsbar );
		});
	};

	$.fn.jNewsbar.options = {
		position : 'bottom',
		effect : 'slideUp',
		height : 23,
		animSpeed: 600, // Slide transition speed
        pauseTime: 3000,
        pauseOnHover: true,
        toggleItems: 5,
        theme: 'dark'
	};

})( jQuery, window, document );