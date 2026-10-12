// Keeps the two language flags in the navbar pointed at the translated
// version of whatever page is currently open, instead of always the home
// page. Runs on every page (see _quarto.yml include-after-body).
(function () {
  var PAGES = [
    { en: "index.html", fr: "fr/index.html" },
    { en: "research.html", fr: "fr/recherche.html" },
    { en: "publications.html", fr: "fr/publications.html" },
    { en: "talks.html", fr: "fr/exposes.html" },
    { en: "teaching.html", fr: "fr/enseignement.html" },
    { en: "cv.html", fr: "fr/cv.html" },
  ];

  function currentPage() {
    var path = window.location.pathname;
    if (path === "/" || path === "" || /\/fr\/?$/.test(path)) {
      return PAGES[0];
    }
    for (var i = 0; i < PAGES.length; i++) {
      if (path.indexOf(PAGES[i].en) !== -1 || path.indexOf(PAGES[i].fr) !== -1) {
        return PAGES[i];
      }
    }
    return PAGES[0];
  }

  function isFrench() {
    return /\/fr\//.test(window.location.pathname) || /\/fr\/?$/.test(window.location.pathname);
  }

  document.addEventListener("DOMContentLoaded", function () {
    var page = currentPage();
    var here = isFrench();
    var enImg = document.querySelector('img[src*="flag-us"]');
    var frImg = document.querySelector('img[src*="flag-fr"]');
    var enLink = enImg && enImg.closest("a");
    var frLink = frImg && frImg.closest("a");
    if (!enLink || !frLink) return;

    // Paths relative to the current page, matching how Quarto renders
    // every other link on the site -- never root-absolute, since that
    // breaks whenever the site isn't served from the exact domain root.
    enLink.setAttribute("href", here ? "../" + page.en : page.en);
    frLink.setAttribute("href", here ? page.fr.replace(/^fr\//, "") : page.fr);

    var activeLink = here ? frLink : enLink;
    activeLink.classList.add("lang-active");
    activeLink.addEventListener("click", function (e) {
      e.preventDefault();
    });
  });
})();
