document.addEventListener("DOMContentLoaded", function () {
  const urlParams = new URLSearchParams(window.location.search);
  const ip_family_param = urlParams.get("ip_family");
  const traffic_direction_param = urlParams.get("traffic_direction");

  const form = document.getElementById("ruleform");
  const ruleNum = document.getElementById("id_rule_num");
  const description = document.getElementById("id_description");
  const typeSelect = document.getElementById("id_type");
  const protocolSelect = document.getElementById("id_protocol");
  const traffic_direction = document.getElementById("id_traffic_direction");
  const ip_family = document.getElementById("id_ip_family");
  const source_port = document.getElementById("id_source_port");
  const destination_port = document.getElementById("id_destination_port");
  const source_address = document.getElementById("id_source_address");
  const destination_address = document.getElementById("id_destination_address");

  const updateOrSubmit = submitBtn.getAttribute('update_or_submit');
  const pattern = source_address.getAttribute('pattern');
  const submitBtn = form.querySelector('input[type="submit"]');

  const udpTypes = ["CUSTOM UDP", "ALL UDP", "DNS UDP 53", "NFS 2049"];
  const tcpTypes = ["CUSTOM TCP", "ALL TCP"];

  if (updateOrSubmit == "UPDATE")
    OriginalRuleNum = ruleNum.value;

  const portMapping = {
    "SSH 22": 22,
    "TELNET 23": 23,
    "SMTP 25": 25,
    "NAMESERVER 42": 42,
    "DNS UDP 53": 53,
    "DNS TCP 53": 53,
    "HTTP 80": 80,
    "POP3 110": 110,
    "IMAP 143": 143,
    "LDAP 389": 389,
    "HTTPS 443": 443,
    "SMB 445": 445,
    "SMTPS 465": 465,
    "IMAPS 993": 993,
    "POP3S 995": 995,
    "NFS 2049": 2049,
  };

  if (ip_family_param !== null && traffic_direction_param !== null) {
    traffic_direction.value = traffic_direction_param;
    ip_family.value = ip_family_param;
    traffic_direction.disabled = true;
    ip_family.disabled = true;
  } else {
    traffic_direction.disabled = true;
    ip_family.disabled = true;
    if (typeSelect.value == "ALL UDP") {
      source_port.disabled = destination_port.disabled = true;
    } else if (typeSelect.value == "ALL TCP") {
      source_port.disabled = destination_port.disabled = true;
    } else if (
      typeSelect.value == "CUSTOM ICMP" ||
      typeSelect.value === "ALL ICMP"
    ) {
      source_port.disabled = destination_port.disabled = true;
    } else {
      if (traffic_direction.value === "Inbound") {
        source_port.disabled = true;
      } else {
        destination_port.disabled = true;
      }
    }
  }

  typeSelect.addEventListener("change", (event) => {
    const selectedType = event.target.value;

    let protocolValue = "TCP";

    if (udpTypes.includes(selectedType)) {
      protocolValue = "UDP";
      if (selectedType === "ALL UDP") {
        source_port.value = "";
        destination_port.value = "";
      }
      source_port.disabled = destination_port.disabled =
        selectedType === "ALL UDP";
      source_address.disabled = destination_address.disabled = false;
    } else if (tcpTypes.includes(selectedType)) {
      if (selectedType === "ALL TCP") {
        source_port.value = "";
        destination_port.value = "";
      }
      source_port.disabled = destination_port.disabled =
        selectedType === "ALL TCP";
      source_address.disabled = destination_address.disabled = false;
    } else if (selectedType == "CUSTOM ICMP" || selectedType == "ALL ICMP") {
      protocolValue = "ICMP";
      source_port.value = destination_port.value = "";
      source_port.disabled = destination_port.disabled = true;
    }

    protocolSelect.value = protocolValue;

    if (selectedType in portMapping) {
      const portNumber = portMapping[selectedType];
      if (traffic_direction.value === "Inbound") {
        source_port.value = portNumber;
        source_port.disabled = true;
        destination_port.disabled = false;
      } else {
        destination_port.value = portNumber;
        destination_port.disabled = true;
        source_port.disabled = false;
      }
      source_address.disabled = destination_address.disabled = false;
    }
  });
  protocolSelect.addEventListener("change", (event) => {
    const selectedType = event.target.value;
    if (selectedType == "UDP") {
      TypeValue = "CUSTOM UDP";
      source_port.disabled = false;
      destination_port.disabled = false;
      source_address.disabled = false;
      destination_address.disabled = false;
    } else if (selectedType == "ICMP") {
      TypeValue = "CUSTOM ICMP";
      source_port.value = "";
      destination_port.value = "";
      source_port.disabled = true;
      destination_port.disabled = true;
      source_address.disabled = false;
      destination_address.disabled = false;
    } else if (selectedType == "TCP") {
      TypeValue = "CUSTOM TCP";
      source_port.disabled = false;
      destination_port.disabled = false;
      source_address.disabled = false;
      destination_address.disabled = false;
    }
    typeSelect.value = TypeValue;
  });

  submitBtn.addEventListener("click", (event) => {
    if (!ruleNum.value || !description.value) {
      errorModalBody.innerHTML = 'Both rule number and description are required.';
      $('#errorModal').modal("show");
      event.preventDefault();
      return;
    }
    else {
      if (updateOrSubmit == "UPDATE") {
        if (OriginalRuleNum == ruleNum.value) {
          source_port.disabled = false;
          destination_port.disabled = false;
          source_address.disabled = false;
          destination_address.disabled = false;
          traffic_direction.disabled = false;
          ip_family.disabled = false;
          form.submit();
        }
      }
      const xhr = new XMLHttpRequest();
      xhr.open('GET', `/firewall/check_rule_uniqueness/?rule_num=${ruleNum.value}&traffic_direction=${traffic_direction.value}&ip_family=${ip_family.value}`);
      xhr.onload = () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          if (response.exists) {
            errorModalBody.innerHTML = 'This rule number alread exists, please choose a unique rule number.';
            $('#errorModal').modal("show");
          }
          else {
            // Enable disabled fields and submit the form
            source_port.disabled = false;
            destination_port.disabled = false;
            source_address.disabled = false;
            destination_address.disabled = false;
            traffic_direction.disabled = false;
            ip_family.disabled = false;
            form.submit();
          }
        } else {
          errorModalBody.innerHTML = 'An error occurred while checking the rule uniqueness.';
          $('#errorModal').modal("show");
        }
      };
      xhr.send();
      event.preventDefault(); // Prevent the form from being submitted before the AJAX request completes
    }
  });

  // input constraints

  var ruleNumField = document.querySelector('input[name="rule_num"]');
  ruleNumField.addEventListener("input", function () {
    if (
      ruleNumField.validity.rangeOverflow ||
      ruleNumField.validity.rangeUnderflow
    ) {
      alert("The value must be between 1 and 999");
      ruleNumField.value = "";
    }
  });

  function validateIPAddress(input) {
    const regex = new RegExp(
      //Normal IPv6 Regex : "^([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}$"
      //Compressed IPv6 Regex : "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
      //IPv4 Regex : "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(.(?!$)|$)){4}$"
      pattern
    );
    if (!regex.test(input.value)) {
      input.value = null;
      if (pattern == "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(.(?!$)|$)){4}$")
        errorModalBody.innerHTML = 'Please enter a valid IPv4 address.';
      else
        errorModalBody.innerHTML = 'Please enter a valid IPv6 address.';
      $('#errorModal').modal("show");
    }
  }

  function validatePort(input) {
    const regex = new RegExp(
      "^((6553[0-6])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-5]{0,5})|([0-9]{1,4}))$"
    );
    if (!regex.test(input.value)) {
      input.value = "";
      errorModalBody.innerHTML = 'Please enter a valid port number';
      $('#errorModal').modal("show");
    }
  }

  source_port.addEventListener("input", function () {
    validatePort(source_port);
  });

  destination_port.addEventListener("input", function () {
    validatePort(destination_port);
  });

  source_address.addEventListener("blur", function () {
    validateIPAddress(source_address);
  });

  destination_address.addEventListener("blur", function () {
    validateIPAddress(destination_address);
  });
});
