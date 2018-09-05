showDialog = function (header, text, opts) {
  if (!($("#dialog").length)) {
    $("body").append("<div id=dialog title='"+header+"'></div>");
  } else {
    $(".ui-dialog-title").html(header);
  }

  contents = "<contentarea style=\"height:100px\"><div id=\"error\"></div>";
  for (var i=0; i < text.length; i++) {
     contents += '<div style="'+ (text[i].style || 'plain') +'">'+text[i].text+'</div>';
  }
  contents += "</contentarea>";

  btnArray = [
       {
           text: "Ok",
            'class':"right active",
            click: function() 
            {
                if (! opts.hasOwnProperty('fnok'))
                    $(this).dialog('destroy').remove();
                else
                    opts.fnok(this); 
            }
        },
        {
            text: "Cancel",
            'class':"right active",
            click: function() 
            {
                $(this).dialog('destroy').remove() 
            }
		}
  	];

  $("#dialog").html(contents);
  $("#dialog").dialog({ draggable : false, modal : true, buttons: btnArray});
};

hideDialog = function () {
  $("#dialog").parent().hide();
}

