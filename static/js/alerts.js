document.addEventListener("DOMContentLoaded", function() {

    let divAlertBell = document.getElementById('alertbell');
    let divAlert = document.getElementById('alerts');

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
            divAlert.innerHTML = '';
        }).catch(error => console.log(`Here is our error: ${error}`));
    };
});
