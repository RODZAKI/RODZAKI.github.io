(function () {
  var LABEL = '⟵ Return to Threshold';
  var DEFAULT_HREF = '/';
  var BUTTON_ID = 'return-control-btn';

  function resolveReturnTarget() {
    try {
      if (
        document.referrer &&
        document.referrer.indexOf(window.location.origin) === 0
      ) {
        return document.referrer;
      }
    } catch (e) {}
    return DEFAULT_HREF;
  }

  function shouldInject() {
    var meta = document.querySelector('meta[name="return-control"]');
    if (meta && meta.getAttribute('content') === 'off') return false;
    if (document.body && document.body.getAttribute('data-return-control') === 'off') return false;
    if (document.getElementById(BUTTON_ID)) return false;
    return true;
  }

  function inject() {
    if (!shouldInject()) return;
    var a = document.createElement('a');
    a.id = BUTTON_ID;
    a.href = resolveReturnTarget();
    a.textContent = LABEL;
    a.style.cssText = [
      'position:fixed',
      'top:16px',
      'left:16px',
      'z-index:9999',
      'padding:8px 12px',
      'background:#111',
      'color:#fff',
      'border-radius:6px',
      'text-decoration:none',
      'font-size:14px',
      'font-family:sans-serif'
    ].join(';');
    document.body.appendChild(a);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();