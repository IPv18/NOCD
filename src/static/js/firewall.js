document.addEventListener("DOMContentLoaded", function () {
    // Get the alert message element
    var alertMessage = document.getElementById('alert-message');

    // If the alert message element exists, add an event listener to the close button
    if (alertMessage) {
        var closeButton = alertMessage.querySelector('.close');
        closeButton.addEventListener('click', function() {
            // When the close button is clicked, remove the alert message from the session storage
            sessionStorage.removeItem('alert-message');
        });
    }

    // Check if the alert message is in the session storage
    var sessionMessage = sessionStorage.getItem('alert-message');
    if (sessionMessage) {
        // If the alert message is in the session storage, display it and remove it from the session storage
        alertMessage.innerHTML = sessionMessage;
        sessionStorage.removeItem('alert-message');
    }
    

    function SwitchTablePolicy(rule_id) {
        var xhr = new XMLHttpRequest();
        var url = '/firewall/rule/' + rule_id + '/';
        xhr.open('PATCH', url);
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        xhr.setRequestHeader('X-CSRFToken', csrftoken);
        xhr.onload = function() {
            location.reload();
        };
        xhr.send();
    }

    const switchPolicyBtns = document.querySelectorAll('.switch-policy-btn');
    if (switchPolicyBtns) {
        switchPolicyBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const rule_id = this.getAttribute('data-rule-id');
                SwitchTablePolicy(rule_id);
            });
        });
    }
});