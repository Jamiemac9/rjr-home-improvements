/* Cookie consent — RJR Home Improvements
   The site sets no cookies by default. Optional analytics only run after "Accept".
   To add analytics, put the tag in build.py's ANALYTICS setting; it is emitted as
   <script type="text/plain" data-consent="analytics"> and activated here on consent.
   The choice is stored in localStorage ("rjr-consent") for 180 days. */
(function () {
  var KEY = "rjr-consent", DAYS = 180;
  var box = document.getElementById("consent");
  if (!box) return;

  function read() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || "null");
      if (v && Date.now() - v.t < DAYS * 864e5) return v.choice;
    } catch (e) {}
    return null;
  }
  function save(choice) {
    try { localStorage.setItem(KEY, JSON.stringify({ choice: choice, t: Date.now() })); } catch (e) {}
  }
  function activate() {
    var tags = document.querySelectorAll('script[type="text/plain"][data-consent="analytics"]');
    for (var i = 0; i < tags.length; i++) {
      var s = document.createElement("script");
      for (var j = 0; j < tags[i].attributes.length; j++) {
        var a = tags[i].attributes[j];
        if (a.name !== "type" && a.name !== "data-consent") s.setAttribute(a.name, a.value);
      }
      s.text = tags[i].text;
      tags[i].parentNode.replaceChild(s, tags[i]);
    }
  }
  function show() { box.hidden = false; }
  function hide() { box.hidden = true; }

  var choice = read();
  if (choice === "accept") activate();
  if (!choice) show();

  box.addEventListener("click", function (e) {
    var b = e.target.closest("[data-choice]");
    if (!b) return;
    var c = b.getAttribute("data-choice");
    save(c);
    hide();
    if (c === "accept") activate();
  });
  var open = document.querySelectorAll("[data-consent-open]");
  for (var k = 0; k < open.length; k++) open[k].addEventListener("click", show);
})();
