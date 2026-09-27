/* Quote form -> pre-filled WhatsApp message.
   Nothing is sent to or stored by the website: the answers are written into a
   wa.me link on the visitor's device, and WhatsApp opens with the message ready
   to check, add photos to and send. Inputs deliberately have no name attributes,
   so a submit without JavaScript sends no personal data anywhere. */
(function () {
  var form = document.getElementById("quote");
  if (!form) return;

  function val(id) {
    var el = document.getElementById(id);
    return el ? el.value.trim() : "";
  }

  // Links like "Report an emergency" preset the urgency before jumping to the form
  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-set-urgency]");
    if (!a) return;
    var sel = document.getElementById("q-urgency");
    var want = a.getAttribute("data-set-urgency");
    for (var i = 0; sel && i < sel.options.length; i++) {
      if (sel.options[i].text.toLowerCase().indexOf(want) === 0) { sel.selectedIndex = i; break; }
    }
  });

  // Tidy the postcode as it's typed: upper case, single space before the last three characters
  var pc = document.getElementById("q-postcode");
  if (pc) pc.addEventListener("blur", function () {
    var v = pc.value.toUpperCase().replace(/\s+/g, "");
    if (v.length > 4) v = v.slice(0, -3) + " " + v.slice(-3);
    pc.value = v;
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var status = form.querySelector(".qstatus");
    if (!form.checkValidity()) {
      form.classList.add("tried");
      var bad = form.querySelector(":invalid");
      if (bad) bad.focus();
      if (status) status.textContent = "Please fill in the highlighted fields.";
      return;
    }
    var urgency = val("q-urgency");
    var emergency = urgency.toLowerCase().indexOf("emergency") === 0;
    var lines = [
      emergency ? "Hi RJR, I have a roofing emergency." : "Hi RJR, I'd like a quote.",
      "",
      "Service: " + val("q-service"),
      "Urgency: " + urgency,
      "Name: " + val("q-name"),
      "Postcode: " + val("q-postcode").toUpperCase(),
      "Area: " + val("q-area")
    ];
    if (val("q-property")) lines.push("Property: " + val("q-property"));
    lines.push("", "What's happening: " + val("q-details"), "");
    lines.push("Please reply by: " + (val("q-reply") || "WhatsApp message") + " (" + (val("q-when") || "Any time").toLowerCase() + ")");
    var photos = document.getElementById("q-photos");
    if (photos && photos.checked) lines.push("Photos: attached below.");
    lines.push("", "Sent from the website: " + (form.getAttribute("data-page") || "/"));

    var url = "https://wa.me/" + form.getAttribute("data-wa") + "?text=" + encodeURIComponent(lines.join("\n"));
    var link = document.createElement("a");
    link.href = url;
    link.target = "_blank";
    link.rel = "noopener";
    document.body.appendChild(link);
    link.click();
    link.remove();
    if (status) {
      status.innerHTML = "";
      status.appendChild(document.createTextNode("WhatsApp is opening with your message. If it didn't, "));
      var again = document.createElement("a");
      again.href = url; again.target = "_blank"; again.rel = "noopener";
      again.textContent = "tap here to open it";
      status.appendChild(again);
      status.appendChild(document.createTextNode("."));
    }
  });
})();
