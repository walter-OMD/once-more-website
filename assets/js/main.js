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

// Client logo carousel: continuous auto-scroll + drag to scroll
(function () {
  var viewport = document.querySelector('.logos');
  var track = viewport && viewport.querySelector('.logos-track');
  if (!viewport || !track) return;

  // width of a single set (the track holds two identical copies)
  function setWidth() { return track.scrollWidth / 2; }

  var reduce = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var speed = 0.5;          // px per frame for auto-scroll
  var dragging = false, paused = false;
  var startX = 0, startScroll = 0, raf;

  function wrap() {
    var w = setWidth();
    if (w <= 0) return;
    if (viewport.scrollLeft >= w) viewport.scrollLeft -= w;
    else if (viewport.scrollLeft < 0) viewport.scrollLeft += w;
  }

  function tick() {
    if (!dragging && !paused && !reduce) {
      viewport.scrollLeft += speed;
      wrap();
    }
    raf = requestAnimationFrame(tick);
  }
  raf = requestAnimationFrame(tick);

  // pause on hover so people can read
  viewport.addEventListener('mouseenter', function () { paused = true; });
  viewport.addEventListener('mouseleave', function () { paused = false; });

  // drag to scroll (pointer covers mouse + touch)
  viewport.addEventListener('pointerdown', function (e) {
    dragging = true;
    viewport.classList.add('dragging');
    startX = e.clientX;
    startScroll = viewport.scrollLeft;
    viewport.setPointerCapture && viewport.setPointerCapture(e.pointerId);
  });
  viewport.addEventListener('pointermove', function (e) {
    if (!dragging) return;
    viewport.scrollLeft = startScroll - (e.clientX - startX);
    wrap();
  });
  function endDrag() {
    dragging = false;
    viewport.classList.remove('dragging');
  }
  viewport.addEventListener('pointerup', endDrag);
  viewport.addEventListener('pointercancel', endDrag);
  viewport.addEventListener('mouseleave', endDrag);
})();

