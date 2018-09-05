SM = SM || {};

function doPoll()
{
    pollrate    = 50000;
    $.ajax({
        type: "GET",
        url: "/account/poll/",

        async: true, /* If set to non-async, browser shows page as "Loading.."*/
        //cache: false,
        timeout:50000, /* Timeout in ms */

        success: function(data)
        { 
            items       = data.data.items[0]; 
            alerts      = items.alerts;
            //pollrate    = items.pollrate;
            pollrate    = 50000;

            if (alerts > 0)     $('#alerts').html(alerts.toString());
            else                $('#alerts').html("");

            setTimeout(
                doPoll, /* Request next message */
                pollrate /* ..after 1 seconds */
            );
        },
        error: function(XMLHttpRequest, textStatus, errorThrown)
        {
            console.log("error", textStatus + " (" + errorThrown + ")");
            setTimeout(
                doPoll, /* Try again after.. */
                15000
            ); /* milliseconds (15seconds) */
        }
    });
};
