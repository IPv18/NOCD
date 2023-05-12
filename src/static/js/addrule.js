document.addEventListener("DOMContentLoaded", function () {
  const URL_PARAMS = new URLSearchParams(window.location.search);
  const IP_FAMILY_PARAM = URL_PARAMS.get("ip_family");
  const TRAFFIC_DIRECTION_PARAM = URL_PARAMS.get("traffic_direction");

  const FORM = document.getElementById("rule_form");
  const RULE_NUM = document.getElementById("id_rule_priority");
  const DESCRIPTION = document.getElementById("id_description");
  const TYPE_SELECT = document.getElementById("id_type");
  const PROTOCOL_SELECT = document.getElementById("id_protocol");
  const TRAFFIC_DIRECTION = document.getElementById("id_traffic_direction");
  const IP_FAMILY = document.getElementById("id_ip_family");
  const SOURCE_PORT = document.getElementById("id_source_port");
  const DESTINATION_PORT = document.getElementById("id_destination_port");
  const SOURCE_ADDRESS = document.getElementById("id_source_address");
  const DESTINATION_ADDRESS = document.getElementById("id_destination_address");

  const SUBMIT_BUTTON = FORM.querySelector('input[type="submit"]');
  const UPDATE_OR_SUBMIT = SUBMIT_BUTTON.getAttribute('update-or-submit');
  const PATTERN = SOURCE_ADDRESS.getAttribute('pattern');

  const UDP_TYPE = ["CUSTOM UDP", "ALL UDP", "DNS UDP 53", "NFS 2049"];
  const TCP_TYPE = ["CUSTOM TCP", "ALL TCP"];

  if (UPDATE_OR_SUBMIT == "UPDATE")
    original_rule_priority = RULE_NUM.value;

  const PORT_MAPPING = {
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

  if (IP_FAMILY_PARAM !== null && TRAFFIC_DIRECTION_PARAM !== null) 
  {
    TRAFFIC_DIRECTION.value = TRAFFIC_DIRECTION_PARAM;
    IP_FAMILY.value = IP_FAMILY_PARAM;
    TRAFFIC_DIRECTION.disabled = true;
    IP_FAMILY.disabled = true;
  } 
  else 
  {
    TRAFFIC_DIRECTION.disabled = true;
    IP_FAMILY.disabled = true;
    if (TYPE_SELECT.value == "ALL UDP" || TYPE_SELECT.value == "ALL TCP" || TYPE_SELECT.value == "CUSTOM ICMP" || TYPE_SELECT.value === "ALL ICMP") 
      SOURCE_PORT.disabled = DESTINATION_PORT.disabled = true; 
    else 
      if (TRAFFIC_DIRECTION.value == "Inbound" && TYPE_SELECT.value != "CUSTOM UDP" && TYPE_SELECT.value != "CUSTOM TCP") 
        SOURCE_PORT.disabled = true;
      else if (TRAFFIC_DIRECTION.value == "Outbound" && TYPE_SELECT.value != "CUSTOM UDP" && TYPE_SELECT.value != "CUSTOM TCP")
        DESTINATION_PORT.disabled = true;
  }

  TYPE_SELECT.addEventListener("change", (event) => {
    const SELECTED_TYPE = event.target.value;

    let protocolValue = "TCP";

    if (UDP_TYPE.includes(SELECTED_TYPE)) {
      protocolValue = "UDP";
      if (SELECTED_TYPE === "ALL UDP") {
        SOURCE_PORT.value = "";
        DESTINATION_PORT.value = "";
      }
      SOURCE_PORT.disabled = DESTINATION_PORT.disabled =
        SELECTED_TYPE === "ALL UDP";
      SOURCE_ADDRESS.disabled = DESTINATION_ADDRESS.disabled = false;
    } else if (TCP_TYPE.includes(SELECTED_TYPE)) {
      if (SELECTED_TYPE === "ALL TCP") {
        SOURCE_PORT.value = "";
        DESTINATION_PORT.value = "";
      }
      SOURCE_PORT.disabled = DESTINATION_PORT.disabled =
        SELECTED_TYPE === "ALL TCP";
      SOURCE_ADDRESS.disabled = DESTINATION_ADDRESS.disabled = false;
    } else if (SELECTED_TYPE == "CUSTOM ICMP" || SELECTED_TYPE == "ALL ICMP") {
      protocolValue = "ICMP";
      SOURCE_PORT.value = DESTINATION_PORT.value = "";
      SOURCE_PORT.disabled = DESTINATION_PORT.disabled = true;
    }

    PROTOCOL_SELECT.value = protocolValue;

    if (SELECTED_TYPE in PORT_MAPPING) {
      const PORT_NUMBER = PORT_MAPPING[SELECTED_TYPE];
      if (TRAFFIC_DIRECTION.value === "Inbound") {
        SOURCE_PORT.value = PORT_NUMBER;
        SOURCE_PORT.disabled = true;
        DESTINATION_PORT.disabled = false;
      } else {
        DESTINATION_PORT.value = PORT_NUMBER;
        DESTINATION_PORT.disabled = true;
        SOURCE_PORT.disabled = false;
      }
      SOURCE_ADDRESS.disabled = DESTINATION_ADDRESS.disabled = false;
    }
  });
  PROTOCOL_SELECT.addEventListener("change", (event) => {
    const SELECTED_TYPE = event.target.value;
    if (SELECTED_TYPE == "UDP") {
      TypeValue = "CUSTOM UDP";
      SOURCE_PORT.disabled = false;
      DESTINATION_PORT.disabled = false;
      SOURCE_ADDRESS.disabled = false;
      DESTINATION_ADDRESS.disabled = false;
    } else if (SELECTED_TYPE == "ICMP") {
      TypeValue = "CUSTOM ICMP";
      SOURCE_PORT.value = "";
      DESTINATION_PORT.value = "";
      SOURCE_PORT.disabled = true;
      DESTINATION_PORT.disabled = true;
      SOURCE_ADDRESS.disabled = false;
      DESTINATION_ADDRESS.disabled = false;
    } else if (SELECTED_TYPE == "TCP") {
      TypeValue = "CUSTOM TCP";
      SOURCE_PORT.disabled = false;
      DESTINATION_PORT.disabled = false;
      SOURCE_ADDRESS.disabled = false;
      DESTINATION_ADDRESS.disabled = false;
    }
    TYPE_SELECT.value = TypeValue;
  });

  SUBMIT_BUTTON.addEventListener("click", (event) => {
    if (!RULE_NUM.value || !DESCRIPTION.value) {
      errorModalBody.innerHTML = 'Both rule number and description are required.';
      $('#errorModal').modal("show");
      event.preventDefault();
      return;
    }
    else {
      if (UPDATE_OR_SUBMIT == "UPDATE") {
        if (original_rule_priority == RULE_NUM.value) {
          SOURCE_PORT.disabled = false;
          DESTINATION_PORT.disabled = false;
          SOURCE_ADDRESS.disabled = false;
          DESTINATION_ADDRESS.disabled = false;
          TRAFFIC_DIRECTION.disabled = false;
          IP_FAMILY.disabled = false;
          FORM.submit();
        }
      }
      const XML_HTTP_REQUEST = new XMLHttpRequest();
      XML_HTTP_REQUEST.open('GET', `/firewall/check_rule_uniqueness/?rule_priority=${RULE_NUM.value}&traffic_direction=${TRAFFIC_DIRECTION.value}&ip_family=${IP_FAMILY.value}`);
      XML_HTTP_REQUEST.onload = () => {
        if (XML_HTTP_REQUEST.status === 200) {
          const XML_HTTP_RESPONSE = JSON.parse(XML_HTTP_REQUEST.responseText);
          if (XML_HTTP_RESPONSE.exists) {
            errorModalBody.innerHTML = 'This rule number already exists, please choose a unique rule number.';
            $('#errorModal').modal("show");
          }
          else {
            SOURCE_PORT.disabled = false;
            DESTINATION_PORT.disabled = false;
            SOURCE_ADDRESS.disabled = false;
            DESTINATION_ADDRESS.disabled = false;
            TRAFFIC_DIRECTION.disabled = false;
            IP_FAMILY.disabled = false;
            FORM.submit();
          }
        } else {
          errorModalBody.innerHTML = 'An error occurred while checking the rule uniqueness.';
          $('#errorModal').modal("show");
        }
      };
      XML_HTTP_REQUEST.send();
      event.preventDefault(); 
    }
  });

  // input constraints

  var rule_priority_field = document.querySelector('input[name="rule_priority"]');
  rule_priority_field.addEventListener("input", function () {
    if (
      rule_priority_field.validity.rangeOverflow ||
      rule_priority_field.validity.rangeUnderflow
    ) {
      rule_priority_field.value = "";
      errorModalBody.innerHTML = 'The value must be between 1 and 999';
      $('#errorModal').modal("show");
    }
  });

  function validateIPAddress(input) {
    const REGEX = new RegExp(
      //Normal IPv6 REGEX : "^([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4}$"
      //Compressed IPv6 REGEX : "(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]).){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))"
      //IPv4 REGEX : "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(.(?!$)|$)){4}$" 
      PATTERN
    );
    if (!REGEX.test(input.value)) {
      input.value = null;
      if (IP_FAMILY.value == "IPv6")
        errorModalBody.innerHTML = 'Please enter a valid host/network normal IPv6 address.';
      else
        errorModalBody.innerHTML = 'Please enter a valid host/network IPv4 address.<br>Possible inputs:-<br><br>&emsp;-->[0-255].[0-255].[0-255].[0-255]<br>&emsp;-->[0-255].[0-255].[0-255].[0-255]/[1-31]';
      $('#errorModal').modal("show");
    }
  }

  function validatePort(input) {
    const REGEX = new RegExp(
      "^((6553[0-6])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-9]{1,4}))(:(?=((6553[0-6])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-9]{1,4}))))?((?<=:)(?=((6553[0-6])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-9]{1,4}))))?((?<=:)((6553[0-6])|(655[0-2][0-9])|(65[0-4][0-9]{2})|(6[0-4][0-9]{3})|([1-5][0-9]{4})|([0-9]{1,4})))?$"
    );
  
    if (!REGEX.test(input.value)) {
      input.value = "";
      errorModalBody.innerHTML = "Please enter a valid port number (or range).<br>Possible inputs:<br><br>&emsp;-->[0-65536]<br>&emsp;-->[0-65536]:[0-65536]";
      $('#errorModal').modal("show");
    } else {
      const parts = input.value.split(":");
      if (parts.length == 2 && parseInt(parts[1]) <= parseInt(parts[0])) {
        input.value = "";
        errorModalBody.innerHTML = "Please enter a valid port range where the second port number is larger than the first port number.";
        $('#errorModal').modal("show");
      }
    }
  }
  
  


  SOURCE_PORT.addEventListener("blur", function () {
    validatePort(SOURCE_PORT);
  });

  DESTINATION_PORT.addEventListener("blur", function () {
    validatePort(DESTINATION_PORT);
  });

  SOURCE_ADDRESS.addEventListener("blur", function () {
    validateIPAddress(SOURCE_ADDRESS, IP_FAMILY);
  });

  DESTINATION_ADDRESS.addEventListener("blur", function () {
    validateIPAddress(DESTINATION_ADDRESS, IP_FAMILY);
  });
});

function redirectToHome() {
  const URL_PARAMS = new URLSearchParams(window.location.search);
  const IP_FAMILY_PARAM = URL_PARAMS.get("ip_family");
  const TRAFFIC_DIRECTION_PARAM = URL_PARAMS.get("traffic_direction");
  
  var id = "";
  if (IP_FAMILY_PARAM === "IPv4" && TRAFFIC_DIRECTION_PARAM === "Inbound") {
      id = "1";
  } else if (IP_FAMILY_PARAM === "IPv4" && TRAFFIC_DIRECTION_PARAM === "Outbound") {
      id = "2";
  } else if (IP_FAMILY_PARAM === "IPv6" && TRAFFIC_DIRECTION_PARAM === "Inbound") {
      id = "3";
  } else if (IP_FAMILY_PARAM === "IPv6" && TRAFFIC_DIRECTION_PARAM === "Outbound") {
      id = "4";
  }
  
  var homeUrl = '/firewall/?id=' + encodeURIComponent(id);
  window.location.href = homeUrl;
}
