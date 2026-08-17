document.addEventListener("DOMContentLoaded", function() {

    let divAlertBell = document.getElementById('alertbell');
    let divAlert = document.getElementById('alerts');

    // #alertbell only renders when alert_server_active is on (layout.html),
    // but this script loads for every authenticated user regardless -- so
    // the element is legitimately absent whenever that setting is off.
    if (!divAlertBell) {
        return;
    }

    divAlertBell.onclick = () => {
        fetch('/api/accounts/alerts', {
            headers: {
                'X-CSRFToken':  Cookies.get('csrftoken')
            },
            method: 'GET',
        })
        .then(handleErrors)
        .then(response => response.json())
        .then(data => {
            if (divAlert) {
                divAlert.innerHTML = '';
            }
        }).catch(error => console.log(`Here is our error: ${error}`));
    };
});
