var flagIcon    = null;

function initFlagIcon()
{
    console.log("step 1");
    console.log(image_url);
    console.log("step 2");
    console.log(google);
    console.log("step 3");
    console.log(google.maps);
    console.log("step 4");
    console.log(google.maps.MarkerImage);
    flagIcon = new google.maps.MarkerImage(image_url + 'images/icons/divemarker.png',
                                           new google.maps.Size(20, 33),
                                           new google.maps.Point(0, 0),
                                           new google.maps.Point(0, 33));
}
