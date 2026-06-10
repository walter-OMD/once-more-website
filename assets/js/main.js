// OnceMore Digital - minimal interactions
(function () {
  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var links = document.getElementById('nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', function () {
      var open = links.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Contact form: no backend yet, fall back to a mailto so nothing is lost
  var form = document.getElementById('contact-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var name = (form.name && form.name.value) || '';
      var email = (form.email && form.email.value) || '';
      var message = (form.message && form.message.value) || '';
      var subject = encodeURIComponent('Website enquiry from ' + (name || 'a visitor'));
      var body = encodeURIComponent(
        'Name: ' + name + '\nEmail: ' + email + '\n\n' + message
      );
      window.location.href =
        'mailto:walter@oncemoredigital.com?subject=' + subject + '&body=' + body;
    });
  }
})();
